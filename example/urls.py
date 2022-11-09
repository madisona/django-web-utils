import django

if django.get_version() >= '2.0.0':
    from django.urls import re_path as url
else:
    from django.conf.urls import url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from django.views.generic import View

urlpatterns = [
    url(r'^$', View.as_view(), name='sitemap'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
