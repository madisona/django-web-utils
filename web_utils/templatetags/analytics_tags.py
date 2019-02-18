from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escapejs, mark_safe

register = template.Library()


# deprecated
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


@register.inclusion_tag("web_utils/analytics_gtag_snippet.html")
def analytics_gtag_snippet():
    analytics_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', None)
    if not analytics_id:
        raise ImproperlyConfigured("You must define GOOGLE_ANALYTICS_ID in settings.")

    return {
        'GOOGLE_ANALYTICS_ID': analytics_id,
    }


# deprecated
@register.simple_tag
def track_event(category, action, label):
    return mark_safe("onClick=\"_gaq.push(['_trackEvent', '{category}', '{action}', '{label}']);\"".format(
        category=escapejs(category),
        action=escapejs(action),
        label=escapejs(label).replace("\\u002D", "-"),
    ))


# deprecated
@register.simple_tag
def universal_track_event(category, action, label):
    return mark_safe("onClick=\"ga('send', 'event', '{category}', '{action}', '{label}');\"".format(
        category=escapejs(category),
        action=escapejs(action),
        label=escapejs(label).replace("\\u002D", "-"),
    ))


@register.simple_tag
def gtag_track_event(category, action, label):
    """
    This is the most recent style. the gtag snippet replaced the universal track event
    """
    return mark_safe("onClick=\"gtag('event', '{action}', {{'event_category': '{category}', 'event_label': '{label}'}});\"".format(  # noqa: E501
        category=escapejs(category),
        action=escapejs(action),
        label=escapejs(label).replace("\\u002D", "-"),
    ))
