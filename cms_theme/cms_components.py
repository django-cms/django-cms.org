from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.image.fields import ImageFormField
from djangocms_frontend.fields import HTMLFormField

from djangocms_frontend.fields import ColoredButtonGroup


@components.register
class Hero(CMSFrontendComponent):
    """Hero component with background grid option"""

    class Meta:
        name = _("Hero")
        render_template = "hero/hero.html"
        allow_children = True
        child_classes = [
            "TextPlugin",
            "TextLinkPlugin",
            "ImagePlugin",
            "HeadingPlugin",
            "CounterPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )


@components.register
class Features(CMSFrontendComponent):
    """Features section container with accordion and content area"""

    class Meta:
        plugin_name = _("Features")
        render_template = "features/features.html"
        allow_children = True
        child_classes = [
            "TextPlugin",
            "HeadingPlugin",
            "AccordionPlugin",
            "TextLinkPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )

    mirror_layout = forms.BooleanField(
        label=_("Mirror layout"),
        required=False,
        initial=False,
        help_text=_(
            "Enable to display images on the left and the accordion on the right."
        ),
    )

    accordion_header_color = forms.ChoiceField(
        label=_("Accordion header text color"),
        choices=[
            ("default", _("Default (Black)")),
            ("primary", _("Primary")),
            ("secondary", _("Secondary")),
            ("white", _("White")),
            ("muted", _("Muted")),
        ],
        required=False,
        initial="default",
    )
    

@components.register
class TimelineContainer(CMSFrontendComponent):
    """Timeline component with vertical layout option"""

    class Meta:
        name = _("Timeline")
        render_template = "timeline/timeline.html"
        allow_children = True
        child_classes = [
            "CardPlugin",
            "TextPlugin",
            "HeadingPlugin",
            "SpacingPlugin",
        ]
        mixins = [
            "Background",
            "Spacing",
            "Attributes",
        ]

    divider_color = forms.ChoiceField(
        label=_("Divider line color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        help_text=_("Color of the vertical timeline line."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    circle_color = forms.ChoiceField(
        label=_("Circle color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="secondary",
        help_text=_("Color of the timeline circles."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )


@components.register
class Footer(CMSFrontendComponent):
    """Footer component with divider color option"""

    class Meta:
        name = _("Footer")
        render_template = "footer/footer.html"
        allow_children = True
        child_classes = [
            "GridRowPlugin",
            "TextPlugin",
            "TextLinkPlugin",
            "ImagePlugin",
            "HeadingPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    divider_color = forms.ChoiceField(
        label=_("Divider line color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="white",
        help_text=_("Color of the horizontal divider line."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )


@components.register
class FooterLinksList(CMSFrontendComponent):
    """Footer Links List component"""

    class Meta:
        name = _("Footer Links List")
        render_template = "footer/footer_links_list.html"
        requires_parent = True
        parent_classes = ["Footer", "GridColumnPlugin"]
        allow_children = True
        child_classes = [
            "TextLinkPlugin",
        ]
        mixins = ["Attributes", "Spacing"]

    item_spacing = forms.ChoiceField(
        label=_("Item Spacing"),
        choices=settings.DJANGOCMS_FRONTEND_SPACER_SIZES,
        required=False,
    )

    item_alignment = forms.ChoiceField(
        label=_("Item Alignment"),
        choices=[
            ("flex-row", _("One line")),
            ("flex-column", _("Stacked")),
        ],
        required=False,
        initial="flex-column",
    )
    
    
@components.register
class CTAPanel(CMSFrontendComponent):
    """CTAPanel component with background grid option"""

    class Meta:
        name = _("CTA Panel")
        render_template = "cta/cta_panel.html"
        allow_children = True
        child_classes = [
            "TextLinkPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )

    main_heading = HTMLFormField(
        label=_("Main heading"),
        required=False,
    )

    content_alignment = forms.ChoiceField(
        label=_("Content alignment"),
        choices=[
            ("start", _("Start")),
            ("center", _("Center (Default)")),
            ("end", _("End"))
        ],
        initial="center",
        help_text=_("Controls horizontal alignment of all content")
    )

@components.register
class RelatedPeople(CMSFrontendComponent):

    """Related People component"""
    class Meta:
        name = _("Related People")
        render_template = "related_people/related_people.html"
        allow_children = True
        child_classes = [
            "HeadingPlugin",
            "PeopleCardPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
        help_text=_("Eyebrow text"),
    )

    grid_columns = forms.ChoiceField(
        label=_("Grid columns"),
        choices=[
            ("1", _("1")),
            ("2", _("2")),
            ("3", _("3")),
        ],
        initial="3",
        help_text=_("Number of grid columns."),
    )

@components.register
class CardButtonContainer(CMSFrontendComponent):
    """Card button container component"""

    class Meta:
        name = _("Card button container")
        allow_children = True
        child_classes = [
            "TextLinkPlugin",
        ]
        parent_classes = [
            "PeopleCardPlugin",
        ]


@components.register
class PeopleCard(CMSFrontendComponent):
    """People card component"""

    class Meta:
        name = _("People Card")
        render_template = "related_people/person_card.html"
        allow_children = True
        parent_classes = [
            "RelatedPeoplePlugin",
        ]
        child_classes = [
            "CardButtonContainerPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    # profile image goes here
    photo = ImageFormField(
        label=_("Photo"),
        required=True,
        help_text=_("Photo displayed in people card."),
    )

    role = forms.CharField(
        label=_("Role"),
        required=False,
        help_text=_("Role displayed in people card."),
    )

    person_name = forms.CharField(
        label=_("Person name"),
        required=False,
        help_text=_("Person name displayed in people card."),
    )

    sub_headline = forms.CharField(
        label=_("Sub headline"),
        required=False,
        help_text=_("Sub headline displayed in people card."),
    )

    description = HTMLFormField(
        label=_("Description"),
        required=False,
        help_text=_("Description displayed in people card."),
    )


