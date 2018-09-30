import mock

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus

from django import test
from django.conf import settings
from django.urls import reverse

from web_utils.web import ping_google_sitemap


class GoogleSitemapPingTests(test.TestCase):

    def setUp(self, **kwargs):
        self.settings_dict = {
            'SITE_DOMAIN': 'http://www.mydomain.com',
            'PING_GOOGLE_SITEMAP': True,
            'GOOGLE_SITEMAP_URL': 'http://www.google.com/webmasters/tools/ping',
        }
        self.original_settings = {k: getattr(settings, k, None) for k in self.settings_dict}
        [setattr(settings, k, v) for k, v in self.settings_dict.items()]

    def tearDown(self):
        [setattr(settings, k, v) for k, v in self.original_settings.items()]

    @property
    def urls(self):
        """
        Setting urls to make sure reversing sitemap url works.
        """
        from django.conf.urls import url
        from django.views.generic import TemplateView
        return [
            url(r'^sitemap.xml/$', TemplateView.as_view(), name='sitemap'),
        ]

    @mock.patch('web_utils.web.urlopen')
    def test_pings_google_sitemap_with_sitemap_location(self, urlopen):
        ping_google_sitemap(mock.Mock())

        expected_call = self.settings_dict['GOOGLE_SITEMAP_URL'] + '?sitemap=' + quote_plus(
            self.settings_dict['SITE_DOMAIN'] + reverse("sitemap")
        )
        urlopen.assert_called_once_with(expected_call)

    @mock.patch('web_utils.web.urlopen')
    def test_doesnt_pings_google_sitemap(self, urlopen):
        settings.PING_GOOGLE_SITEMAP = False
        ping_google_sitemap(mock.Mock())

        self.assertFalse(urlopen.called)
