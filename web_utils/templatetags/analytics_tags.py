from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escapejs

register = template.Library()


@register.inclusion_tag("web_utils/analytics_snippet.html")
def analytics_snippet():
    analytics_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', None)
    analytics_domain = getattr(settings, 'GOOGLE_ANALYTICS_DOMAIN', None)
    if not (analytics_id and analytics_domain):
        raise ImproperlyConfigured("You must define GOOGLE_ANALYTICS_ID and GOOGLE_ANALYTICS_DOMAIN in settings.")

    return {
        'GOOGLE_ANALYTICS_ID': analytics_id,
        'GOOGLE_ANALYTICS_DOMAIN': analytics_domain,
    }


@register.simple_tag
def track_event(category, action, label):
    return "onClick=\"_gaq.push(['_trackEvent', '{category}', '{action}', '{label}']);\"".format(
        category=escapejs(category),
        action=escapejs(action),
        label=escapejs(label).replace("\\u002D", "-"),
    )


@register.simple_tag
def universal_track_event(category, action, label):
    return "onClick=\"ga('send', 'event', '{category}', '{action}', '{label}');\"".format(
        category=escapejs(category),
        action=escapejs(action),
        label=escapejs(label).replace("\\u002D", "-"),
    )
