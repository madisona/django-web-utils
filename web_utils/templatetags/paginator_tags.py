from django import template

register = template.Library()


def get_pages_to_show(current_page, total_pages):
    """
    Gets page numbers +/- 2 from current page.
    """
    page_list = []
    if total_pages > 5:
        for s in [-2, -1, 0, 1, 2]:
            num = current_page + s
            if 0 < num <= total_pages:
                page_list.append(num)
    else:
        page_list = range(1, min(total_pages, 5) + 1)
    return page_list


def get_query_without_page(get_params):
    """
    This is used so we can show the pagination properly keeping the search results.
    """
    query_string_without_page = get_params.copy()
    if 'page' in query_string_without_page:
        del query_string_without_page['page']
    return query_string_without_page.urlencode()


@register.inclusion_tag("web_utils/paginator.html")
def show_paginator(page, paginator, get_params=None):
    """
    :param page:
        The page_obj used by the paginator
    :param paginator:
        The actual paginator object
    :param get_params:
        The GET parameters of the page. Used for when you want to paginate search
        results, but we need to keep the parameters so the subsequent pages & links
        can properly execute the query and keep track of the right results,
    """
    query_string = None
    if get_params:
        query_string = get_query_without_page(get_params)
    return {
        'page_numbers': get_pages_to_show(page.number, paginator.num_pages),
        'page_obj': page,
        'query_string': query_string,
    }
