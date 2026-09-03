from types import SimpleNamespace

from django.template import Context, Template
from django.test import SimpleTestCase

from cms_theme.templatetags.cms_theme_tags import (
    card_link_label,
    icon_link_label,
    image_link_label,
)


def plugin(config, **attrs):
    """A stand-in for a plugin instance: the filters only read config."""
    return SimpleNamespace(config=config, **attrs)


class IconLinkLabelTests(SimpleTestCase):
    """The footer social row is icon-only links, on every page."""

    def test_names_a_brand_icon(self):
        self.assertEqual(
            icon_link_label(plugin({"icon_left": {"iconClass": "fa-brands fa-mastodon"}})),
            "Mastodon",
        )

    def test_applies_overrides_for_names_that_title_case_badly(self):
        for icon_class, expected in (
            ("fa-brands fa-x-twitter", "X"),
            ("fa-brands fa-github", "GitHub"),
            ("fa-brands fa-linkedin-in", "LinkedIn"),
            ("bi bi-rss", "RSS"),
        ):
            with self.subTest(icon_class=icon_class):
                self.assertEqual(
                    icon_link_label(plugin({"icon_right": {"iconClass": icon_class}})),
                    expected,
                )

    def test_adds_nothing_when_the_link_already_has_a_name(self):
        named = plugin({"name": "Follow us", "icon_left": {"iconClass": "fa-brands fa-mastodon"}})
        self.assertEqual(icon_link_label(named), "")

        by_hand = plugin(
            {
                "icon_left": {"iconClass": "fa-brands fa-mastodon"},
                "attributes": {"aria-label": "Our Mastodon account"},
            }
        )
        self.assertEqual(icon_link_label(by_hand), "")

        with_children = plugin({"icon_left": {"iconClass": "fa-brands fa-mastodon"}})
        with_children.child_plugin_instances = [object()]
        self.assertEqual(icon_link_label(with_children), "")

    def test_returns_nothing_without_an_icon(self):
        self.assertEqual(icon_link_label(plugin({})), "")


class CardLinkLabelTests(SimpleTestCase):
    """A linked card is an empty <a> stretched over the whole card."""

    def test_uses_the_card_title(self):
        self.assertEqual(card_link_label(plugin({"card_title": "Become a member"})), "Become a member")

    def test_strips_markup_from_the_title(self):
        self.assertEqual(card_link_label(plugin({"card_title": "<b>Join</b> us"})), "Join us")

    def test_falls_back_to_the_opening_words_of_the_body(self):
        card = plugin(
            {
                "card_title": "",
                "card_content": "<p>Read the full case study about our migration today</p>",
            }
        )
        self.assertEqual(card_link_label(card), "Read the full case study about our migration…")

    def test_returns_nothing_when_the_card_has_no_text_at_all(self):
        self.assertEqual(card_link_label(plugin({"card_title": None, "card_content": ""})), "")

    def test_rendered_anchor_carries_and_escapes_the_label(self):
        template = Template(
            '{% load cms_theme_tags %}'
            '<a href="#" class="stretched-link"'
            '{% with a11y_label=instance|card_link_label %}'
            '{% if a11y_label %} aria-label="{{ a11y_label }}"{% endif %}{% endwith %}></a>'
        )
        rendered = template.render(Context({"instance": plugin({"card_title": 'Say "hi" & more'})}))
        self.assertEqual(
            rendered,
            '<a href="#" class="stretched-link" aria-label="Say &quot;hi&quot; &amp; more"></a>',
        )

    def test_rendered_anchor_omits_an_empty_label(self):
        template = Template(
            '{% load cms_theme_tags %}'
            '<a href="#"'
            '{% with a11y_label=instance|card_link_label %}'
            '{% if a11y_label %} aria-label="{{ a11y_label }}"{% endif %}{% endwith %}></a>'
        )
        self.assertEqual(
            template.render(Context({"instance": plugin({"card_title": ""})})),
            '<a href="#"></a>',
        )


class ImageLinkLabelTests(SimpleTestCase):
    """A link whose only content is an image is named by that image."""

    def test_prefers_the_alt_text_the_editor_set_on_the_plugin(self):
        image = SimpleNamespace(default_alt_text="filer alt", label="logo.png")
        instance = plugin({"attributes": {"alt": "Editor alt"}}, rel_image=image)
        self.assertEqual(image_link_label(instance), "Editor alt")

    def test_falls_back_to_the_filer_alt_text(self):
        image = SimpleNamespace(default_alt_text="Acme Corp logo", label="acme.png")
        self.assertEqual(image_link_label(plugin({}, rel_image=image)), "Acme Corp logo")

    def test_falls_back_to_the_filer_label_as_a_last_resort(self):
        image = SimpleNamespace(default_alt_text="", label="Acme Corp")
        self.assertEqual(image_link_label(plugin({}, rel_image=image)), "Acme Corp")

    def test_returns_nothing_without_an_image(self):
        self.assertEqual(image_link_label(plugin({}, rel_image=None)), "")
        self.assertEqual(image_link_label(plugin({})), "")
