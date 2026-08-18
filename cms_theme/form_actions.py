import hashlib
import hmac
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import BoundedSemaphore, Lock

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import F
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django_altcha import AltchaField
from djangocms_form_builder import actions
from djangocms_form_builder.helpers import get_option

from cms_theme.models import FormEmailQuota

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_SETS = (("default", _("Default confirmation")),)
TEMPLATE_SETS = getattr(
    settings,
    "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_TEMPLATE_SETS",
    DEFAULT_TEMPLATE_SETS,
)
if not TEMPLATE_SETS or any(
    not isinstance(key, str) or not re.fullmatch(r"[-\w]+", key)
    for key, _label in TEMPLATE_SETS
):
    raise ImproperlyConfigured(
        "Confirmation email template keys must be non-empty slugs"
    )
TEMPLATE_KEYS = frozenset(key for key, _label in TEMPLATE_SETS)
MAX_CONTEXT_VALUE_LENGTH = 2000
_email_executor = None
_email_executor_lock = Lock()


def _positive_setting(name, default):
    value = int(getattr(settings, name, default))
    if value < 1:
        raise ImproperlyConfigured(f"{name} must be a positive integer")
    return value


class _BoundedEmailExecutor:
    """A process-local executor with a hard cap on outstanding messages."""

    def __init__(self, max_workers, max_pending):
        self._slots = BoundedSemaphore(max_pending)
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="form-confirmation-email",
        )

    def submit(self, message):
        if not self._slots.acquire(blocking=False):
            return False
        try:
            self._executor.submit(self._send, message)
        except Exception:
            self._slots.release()
            raise
        return True

    def _send(self, message):
        try:
            message.send(fail_silently=False)
        except Exception:
            logger.exception("Failed to send form confirmation email")
        finally:
            self._slots.release()

    def shutdown(self, wait=True):
        self._executor.shutdown(wait=wait)


def _get_email_executor():
    # Create it after the first request, rather than at import time before a
    # WSGI server may fork worker processes.
    global _email_executor
    if _email_executor is None:
        with _email_executor_lock:
            if _email_executor is None:
                _email_executor = _BoundedEmailExecutor(
                    max_workers=_positive_setting(
                        "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_WORKERS", 2
                    ),
                    max_pending=_positive_setting(
                        "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_MAX_PENDING", 10
                    ),
                )
    return _email_executor


def _dispatch_email(message):
    try:
        return _get_email_executor().submit(message)
    except Exception:
        logger.exception("Failed to enqueue form confirmation email")
        return False


def _quota_key(kind, value, window, now):
    """Return a non-reversible, fixed-window quota key without storing PII."""
    bucket = int(now.timestamp()) // window
    message = force_bytes(f"form-confirmation-email:{kind}:{bucket}:{value}")
    return hmac.new(
        force_bytes(settings.SECRET_KEY), message, hashlib.sha256
    ).hexdigest()


def _consume_quota(kind, value, limit, window, now):
    key = _quota_key(kind, value, window, now)
    next_window = (int(now.timestamp()) // window + 1) * window
    expires_at = datetime.fromtimestamp(next_window, tz=UTC) + timedelta(seconds=1)

    updated = FormEmailQuota.objects.filter(pk=key, count__lt=limit).update(
        count=F("count") + 1
    )
    if updated:
        return True

    try:
        # The savepoint keeps a concurrent insert from breaking an outer
        # transaction, including Django's TestCase transaction.
        with transaction.atomic():
            FormEmailQuota.objects.create(
                key=key,
                count=1,
                expires_at=expires_at,
            )
        return True
    except IntegrityError:
        # Another request created the bucket between UPDATE and INSERT.
        return bool(
            FormEmailQuota.objects.filter(pk=key, count__lt=limit).update(
                count=F("count") + 1
            )
        )


def _template_name(template_set, filename):
    if template_set not in TEMPLATE_KEYS:
        raise TemplateDoesNotExist(template_set)
    return f"cms_theme/form_emails/{template_set}/{filename}"


def _plain_context_value(value):
    """Turn submitted values into bounded text safe for template context."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return tuple(_plain_context_value(item) for item in value)
    # Encoding round-trip deliberately removes SafeString/SafeData markers so
    # even unexpectedly pre-marked input is escaped again by Django templates.
    return (
        str(value).encode("utf-8", errors="replace").decode("utf-8")
    )[:MAX_CONTEXT_VALUE_LENGTH]


def _email_context(form):
    fields = {}
    rows = []
    for name, field in form.fields.items():
        value = form.cleaned_data.get(name)
        if (
            name == "captcha_field"
            or isinstance(field, (AltchaField, forms.FileField))
            or isinstance(value, UploadedFile)
        ):
            continue
        plain_value = _plain_context_value(value)
        fields[name] = plain_value
        rows.append(
            {
                "name": name,
                "label": str(field.label or name),
                "value": plain_value,
            }
        )
    return {
        "form_name": get_option(form, "form_name", ""),
        "form_fields": fields,
        "form_field_rows": rows,
    }


@actions.register
class SendConfirmationEmailAction(actions.FormAction):
    """Send a fixed, server-owned email template to the submitted email address."""

    class Meta:
        entangled_fields = {
            "action_parameters": ["confirmationemail_template"],
        }

    verbose_name = _("Send confirmation email to submitter")

    confirmationemail_template = forms.ChoiceField(
        label=_("Confirmation email template"),
        required=True,
        initial=TEMPLATE_SETS[0][0],
        choices=TEMPLATE_SETS,
    )

    def execute(self, form, request):
        email_field = form.fields.get("email")
        recipient = form.cleaned_data.get("email")

        # Requiring the form-builder email and CAPTCHA field types avoids
        # accidentally turning same-named free-text fields into a mail relay.
        if not isinstance(email_field, forms.EmailField) or not recipient:
            logger.warning(
                "Confirmation email skipped: form %s has no valid EmailField named email",
                get_option(form, "form_name", ""),
            )
            return 0
        try:
            validate_email(recipient)
        except ValidationError:
            logger.warning("Confirmation email skipped: invalid recipient")
            return 0
        if not isinstance(form.fields.get("captcha_field"), AltchaField):
            logger.warning(
                "Confirmation email skipped: form %s does not use Altcha",
                get_option(form, "form_name", ""),
            )
            return 0

        source = request.META.get(
            getattr(
                settings,
                "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_IP_META_KEY",
                "REMOTE_ADDR",
            ),
            "",
        )
        if not source:
            logger.warning("Confirmation email skipped: client address is unavailable")
            return 0

        now = datetime.now(tz=UTC)
        ip_limit = _positive_setting(
            "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_IP_LIMIT", 10
        )
        ip_window = _positive_setting(
            "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_IP_WINDOW", 3600
        )
        recipient_limit = _positive_setting(
            "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_RECIPIENT_LIMIT", 3
        )
        recipient_window = _positive_setting(
            "DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_RECIPIENT_WINDOW", 86400
        )

        try:
            FormEmailQuota.objects.filter(expires_at__lt=now).delete()
            source_allowed = _consume_quota(
                "source", source, ip_limit, ip_window, now
            )
            recipient_allowed = source_allowed and _consume_quota(
                "recipient",
                recipient.casefold(),
                recipient_limit,
                recipient_window,
                now,
            )
        except Exception:
            # Failing closed is important: a database incident must not silently
            # disable the mail-abuse controls.
            logger.exception("Confirmation email skipped: quota check failed")
            return 0

        if not recipient_allowed:
            logger.warning("Confirmation email skipped: rate limit reached")
            return 0

        template_set = self.get_parameter(form, "confirmationemail_template")
        if template_set not in TEMPLATE_KEYS:
            logger.error("Confirmation email skipped: unknown template set")
            return 0

        context = _email_context(form)
        try:
            subject = render_to_string(
                _template_name(template_set, "subject.txt"), context
            )
            text_message = render_to_string(
                _template_name(template_set, "body.txt"), context
            )
            try:
                html_message = render_to_string(
                    _template_name(template_set, "body.html"), context
                )
            except TemplateDoesNotExist:
                html_message = None
        except TemplateDoesNotExist:
            logger.exception(
                "Confirmation email skipped: template set %s is incomplete",
                template_set,
            )
            return 0

        # Templates are server-owned and HTML auto-escaping remains enabled. Do not
        # use the `safe` filter for submitted values in these templates.
        subject = " ".join(subject.splitlines()).strip()
        if not text_message and html_message:
            text_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            headers={
                "Auto-Submitted": "auto-generated",
                "X-Auto-Response-Suppress": "All",
            },
        )
        if html_message:
            message.attach_alternative(html_message, "text/html")

        if not _dispatch_email(message):
            logger.warning("Confirmation email skipped: delivery queue is full")
            return 0
        return 1
