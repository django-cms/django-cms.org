from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from djangocms_frontend import settings as frontend_settings
from djangocms_frontend.component_base import CMSFrontendComponent, Slot
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.icon.fields import IconPickerField
from djangocms_frontend.contrib.image.fields import ImageFormField

from .fields import ColorChoiceField
from djangocms_frontend.fields import (
    ButtonGroup,
    ColoredButtonGroup,
    HTMLFormField,
    IconGroup,
)
from djangocms_frontend.helpers import first_choice


def _hero_clip_path_choices():
    """Return (id, label) pairs for the Hero clip_path ChoiceField."""
    clip_paths = getattr(settings, "CMS_HERO_CLIP_PATHS", [("none", _("None"), None)])
    return [(cp[0], cp[1]) for cp in clip_paths]


@components.register
class Hero(CMSFrontendComponent):
    """Hero component with background grid option"""

    class Meta:
        name = _("Hero")
        render_template = "hero/hero.html"
        allow_children = True
        child_classes = []
        slots = (
            Slot("links", _("Links"), child_classes=["TextLinkPlugin"]),
            Slot(
                "satellites",
                _("Satellite Images or Counters"),
                child_classes=["ImagePlugin", "CounterPlugin"],
            ),
        )
        mixins = ["Background", "Spacing", "Attributes"]
        frontend_editable_fields = ("heading", "overline", "body")

    heading = forms.CharField(
        label=_("Heading"),
        required=True,
        initial="",
    )
    overline = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
        initial="",
    )
    body = HTMLFormField(
        label=_("Body"),
        required=False,
    )
    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )
    main_image = ImageFormField(
        label=_("Main image"),
        required=False,
        help_text=_(
            "Primary image for the hero section, typically displayed on the right side. Add satellite images as child plugins."
        ),
    )
    main_image_url = forms.URLField(
        label=_("Image URL override"),
        required=False,
        help_text=_("If provided, this URL is used instead of the selected image."),
    )
    clip_path = forms.ChoiceField(
        label=_("Clip path"),
        choices=_hero_clip_path_choices,
        required=False,
        initial="none",
        help_text=_("Optional SVG clip path applied to the hero image."),
    )

    def get_short_description(self):
        return self.heading if self.config.get("heading") else ""


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
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        help_text=_("Color of the vertical timeline line."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    circle_color = forms.ChoiceField(
        label=_("Circle color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
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
        mixins = ["Background", "Spacing", "Attributes"]
        frontend_editable_fields = ("left_label", "middle_label", "right_label")
        slots = (
            Slot("left", _("Links left column"), child_classes=["TextLinkPlugin"]),
            Slot("middle", _("Links middle column"), child_classes=["TextLinkPlugin"]),
            Slot("right", _("Links right column"), child_classes=["TextLinkPlugin"]),
            Slot(
                "bottom",
                _("Bottom links"),
                child_classes=["TextLinkPlugin", "TextPlugin"],
            ),
        )
        child_classes = []  # Only slots, no direct children allowed
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        ("left_label", "middle_label", "right_label"),
                        "divider_color",
                    )
                },
            ),
        )

    left_label = forms.CharField(
        label=_("Left column heading"),
        required=True,
        initial=_("Community"),
    )

    middle_label = forms.CharField(
        label=_("Middle column heading"),
        required=True,
        initial=_("Developer"),
    )

    right_label = forms.CharField(
        label=_("Right column heading"),
        required=True,
        initial=_("Follow us"),
    )

    divider_color = forms.ChoiceField(
        label=_("Divider line color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="white",
        help_text=_("Color of the horizontal divider line."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )


@components.register
class LinksListContainer(CMSFrontendComponent):
    """Footer Links List component"""

    class Meta:
        name = _("Links List Container")
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
        module = _("Sections")
        render_template = "cta/cta_panel.html"
        allow_children = True
        child_classes = [
            "TextLinkPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]
        frontend_editable_fields = ("main_heading", "eyebrow_text")

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )

    main_heading = HTMLFormField(
        label=_("Main heading"),
        required=False,
    )

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )

    content_alignment = forms.ChoiceField(
        label=_("Content alignment"),
        choices=[
            ("start", _("Start")),
            ("center", _("Center (Default)")),
            ("end", _("End")),
        ],
        initial="center",
        help_text=_("Controls horizontal alignment of all content"),
    )


@components.register
class LogoCarousel(CMSFrontendComponent):
    """LogoCarousel component"""

    class Meta:
        name = _("Carousel")
        render_template = "carousel/logo_carousel.html"
        allow_children = True
        child_classes = ["CarouselItemPlugin"]
        mixins = ["Background", "Spacing", "Attributes"]
        frontend_editable_fields = ("heading",)
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        "heading",
                        "text_color",
                        "bg_color",
                    )
                },
            ),
            (
                _("Settings"),
                {
                    "fields": (
                        "loop",
                        "space_between_slides",
                        "autoplay",
                        "delay",
                        "btn_color",
                    ),
                    "classes": ("collapse",),
                },
            ),
        )

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE[0][0],
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        required=False,
    )

    bg_color = forms.ChoiceField(
        label=_("Background color"),
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE[0][0],
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        required=False,
    )

    loop = forms.BooleanField(
        label=_("Loop Carousel"),
        required=False,
        initial=False,
        help_text=_(
            "Turn on to make the slides loop continuously from the last slide back to the first."
        ),
    )

    space_between_slides = forms.IntegerField(
        label=_("Space Between Slides"),
        required=False,
        initial=20,
        validators=[MinValueValidator(0)],
        help_text=_("Set the space (in pixels) between each slide in the carousel."),
    )

    autoplay = forms.BooleanField(
        label=_("AutoPlay"),
        required=False,
        initial=True,
        help_text=_(
            "Turn on to make the slides move automatically without manual navigation."
        ),
    )

    delay = forms.IntegerField(
        label=_("Autoplay delay"),
        required=False,
        initial=3000,
        validators=[MinValueValidator(500)],
        help_text=_(
            "Set the time (in milliseconds) each slide stays visible before moving to the next one."
        ),
    )

    btn_color = forms.ChoiceField(
        label=_("Button Color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Color for the carousel button."),
    )

    def get_short_description(self):
        return self.heading if self.config.get("heading") else ""


@components.register
class BenefitsPanel(CMSFrontendComponent):
    """Benefits panel component"""

    class Meta:
        name = _("Benefits Panel")
        module = _("Sections")
        render_template = "benefits/benefits_panel.html"
        allow_children = True
        child_classes = [
            "BenefitsCardPlugin",
            "TextPlugin",
            "HeadingPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )


@components.register
class BenefitsCard(CMSFrontendComponent):
    """Benefits card component"""

    class Meta:
        name = _("Benefits Card")
        render_template = "benefits/benefits_card.html"
        allow_children = True
        parent_classes = ["BenefitsPanelPlugin"]
        child_classes = [
            "TextLinkPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    card_title = forms.CharField(
        label=_("Card title"),
        required=False,
    )

    card_content = HTMLFormField(
        label=_("Card content"),
        required=False,
    )

    card_icon = IconPickerField(
        label=_("Icon"),
        required=False,
    )


@components.register
class Navbar(CMSFrontendComponent):
    """Navbar component with background grid option"""

    class Meta:
        name = _("Navbar")
        render_template = "navbar/navbar.html"
        allow_children = True
        child_classes = [
            "TextLinkPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    image = ImageFormField(
        label=_("Logo Image"),
        required=False,
    )


@components.register
class RelatedPeople(CMSFrontendComponent):
    """Related People component"""

    class Meta:
        name = _("Related People")
        module = _("Sections")
        render_template = "related_people/related_people.html"
        allow_children = True
        child_classes = ["PeopleCardPlugin"]
        mixins = ["Background", "Spacing", "Attributes"]

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )

    text_color = forms.ChoiceField(
        label=_("Heading text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
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
class PeopleCard(CMSFrontendComponent):
    """People card component"""

    class Meta:
        name = _("People Card")
        render_template = "related_people/person_card.html"
        allow_children = True
        parent_classes = [
            "RelatedPeoplePlugin",
            "GridColumnPlugin",
        ]
        child_classes = ["TextLinkPlugin"]
        mixins = ["Background", "Spacing", "Attributes"]

    image = ImageFormField(
        label=_("Image"),
        required=True,
        help_text=_("Portrait of the person with white background"),
    )

    image_accent = forms.BooleanField(
        label=_("Image accent"),
        required=False,
        initial=False,
        help_text=_("Add image accent"),
    )

    image_accent_color = forms.ChoiceField(
        label=_("Image accent color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        help_text=_("Image accent color"),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    overline = forms.CharField(
        label=_("Overline"),
        required=False,
        initial="contact:",
        help_text=_("Text above the name"),
    )

    name = forms.CharField(
        label=_("Name"),
        required=True,
        help_text=_("Full name"),
    )

    role = forms.CharField(
        label=_("Role"),
        required=False,
        help_text=_("Role displayed in people card"),
    )

    description = HTMLFormField(
        label=_("Description"),
        required=False,
        help_text=_("Description displayed in people card"),
    )

    text_color = forms.ChoiceField(
        label=_("Text Color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="dark",
        help_text=_("Card content text color"),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )


@components.register
class MembershipPlans(CMSFrontendComponent):
    """Membership component"""

    class Meta:
        name = _("Membership Plans")
        render_template = "membership/membership_plans.html"
        allow_children = True
        child_classes = [
            "PlanCardPlugin",
            "HorizontalPlanCardPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
        help_text=_("Eyebrow text"),
    )

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Color for eyebrow and heading text"),
    )


@components.register
class PlanCard(CMSFrontendComponent):
    """Membership plan card component"""

    class Meta:
        name = _("Plan Card")
        render_template = "membership/cards/plan_card.html"
        allow_children = True
        child_classes = [
            "TextPlugin",
            "FeatureItemPlugin",
            "TextLinkPlugin",
        ]
        parent_classes = [
            "MembershipPlansPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    card_heading = forms.CharField(
        label=_("Card heading"),
        required=False,
        help_text=_("Card heading"),
    )

    card_sub_heading = forms.CharField(
        label=_("Card sub heading"),
        required=False,
        help_text=_("Card sub heading"),
    )

    tier_color = forms.ChoiceField(
        label=_("Tier Color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Tier style / Color."),
    )


@components.register
class FeatureItem(CMSFrontendComponent):
    """Feature item component to render icon and text"""

    class Meta:
        name = _("Feature Item")
        render_template = "membership/groups/feature_item.html"
        allow_children = True
        child_classes = [
            "IconPlugin",
            "TextPlugin",
        ]
        parent_classes = [
            "PlanCardPlugin",
        ]


@components.register
class HorizontalPlanCard(CMSFrontendComponent):
    """Membership Horizontal plan card component"""

    class Meta:
        name = _("Horizontal Plan Card")
        render_template = "membership/cards/horizontal_plan_card.html"
        allow_children = True
        child_classes = [
            "TextPlugin",
            "FeatureItemPlugin",
            "TextLinkPlugin",
            "ImagePlugin",
        ]
        parent_classes = [
            "MembershipPlansPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    card_heading = forms.CharField(
        label=_("Card heading"),
        required=True,
        help_text=_("Card heading"),
    )

    card_sub_heading = forms.CharField(
        label=_("Card sub heading"),
        required=False,
        help_text=_("Card sub heading"),
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )


@components.register
class ContentTeaser(CMSFrontendComponent):
    """Content Teaser component"""

    class Meta:
        name = _("Content Teaser")
        render_template = "content_teaser/content_teaser.html"
        allow_children = True
        child_classes = [
            "TeaserContentPlugin",
            "TeaserMediaPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]


@components.register
class TeaserContent(CMSFrontendComponent):
    """Teaser Content component to render text"""

    class Meta:
        name = _("Teaser Content")
        render_template = "content_teaser/components/content.html"
        allow_children = True
        parent_classes = [
            "ContentTeaserPlugin",
        ]
        child_classes = [
            "TextPlugin",
            "HeadingPlugin",
            "SpacingPlugin",
            "TextLinkPlugin",
        ]

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )


@components.register
class TeaserMedia(CMSFrontendComponent):
    """Media Teaser component"""

    class Meta:
        name = _("Teaser Media")
        render_template = "content_teaser/components/media.html"
        allow_children = True
        parent_classes = [
            "ContentTeaserPlugin",
        ]
        child_classes = [
            "ImagePlugin",
            "VideoPlayerPlugin",
        ]


@components.register
class QuotePanelContainer(CMSFrontendComponent):
    """Quote Panel component with background grid option"""

    class Meta:
        name = _("Quote Panel")
        module = _("Sections")
        render_template = "quote_panel/quote_panel.html"
        allow_children = True
        child_classes = ["QuotePanelItemPlugin"]
        frontend_editable_fields = ["overline", "heading"]
        mixins = ["Background", "Spacing", "Attributes"]

    overline = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )
    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )
    heading_context = forms.ChoiceField(
        label=_("Heading context"),
        required=False,
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE,
        widget=ColoredButtonGroup(),
    )

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )


@components.register
class QuotePanelItem(CMSFrontendComponent):
    """Quote Panel Item component to render quote text and author"""

    class Meta:
        name = _("Quote Panel Item")
        render_template = "quote_panel/quote_item.html"
        allow_children = True
        parent_classes = [
            "QuotePanelContainerPlugin",
        ]
        child_classes = [
            "ImagePlugin",
        ]

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
        help_text=_("Eyebrow text for quote item."),
    )

    quote_text = HTMLFormField(
        label=_("Quote text"),
        required=False,
        help_text=_("Main quote text for quote item."),
    )

    author_name = forms.CharField(
        label=_("Author name"),
        required=False,
        help_text=_("Author name for quote item."),
    )

    author_role = forms.CharField(
        label=_("Author role"),
        required=False,
        help_text=_("Author role for quote item."),
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="dark",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Text color for quote item."),
    )


@components.register
class Heading(CMSFrontendComponent):
    """Heading component with text color option"""

    HEADINGS = (
        ("h1", _("Heading 1")),
        ("h2", _("Heading 2")),
        ("h3", _("Heading 3")),
        ("h4", _("Heading 4")),
        ("h5", _("Heading 5")),
    )

    class Meta:
        name = _("Heading")
        render_template = "heading/heading.html"
        allow_children = True
        child_classes = []
        frontend_editable_fields = ("heading", "overline")

    heading_level = forms.ChoiceField(
        label=_("Heading level"),
        choices=getattr(frontend_settings, "DJANGO_FRONTEND_HEADINGS", HEADINGS),
        required=True,
    )
    overline = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )
    heading = forms.CharField(
        label=_("Heading"),
        required=True,
    )
    heading_context = forms.ChoiceField(
        label=_("Heading context"),
        required=False,
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE,
        widget=ColoredButtonGroup(),
    )

    def get_short_description(self):
        return (
            f"{self.heading} <{self.heading_level}>"
            if self.config.get("heading")
            else ""
        )


@components.register
class Spacing(CMSFrontendComponent):
    """Spacing component to add vertical spacing between components"""

    class Meta:
        name = _("Spacing")
        render_template = "spacing/spacing.html"
        allow_children = True
        mixins = ["Attributes"]

    space_property = forms.ChoiceField(
        label=_("Property"),
        choices=frontend_settings.SPACER_PROPERTY_CHOICES,
        initial=first_choice(frontend_settings.SPACER_PROPERTY_CHOICES),
        widget=ButtonGroup(attrs=dict(property="text")),
    )
    space_sides = forms.ChoiceField(
        label=_("Sides"),
        choices=frontend_settings.SPACER_SIDE_CHOICES,
        initial=first_choice(frontend_settings.SPACER_SIDE_CHOICES),
        required=False,
        widget=ButtonGroup(attrs=dict(property="text")),
    )
    space_size = forms.ChoiceField(
        label=_("Size"),
        choices=frontend_settings.SPACER_SIZE_CHOICES + (("auto", _("Auto")),),
        initial=first_choice(frontend_settings.SPACER_SIZE_CHOICES),
        widget=ButtonGroup(attrs=dict(property="text")),
    )
    space_device = forms.ChoiceField(
        label=_("Device"),
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.DEVICE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE[0][0],
        required=False,
        widget=IconGroup(),
    )

    def clean(self):
        super().clean()
        if (
            self.cleaned_data["space_property"] == "p"
            and self.cleaned_data["space_size"] == "auto"
        ):
            raise ValidationError(
                {
                    "space_property": _(
                        "Padding does not have an auto spacing. Either switch to margin or a defined size."
                    ),
                    "space_size": _(
                        "Padding does not have an auto spacing. Either "
                        "switch to a defined size or change the spacing property."
                    ),
                }
            )


@components.register
class CodeBlock(CMSFrontendComponent):
    """Code card component to render code snippets with syntax highlighting"""
    class Media:
        js = (
            "admin/vendor/ace/ace.js"
            if "djangocms_static_ace" in settings.INSTALLED_APPS
            else "https://cdnjs.cloudflare.com/ajax/libs/ace/1.43.3/ace.js",
        )

    class Meta:
        name = _("Code Block")
        render_template = "code_block/code_block.html"
        change_form_template = "code_block/admin/code_block.html"
        allow_children = True
        child_classes = []
        mixins = ["Background", "Spacing", "Attributes"]
        frontend_editable_fields = ("heading",)

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
        help_text=_("Heading for the code block."),
    )
    dark_mode = forms.BooleanField(
        label=_("Dark mode"),
        required=False,
        initial=False,
        help_text=_("Enable dark mode for code block."),
    )
    code_content = forms.CharField(
        label=_("Code"),
        initial="",
        required=True,
        widget=forms.widgets.Textarea(attrs={"class": "js-ckeditor-use-selected-text"}),
    )


@components.register
class CounterContainer(CMSFrontendComponent):
    """Counter container component with optional heading"""

    class Meta:
        name = _("Counter Panel")
        module = _("Sections")
        render_template = "counter/counter_container.html"
        allow_children = True
        child_classes = ["CounterPlugin"]
        mixins = ["Background", "Spacing", "Attributes"]

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Color for eyebrow and heading text"),
    )


class CounterPluginMixin:
    """Plugin mixin that fetches GitHub stats for Counter components."""

    GITHUB_REPO = "django-cms/django-cms"
    GITHUB_ORG = "django-cms"
    CACHE_TIMEOUT = 86400  # 24 hours

    def _get_github_number(self, counter_type):
        import logging

        from django.core.cache import cache

        cache_key = f"counter_github_{counter_type}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        logger = logging.getLogger(__name__)
        number = 0
        try:
            number = self._fetch_github_stat(counter_type)
        except Exception:
            logger.exception("Failed to fetch GitHub stat for %s", counter_type)
        cache.set(cache_key, number, self.CACHE_TIMEOUT)
        return number

    def _fetch_github_stat(self, counter_type):
        from datetime import datetime, timedelta, timezone

        import requests

        if counter_type in ("stars", "forks"):
            resp = requests.get(
                f"https://api.github.com/repos/{self.GITHUB_REPO}",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["stargazers_count" if counter_type == "stars" else "forks_count"]

        since = (datetime.now(tz=timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

        if counter_type == "issues_closed":
            resp = requests.get(
                "https://api.github.com/search/issues",
                params={"q": f"org:{self.GITHUB_ORG} type:issue is:closed closed:>={since}"},
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["total_count"]

        if counter_type == "merges":
            resp = requests.get(
                "https://api.github.com/search/issues",
                params={"q": f"org:{self.GITHUB_ORG} type:pr is:merged merged:>={since}"},
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["total_count"]

        return 0

    def render(self, context, instance, placeholder):
        counter_type = instance.config.get("counter_type", "manual")
        if counter_type != "manual":
            instance.config["number"] = self._get_github_number(counter_type)
        return super().render(context, instance, placeholder)


COUNTER_TYPE_CHOICES = [
    ("manual", _("Manual")),
    ("stars", _("GitHub Stars")),
    ("forks", _("GitHub Forks")),
    ("issues_closed", _("GitHub Issues Closed (30 days)")),
    ("merges", _("GitHub PRs Merged (30 days)")),
]


@components.register
class Counter(CMSFrontendComponent):
    """Counter component with animated number display"""

    _plugin_mixins = [CounterPluginMixin]

    class Meta:
        name = _("Counter")
        render_template = "counter/counter.html"
        allow_children = True
        child_classes = ["TextLinkPlugin"]
        mixins = ["Background", "Attributes"]
        fieldsets = (
            (None, {
                "fields": (
                    "icon",
                    "title",
                    ("counter_type", "number", "is_percent"),
                    "number_color",
                    "description",
                    "color_style",
                )
            }),
        )

    counter_type = forms.ChoiceField(
        label=_("Counter Type"),
        choices=COUNTER_TYPE_CHOICES,
        initial="manual",
    )
    icon = IconPickerField(
        label=_("Icon"),
        required=False,
    )
    title = forms.CharField(
        label=_("Title"),
        required=False,
    )
    number = forms.IntegerField(
        label=_("Number"),
        required=False,
    )
    is_percent = forms.BooleanField(
        label=_("Is Percent"),
        required=False,
        initial=False,
    )
    number_color = ColorChoiceField(
        label=_("Number Color"),
        initial="dark",
    )
    description = HTMLFormField(
        label=_("Description"),
        required=False,
    )
    color_style = ColorChoiceField(
        label=_("Text Color"),
        initial="dark",
    )

    def get_short_description(self):
        return dict(COUNTER_TYPE_CHOICES).get(self.config.get("counter_type"), _("Manual"))
