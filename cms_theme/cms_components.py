from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.icon.fields import IconPickerField
from djangocms_frontend.contrib.image.fields import ImageFormField
from djangocms_frontend.fields import ColoredButtonGroup, HTMLFormField


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
            ("end", _("End")),
        ],
        initial="center",
        help_text=_("Controls horizontal alignment of all content"),
    )


@components.register
class LogoCarousel(CMSFrontendComponent):
    """LogoCarousel component"""

    class Meta:
        name = _("Logo Carousel")
        render_template = "carousel/logo_carousel.html"
        allow_children = True
        child_classes = [
            "HeadingPlugin",
            "CarouselItemPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Color for the carousel button."),
    )


@components.register
class BenefitsPanel(CMSFrontendComponent):
    """Benefits panel component"""

    class Meta:
        name = _("Benefits Panel")
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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
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
    )

    eyebrow_text_color = forms.ChoiceField(
        label=_("Eyebrow text color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Eyebrow text color."),
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
        child_classes = [
            "ImagePlugin",
            "TextPlugin",
            "HeadingPlugin",
            "TextLinkPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    image_accent = forms.BooleanField(
        label=_("Image accent"),
        required=False,
        initial=False,
        help_text=_("Add image accent"),
    )

    image_accent_color = forms.ChoiceField(
        label=_("Image accent color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        help_text=_("Image accent color."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    role = forms.CharField(
        label=_("Role"),
        required=False,
        help_text=_("Role displayed in people card."),
    )

    description = HTMLFormField(
        label=_("Description"),
        required=False,
        help_text=_("Description displayed in people card."),
    )

    text_color = forms.ChoiceField(
        label=_("Text Color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="dark",
        help_text=_("Card content text color."),
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
            "HeadingPlugin",
            "PlanCardPlugin",
            "HorizontalPlanCardPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
        help_text=_("Eyebrow text"),
    )

    eyebrow_text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Color for eyebrow text."),
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
            "SpacingPlugin",
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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
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
            "SpacingPlugin",
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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
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
        render_template = "quote_panel/quote_panel.html"
        allow_children = True
        child_classes = [
            "HeadingPlugin",
            "QuotePanelItemPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="dark",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Text color for quote item."),
    )
