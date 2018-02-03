from django import test

from web_utils.middleware import SSLMiddleware


@test.override_settings(SSL_ENABLED=True)
class SSLMiddlewareTests(test.TestCase):

    def _get_request(self, path='/', secure=False):
        return test.RequestFactory().get(path, secure=secure)

    @test.override_settings(SSL_ENABLED=False)
    def test_returns_none_when_ssl_not_enabled(self):
        request = self._get_request()
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': True})
        self.assertEqual(None, result)

    def test_returns_none_when_should_be_secure_and_is(self):
        request = self._get_request(secure=True)
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': True})
        self.assertEqual(None, result)

    def test_returns_redirect_when_should_be_secure_and_is_not(self):
        request = self._get_request(secure=False)
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': True})
        self.assertEqual(301, result.status_code)
        self.assertEqual('https://{0}/'.format(request.get_host()), result['Location'])

    def test_returns_none_when_should_not_be_secure_and_is_not(self):
        request = self._get_request(secure=False)
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': False})
        self.assertEqual(None, result)

    def test_returns_redirect_when_should_not_be_secure_but_is(self):
        request = self._get_request(secure=True)
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': False})
        self.assertEqual(301, result.status_code)
        self.assertEqual('http://{0}/'.format(request.get_host()), result['Location'])

    @test.override_settings(USE_SSL_DEFAULT=True)
    def test_uses_ssl_by_default_when_settings_requests_and_not_specified_in_view_kwargs(self):
        request = self._get_request(secure=False)
        result = SSLMiddleware().process_view(request, None, None, {})
        self.assertEqual(301, result.status_code)
        self.assertEqual('https://{0}/'.format(request.get_host()), result['Location'])

    @test.override_settings(USE_SSL_DEFAULT=True)
    def test_view_kwarg_trumps_settings_when_use_ssl_default_is_on(self):
        request = self._get_request(secure=False)
        result = SSLMiddleware().process_view(request, None, None, {'USE_SSL': False})
        self.assertEqual(None, result)
