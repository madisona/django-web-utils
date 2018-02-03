def format_currency(value, places=2, show_zero=True):
    """
    Formats value currency format like: $1,500.25

    :param places:
        number of decimal places to show.
    :param show_zero:
        When true, zero should be formatted.
        When false, zero should be empty string.
    """
    if value in (0, None) and not show_zero:
        return ''
    return "${value:,.{precision}f}".format(value=value or 0, precision=places)
