from django import forms
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin


class BackgroundGridMixin:
    """Render-side companion to :class:`~djangocms_frontend.common.BackgroundMixin`.

    Places the ``background_grid`` toggle inside the existing *Background*
    fieldset so the option is grouped consistently with the other background
    settings.  Use together with the ``Background`` mixin and after it, e.g.
    ``mixins = ["Background", "cms_theme.BackgroundGrid", "Spacing"]``.
    """

    def get_fieldsets(self, request, obj=None):
        # Imported lazily: djangocms_frontend.helpers pulls in cms.plugin_base,
        # which must not be imported while the app registry is still populating.
        from djangocms_frontend.helpers import insert_fields

        fieldsets = super().get_fieldsets(request, obj)
        for index, (name, _opts) in enumerate(fieldsets):
            if name == _("Background"):
                return insert_fields(fieldsets, ("background_grid",), block=index, position=-1)
        # No Background fieldset present – fall back to a dedicated block.
        return insert_fields(
            fieldsets,
            ("background_grid",),
            block=None,
            position=-1,
            blockname=_("Background"),
        )


class BackgroundGridFormMixin(EntangledModelFormMixin):
    """Form-side companion adding the ``background_grid`` field to ``config``."""

    class Meta:
        entangled_fields = {"config": ["background_grid"]}

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )
