from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def activate(context, *paths):
    """
    For use in navigation. Returns "active" if the navigation page
    is the same as the page requested.
    The 'django.template.context_processors.request' context processor
    must be activated in your settings.
    In an exception, django doesnt use a RequestContext, so we can't
    necessarily always assume it being present.
    """
    if 'request' in context:
        return bool(context['request'].path in paths) and "active" or ""
    return ''
