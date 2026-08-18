from types import SimpleNamespace
from unittest.mock import patch

from django import forms
from django.core import mail
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
from django.utils.safestring import mark_safe
from django_altcha import AltchaField

from cms_theme.form_actions import SendConfirmationEmailAction, _email_context
from cms_theme.models import FormEmailQuota


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="django CMS <noreply@django-cms.org>",
    DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_IP_LIMIT=10,
    DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_IP_WINDOW=3600,
    DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_RECIPIENT_LIMIT=3,
    DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_RECIPIENT_WINDOW=86400,
)
class SendConfirmationEmailActionTests(TestCase):
    def setUp(self):
        self.action = SendConfirmationEmailAction()
        self.request_factory = RequestFactory()

    def form(self, email="person@example.com", **parameters):
        options = {
            "confirmationemail_template": "default",
            **parameters,
        }
        return SimpleNamespace(
            fields={
                "email": forms.EmailField(),
                "captcha_field": AltchaField(),
            },
            cleaned_data={
                "email": email,
                "message": "Attacker-controlled content must not reach the email",
            },
            Meta=SimpleNamespace(
                options={
                    "form_name": "contact",
                    "form_parameters": options,
                }
            ),
        )

    def request(self, address="192.0.2.1"):
        return self.request_factory.post("/", REMOTE_ADDR=address)

    def test_sends_selected_server_owned_template(self):
        result = self.action.execute(self.form(), self.request())

        self.assertEqual(result, 1)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["person@example.com"])
        expected_subject = render_to_string(
            "cms_theme/form_emails/default/subject.txt"
        ).strip()
        self.assertEqual(message.subject, expected_subject)
        self.assertNotIn("Attacker-controlled", message.body)
        self.assertEqual(message.extra_headers["Auto-Submitted"], "auto-generated")
        self.assertEqual(len(message.alternatives), 1)

    def test_adds_sanitized_form_fields_to_template_context(self):
        form = self.form()
        form.fields["topics"] = forms.MultipleChoiceField(
            label="Topics",
            choices=(("security", "Security"), ("email", "Email")),
        )
        form.cleaned_data["topics"] = ["security", "email"]
        contexts = []

        def render(template_name, context):
            contexts.append(context)
            if template_name.endswith("subject.txt"):
                return "Subject"
            if template_name.endswith("body.html"):
                return "<p>Body</p>"
            return "Body"

        with patch("cms_theme.form_actions.render_to_string", side_effect=render):
            result = self.action.execute(form, self.request())

        self.assertEqual(result, 1)
        self.assertEqual(len(contexts), 3)
        context = contexts[0]
        self.assertEqual(context["form_name"], "contact")
        self.assertEqual(context["form_fields"]["email"], "person@example.com")
        self.assertEqual(context["form_fields"]["topics"], ("security", "email"))
        self.assertNotIn("captcha_field", context["form_fields"])
        self.assertIn(
            {"name": "topics", "label": "Topics", "value": ("security", "email")},
            context["form_field_rows"],
        )

    def test_template_context_removes_safe_markers_and_autoescapes_values(self):
        form = self.form()
        form.fields["message"] = forms.CharField()
        form.cleaned_data["message"] = mark_safe("<script>alert(1)</script>")

        rendered = Template("{{ form_fields.message }}").render(
            Context(_email_context(form))
        )

        self.assertEqual(rendered, "&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_requires_email_field_named_email(self):
        form = self.form()
        form.fields["email"] = forms.CharField()

        with self.assertLogs("cms_theme.form_actions", level="WARNING"):
            result = self.action.execute(form, self.request())

        self.assertEqual(result, 0)
        self.assertEqual(mail.outbox, [])

    def test_revalidates_recipient_before_sending(self):
        form = self.form(email="not-an-email")

        with self.assertLogs("cms_theme.form_actions", level="WARNING"):
            result = self.action.execute(form, self.request())

        self.assertEqual(result, 0)
        self.assertEqual(mail.outbox, [])

    def test_requires_altcha_field(self):
        form = self.form()
        form.fields.pop("captcha_field")

        with self.assertLogs("cms_theme.form_actions", level="WARNING"):
            result = self.action.execute(form, self.request())

        self.assertEqual(result, 0)
        self.assertEqual(mail.outbox, [])

    @override_settings(DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_IP_LIMIT=1)
    def test_limits_messages_per_source_address(self):
        self.assertEqual(self.action.execute(self.form(), self.request()), 1)

        with self.assertLogs("cms_theme.form_actions", level="WARNING"):
            result = self.action.execute(
                self.form(email="someone-else@example.com"), self.request()
            )

        self.assertEqual(result, 0)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(
        DJANGOCMS_FORM_BUILDER_CONFIRMATION_EMAIL_RECIPIENT_LIMIT=1
    )
    def test_limits_messages_per_recipient_across_source_addresses(self):
        self.assertEqual(self.action.execute(self.form(), self.request()), 1)

        with self.assertLogs("cms_theme.form_actions", level="WARNING"):
            result = self.action.execute(
                self.form(), self.request(address="198.51.100.2")
            )

        self.assertEqual(result, 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_quota_rows_do_not_store_email_or_ip_address(self):
        self.action.execute(self.form(), self.request())

        keys = list(FormEmailQuota.objects.values_list("key", flat=True))
        self.assertEqual(len(keys), 2)
        self.assertTrue(all(len(key) == 64 for key in keys))
        self.assertNotIn("person@example.com", "".join(keys))
        self.assertNotIn("192.0.2.1", "".join(keys))

    def test_rejects_unknown_template_set(self):
        form = self.form(confirmationemail_template="../../unexpected")

        with self.assertLogs("cms_theme.form_actions", level="ERROR"):
            result = self.action.execute(form, self.request())

        self.assertEqual(result, 0)
        self.assertEqual(mail.outbox, [])
