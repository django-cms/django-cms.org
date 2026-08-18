from django.template import engines
from django.test import RequestFactory, SimpleTestCase


class AdminDeleteConfirmationContextTests(SimpleTestCase):
    template = engines["django"].from_string(
        "{% load admin_filters %}"
        "{{ deleted_objects|truncated_unordered_list:delete_confirmation_max_display }}"
    )

    def test_missing_display_limit_uses_unlimited_default(self):
        request = RequestFactory().get("/")

        rendered = self.template.render(
            {"deleted_objects": ["Snippet Ptr: Request demo", ["Plugin: 24349"]]},
            request,
        )

        self.assertIn("Snippet Ptr: Request demo", rendered)
        self.assertIn("Plugin: 24349", rendered)

    def test_explicit_display_limit_takes_precedence(self):
        request = RequestFactory().get("/")

        rendered = self.template.render(
            {
                "delete_confirmation_max_display": 1,
                "deleted_objects": ["First", "Second"],
            },
            request,
        )

        self.assertIn("First", rendered)
        self.assertNotIn(">Second<", rendered)
        self.assertIn("more object", rendered)
