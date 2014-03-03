
from django import template
from django.utils.html import escapejs

register = template.Library()


@register.simple_tag
def track_event(category, action, label):
    return "onClick=\"_gaq.push(['_trackEvent', '{category}', '{action}', '{label}']);\"".format(
        category=escapejs(category),
        action=escapejs(action),
        label=escapejs(label).replace("\u002D", "-"),
    )
