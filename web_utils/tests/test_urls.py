import django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

if django.get_version() < '4.0':
    from django.middleware.csrf import _get_new_csrf_token as _get_new_csrf_string
else:
    from django.middleware.csrf import _get_new_csrf_string

from web_utils.urls import decorated_patterns
from web_utils.tests import url_conf


@override_settings(ROOT_URLCONF='web_utils.tests.url_conf')
class DecoratedPatternsTests(TestCase):

    def setUp(self):
        test_patterns = decorated_patterns(login_required, url_conf.urlpatterns)
        test_patterns += decorated_patterns((login_required, csrf_exempt), url_conf.more_patterns)
        url_conf.urlpatterns = test_patterns
        self.client = Client(enforce_csrf_checks=True)

    def assertWasRedirected(self, url, response, status_code=302):
        """
        A quick way to assertRedirects without following the next link.
        """
        self.assertEqual(status_code, response.status_code)
        self.assertEqual("{}".format(url), response['Location'])

    def _get_login_url(self, destination):
        return settings.LOGIN_URL + '?next={0}'.format(destination)

    def _create_user(self, username="test", password="pswd"):
        user = User(username=username, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()
        return user

    def _get_csrf_token(self):
        token = _get_new_csrf_string()
        self.client.cookies[settings.CSRF_COOKIE_NAME] = token
        return token

    def test_decorated_patterns_applies_decorator_to_views(self):
        destination = reverse("test_one")
        expected_url = self._get_login_url(destination)

        response = self.client.get(destination)
        self.assertWasRedirected(expected_url, response)

    def test_decorated_patterns_applies_decorators_recursively_through_multiple_includes(self):
        destination = reverse("testing:test_two")
        expected_url = self._get_login_url(destination)

        response = self.client.get(destination)
        self.assertWasRedirected(expected_url, response)

    def test_hits_end_page_when_login_decorator_passes(self):
        destination = reverse("test_one")
        user = self._create_user(password="pswd")
        self.client.login(username=user.username, password="pswd")

        response = self.client.get(destination)
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"Test One", response.content)

    def test_multiple_decorators_applied_to_views(self):
        # applied login middleware when csrf_passes
        destination = reverse("test_three")
        expected_url = self._get_login_url(destination)

        response = self.client.post(destination, {'data': 'something'})
        self.assertWasRedirected(expected_url, response)

    def test_second_decorator_hits_when_passes_first(self):
        # allows post without csrf
        destination = reverse("test_three")

        user = self._create_user(password="pswd")
        self.client.login(username=user.username, password="pswd")

        response = self.client.post(destination, {'data': 'something'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"Test Three", response.content)

    def test_make_sure_csrf_is_really_being_checked(self):
        # view test_two is not under csrf_exempt
        destination = reverse("testing:test_two")

        user = self._create_user(password="pswd")
        self.client.login(username=user.username, password="pswd")

        response = self.client.post(destination)
        self.assertEqual(403, response.status_code, response.content)
        response = self.client.post(destination, data={'csrfmiddlewaretoken': self._get_csrf_token()})
        self.assertEqual(200, response.status_code)
