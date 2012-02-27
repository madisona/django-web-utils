
from django.conf import settings
from django.http import HttpResponsePermanentRedirect, get_host


class SSLMiddleware(object):
    """
    Lets you specify which urls use SSL and which do not. The middleware
    forces every request to use the protocol specified.

    Available settings to configure (boolean values):
    SSL_ENABLED - Whether to even use SSL or not (Defaults to False)
    USE_SSL_DEFAULT - Use https unless otherwise specified (Defaults to False)


    Usage:
        url('^admin/', include('django.contrib.admin'), kwargs={'USE_SSL': True}),

    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        ssl_enabled = getattr(settings, "SSL_ENABLED", False)
        use_secure_as_default = getattr(settings, "USE_SSL_DEFAULT", False)
        use_secure = view_kwargs.pop("USE_SSL", use_secure_as_default)

        if ssl_enabled and not use_secure == request.is_secure():
            return self._redirect(request, use_secure)

    def _redirect(self, request, use_secure):
        protocol = use_secure and "https" or "http"
        redirect_url = "%s://%s%s" % (protocol, get_host(request), request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError("""Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs.""")

        return HttpResponsePermanentRedirect(redirect_url)
