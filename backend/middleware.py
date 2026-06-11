from django.contrib.redirects.middleware import RedirectFallbackMiddleware
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect


class PathOnlyRedirectFallbackMiddleware(RedirectFallbackMiddleware):
    """Redirect fallback that matches on the request path, ignoring the query string.

    Django's stock :class:`RedirectFallbackMiddleware` looks up ``old_path``
    using ``request.get_full_path()``, so a stored redirect for ``/en/faq/``
    never matches an incoming ``/en/faq/?utm_source=x``. We match on
    ``request.path`` only, and forward the original query string onto the
    redirect target so UTM/analytics params survive the hop.

    Redirects are issued as temporary (302) rather than the stock permanent
    (301), so targets can be refined later without browsers having cached a
    permanent redirect to ``/``.
    """

    response_redirect_class = HttpResponseRedirect

    def process_response(self, request, response):
        # No need to look for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        path = request.path
        current_site = get_current_site(request)

        r = None
        try:
            r = Redirect.objects.get(site=current_site, old_path=path)
        except Redirect.DoesNotExist:
            pass
        if r is None and not path.endswith("/"):
            try:
                r = Redirect.objects.get(site=current_site, old_path=path + "/")
            except Redirect.DoesNotExist:
                pass

        if r is not None:
            if r.new_path == "":
                return self.response_gone_class()
            new_path = r.new_path
            # Forward the original query string (e.g. UTM params) to the target
            # so analytics attribution survives the redirect.
            query_string = request.META.get("QUERY_STRING", "")
            if query_string:
                separator = "&" if "?" in new_path else "?"
                new_path = f"{new_path}{separator}{query_string}"
            return self.response_redirect_class(new_path)

        return response
