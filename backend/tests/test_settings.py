import os
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from backend.settings import _env_bool, _env_int


class EnvironmentSettingTests(SimpleTestCase):
    def test_env_bool_accepts_common_boolean_values(self):
        expected_values = {
            "1": True,
            "true": True,
            "YES": True,
            "on": True,
            "0": False,
            "false": False,
            "NO": False,
            "off": False,
        }

        for value, expected in expected_values.items():
            with self.subTest(value=value), patch.dict(
                os.environ, {"TEST_EMAIL_BOOLEAN": value}
            ):
                self.assertIs(_env_bool("TEST_EMAIL_BOOLEAN"), expected)

    def test_env_bool_rejects_invalid_value(self):
        with patch.dict(os.environ, {"TEST_EMAIL_BOOLEAN": "invalid"}):
            with self.assertRaisesMessage(
                ImproperlyConfigured, "TEST_EMAIL_BOOLEAN must be one of"
            ):
                _env_bool("TEST_EMAIL_BOOLEAN")

    def test_env_int_parses_integer(self):
        with patch.dict(os.environ, {"TEST_EMAIL_INTEGER": "587"}):
            self.assertEqual(_env_int("TEST_EMAIL_INTEGER", 25), 587)

    def test_env_int_rejects_invalid_value(self):
        with patch.dict(os.environ, {"TEST_EMAIL_INTEGER": "smtp"}):
            with self.assertRaisesMessage(
                ImproperlyConfigured, "TEST_EMAIL_INTEGER must be an integer"
            ):
                _env_int("TEST_EMAIL_INTEGER", 25)
