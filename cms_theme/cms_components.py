from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.contrib.icon.fields import IconPickerField
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
class MembershipPlans(CMSFrontendComponent):
    """Membership component"""

    class Meta:
        name = _("Membership Plans")
        render_template = "membership/membership_plans.html"
        allow_children = True
        child_classes = [
            "MembershipTopSectionGroupPlugin",
            "PlanCardGroupPlugin",
            "HorizontalPlanCardPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]


@components.register
class MembershipTopSectionGroup(CMSFrontendComponent):
    """Membership top section group"""

    class Meta:
        name = _("Top Section Group")
        allow_children = True
        child_classes = [
            "HeadingPlugin",
        ]
        parent_classes = [
            "MembershipPlansPlugin",
        ]

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
class PlanCardGroup(CMSFrontendComponent):
    """Plan card group"""

    class Meta:
        name = _("Plan Card Group")
        allow_children = True
        child_classes = [
            "PlanCardPlugin",
        ]
        parent_classes = [
            "MembershipPlansPlugin",
        ]


@components.register
class PlanCard(CMSFrontendComponent):
    """Membership plan card component"""

    class Meta:
        name = _("Plan Card")
        render_template = "membership/cards/plan_card.html"
        allow_children = True
        child_classes = [
            "TextLinkPlugin",
            "TextPlugin",
        ]
        parent_classes = [
            "PlanCardGroup",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    TIER_COLOR_CHOICES = (
        ("accent-platinum", _("Platinum")),
        ("accent-gold", _("Gold")),
        ("accent-silver", _("Silver")),
        ("accent-bronze", _("Bronze")),
    )

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
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES + TIER_COLOR_CHOICES,
        required=False,
        initial="default",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        help_text=_("Tier style / Color."),
    )


@components.register
class HorizontalPlanCard(CMSFrontendComponent):
    """Membership Horizontal plan card component"""

    class Meta:
        name = _("Horizontal Plan Card")
        render_template = "membership/cards/horizontal_plan_card.html"
        allow_children = True
        child_classes = [
            "ImagePlugin",
            "GridColumnPlugin",
        ]
        parent_classes = [
            "MembershipPlansPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]
