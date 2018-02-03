from django import template

from web_utils import formatting

register = template.Library()


@register.simple_tag
def format_currency(value, places=2, show_zero="True"):
    """
    Displays value as US currency: $1,500.00
    """
    show_zero = True if show_zero == "True" else False
    return formatting.format_currency(value, places, show_zero)
