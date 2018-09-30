try:
    from urllib2 import urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, HTTPError
    from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse

GOOGLE_SITEMAP_URL = 'http://www.google.com/webmasters/tools/ping'


def ping_google_sitemap(sender, **kwargs):
    """
    Ping Google to let them know of updated content.
    """
    # SITEMAP_FAIL = "Couldn't automatically update Google Sitemap. Please do it manually in webmaster tools."

    if getattr(settings, 'PING_GOOGLE_SITEMAP', False):
        data = urlencode({
            'sitemap': settings.SITE_DOMAIN + reverse("sitemap"),
        })
        url = GOOGLE_SITEMAP_URL + '?' + data
        try:
            response = urlopen(url)
            if response.code / 100 == 2:
                # todo: should we log it or message the user somehow?
                pass

        except HTTPError:
            # todo: should we log it or message the user somehow?
            pass
