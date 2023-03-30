import django
from django import http
from django.views.generic import View

if django.get_version() >= '2.0.0':
    from django.urls import re_path as url
    from django.urls import include
else:
    from django.conf.urls import url, include


class TestView(View):
    response_content = None

    def get(self, *args, **kwargs):
        return http.HttpResponse(self.response_content)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


nested_patterns = [
    url(r'^test/two/$', TestView.as_view(response_content="Test Two"), name="test_two"),
]

more_patterns = [url(r'^test/three/$', TestView.as_view(response_content="Test Three"), name="test_three")]

urlpatterns = [
    url(r'^test/one/$', TestView.as_view(response_content="Test One"), name="test_one"),
    url(r'^', include((nested_patterns, 'testing'), namespace="testing")),
]
