def decorated_patterns(wrapping_functions, patterns):
    """
    Used to wrap entire URL patterns in a decorator

    adapted from: https://gist.github.com/1378003
    """
    if not isinstance(wrapping_functions, (list, tuple)):
        wrapping_functions = (wrapping_functions, )

    return [_wrap_resolver(wrapping_functions, url_instance) for url_instance in patterns]


def _wrap_resolver(wrapping_functions, url_instance):  # noqa
    resolve_func = getattr(url_instance, 'resolve', None)
    if resolve_func is None:
        return url_instance

    def _wrap_resolved_func(*args, **kwargs):
        result = resolve_func(*args, **kwargs)

        view_func = getattr(result, 'func', None)
        if view_func is None:
            return result

        for _f in reversed(wrapping_functions):
            view_func = _f(view_func)

        setattr(result, 'func', view_func)
        return result

    setattr(url_instance, 'resolve', _wrap_resolved_func)
    return url_instance
