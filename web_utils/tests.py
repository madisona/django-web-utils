
import mock
from urllib import quote_plus

from django import test
from django.conf import settings
from django.core.urlresolvers import reverse

from web_utils.formatting import format_currency
from web_utils.middleware import SSLMiddleware
from web_utils.templatetags import formatting_tags
from web_utils.web import ping_google_sitemap

__all__ = (
    'FormatCurrencyTests',
    'FormatCurrencyTemplateTagTests',
    'GoogleSitemapPingTests',
    'SSLMiddlewareTests',
)


class FormatCurrencyTests(test.TestCase):

    def test_show_empty_string_when_amount_is_zero_if_show_zero_is_false(self):
        amount = format_currency(0, show_zero=False)
        self.assertEqual("", amount)

    def test_show_formatted_zero_amount(self):
        amount = format_currency(0)
        self.assertEqual("$0.00", amount)

    def test_show_default_formatted_dollar_amount_when_amount_is_not_zero(self):
        amount = format_currency(123)
        self.assertEqual("$123.00", amount)

    def test_allow_decimal_precision_to_be_specified(self):
        amount = format_currency(123.123456, 4)
        self.assertEqual("$123.1235", amount)

    def test_add_thousand_separator(self):
        amount = format_currency(1000)
        self.assertEqual("$1,000.00", amount)

    def test_show_empty_string_when_value_is_none_and_show_zero_is_False(self):
        amount = format_currency(None, show_zero=False)
        self.assertEqual("", amount)

    def test_show_zero_when_value_is_none_and_show_zero_is_True(self):
        amount = format_currency(None)
        self.assertEqual("$0.00", amount)


class FormatCurrencyTemplateTagTests(test.TestCase):

    def test_show_empty_string_when_amount_is_zero_if_show_zero_is_false(self):
        amount = formatting_tags.format_currency(0, show_zero="False")
        self.assertEqual("", amount)

    def test_show_formatted_zero_amount(self):
        amount = formatting_tags.format_currency(0)
        self.assertEqual("$0.00", amount)

    def test_show_default_formatted_dollar_amount_when_amount_is_not_zero(self):
        amount = formatting_tags.format_currency(123)
        self.assertEqual("$123.00", amount)

    def test_allow_decimal_precision_to_be_specified(self):
        amount = formatting_tags.format_currency(123.123456, 4)
        self.assertEqual("$123.1235", amount)

    def test_add_thousand_separator(self):
        amount = formatting_tags.format_currency(1000)
        self.assertEqual("$1,000.00", amount)

    def test_show_empty_string_when_value_is_none_and_show_zero_is_False(self):
        amount = formatting_tags.format_currency(None, show_zero="False")
        self.assertEqual("", amount)

    def test_show_zero_when_value_is_none_and_show_zero_is_True(self):
        amount = formatting_tags.format_currency(None, show_zero="True")
        self.assertEqual("$0.00", amount)


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
        from django.conf.urls.defaults import patterns, url
        from django.views.generic import TemplateView
        return patterns('',
           url(r'^sitemap.xml/$', TemplateView.as_view(), name='sitemap'),
        )


    @mock.patch('urllib2.urlopen')
    def test_pings_google_sitemap_with_sitemap_location(self, urlopen):
        ping_google_sitemap(mock.Mock())

        expected_call = self.settings_dict['GOOGLE_SITEMAP_URL'] + '?sitemap=' + quote_plus(self.settings_dict['SITE_DOMAIN'] + reverse("sitemap"))
        urlopen.assert_called_once_with(expected_call)

    @mock.patch('urllib2.urlopen')
    def test_doesnt_pings_google_sitemap(self, urlopen):
        settings.PING_GOOGLE_SITEMAP = False
        ping_google_sitemap(mock.Mock())

        self.assertFalse(urlopen.called)


class SSLMiddlewareTests(test.TestCase):

    def setUp(self):
        self._original_settings = {
            'USE_SSL_DEFAULT': getattr(settings, 'USE_SSL_DEFAULT', None),
            'SSL_ENABLED': getattr(settings, 'SSL_ENABLED', None),
            }
        settings.SSL_ENABLED = True


    def tearDown(self):
        [setattr(settings, k, v) for k, v in self._original_settings.items()]

    def _get_request(self, protocol='http', path='/'):
        return test.RequestFactory(**{'wsgi.url_scheme': protocol}).get(path)

    def test_returns_none_when_ssl_not_enabled(self):
        settings.SSL_ENABLED = False

        request = self._get_request()
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': True})
        self.assertEqual(None, result)

    def test_returns_none_when_should_be_secure_and_is(self):
        request = self._get_request(protocol='https')
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': True})
        self.assertEqual(None, result)

    def test_returns_redirect_when_should_be_secure_and_is_not(self):
        request = self._get_request(protocol='http')
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': True})
        self.assertEqual(301, result.status_code)
        self.assertEqual('https://{0}/'.format(request.get_host()), result['Location'])

    def test_returns_none_when_should_not_be_secure_and_is_not(self):
        request = self._get_request(protocol='http')
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': False})
        self.assertEqual(None, result)

    def test_returns_redirect_when_should_not_be_secure_but_is(self):
        request = self._get_request(protocol='https')
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': False})
        self.assertEqual(301, result.status_code)
        self.assertEqual('http://{0}/'.format(request.get_host()), result['Location'])

    def test_uses_ssl_by_default_when_settings_requests_and_not_specified_in_view_kwargs(self):
        settings.USE_SSL_DEFAULT = True
        request = self._get_request(protocol='http')
        result = SSLMiddleware().process_view(request, None, None, {})
        self.assertEqual(301, result.status_code)
        self.assertEqual('https://{0}/'.format(request.get_host()), result['Location'])

    def test_view_kwarg_trumps_settings_when_use_ssl_default_is_on(self):
        settings.USE_SSL_DEFAULT = True
        request = self._get_request(protocol='http')
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': False})
        self.assertEqual(None, result)
