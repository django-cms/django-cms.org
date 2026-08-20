from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from backend.middleware import CanonicalHostRedirectMiddleware


def _middleware():
    return CanonicalHostRedirectMiddleware(lambda request: HttpResponse("ok"))


@override_settings(
    ALLOWED_HOSTS=["*"],
    CANONICAL_HOST="www.django-cms.org",
    CANONICAL_HOST_ALIASES=["django-cms.org", "django-cms.com"],
    SECURE_SSL_REDIRECT=True,
)
class CanonicalHostRedirectMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_alias_hosts_redirect_to_canonical_host(self):
        for host in ("django-cms.org", "django-cms.com", "DJANGO-CMS.ORG"):
            with self.subTest(host=host):
                request = self.factory.get("/en/features/", HTTP_HOST=host)

                response = _middleware()(request)

                self.assertEqual(response.status_code, 301)
                self.assertEqual(
                    response["Location"],
                    "https://www.django-cms.org/en/features/",
                )

    def test_query_string_is_preserved(self):
        request = self.factory.get(
            "/en/faq/",
            {"utm_source": "newsletter", "page": "2"},
            HTTP_HOST="django-cms.org",
        )

        response = _middleware()(request)

        self.assertEqual(
            response["Location"],
            "https://www.django-cms.org/en/faq/?utm_source=newsletter&page=2",
        )

    def test_port_is_ignored_when_matching(self):
        request = self.factory.get("/", HTTP_HOST="django-cms.org:8000")

        response = _middleware()(request)

        self.assertEqual(response["Location"], "https://www.django-cms.org/")

    def test_canonical_host_is_served_normally(self):
        for host in ("www.django-cms.org", "www.django-cms.com", "localhost"):
            with self.subTest(host=host):
                request = self.factory.get("/en/", HTTP_HOST=host)

                response = _middleware()(request)

                self.assertEqual(response.status_code, 200)

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_insecure_request_keeps_scheme_when_ssl_redirect_is_off(self):
        request = self.factory.get("/", HTTP_HOST="django-cms.com")

        response = _middleware()(request)

        self.assertEqual(response["Location"], "http://www.django-cms.org/")

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_secure_request_stays_secure(self):
        request = self.factory.get("/", HTTP_HOST="django-cms.com", secure=True)

        response = _middleware()(request)

        self.assertEqual(response["Location"], "https://www.django-cms.org/")
