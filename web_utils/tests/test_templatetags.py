import mock
from django import template
from django import test
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, Page

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

from web_utils.formatting import format_currency
from web_utils.templatetags import formatting_tags, analytics_tags, html_tags, paginator_tags


class FormatCurrencyTests(test.TestCase):

    def test_show_empty_string_when_amount_is_zero_if_show_zero_is_false(self):
        amount = format_currency(0, show_zero=False)
        self.assertEqual("", amount)

    def test_show_formatted_zero_amount(self):
        amount = format_currency(0)
        self.assertEqual("$0.00", amount)

    def test_show_default_formatted_dollar_amount_when_amount_is_not_zero(self):
        amount = format_currency(123)
        self.assertEqual("$123.00", amount)

    def test_allow_decimal_precision_to_be_specified(self):
        amount = format_currency(123.123456, 4)
        self.assertEqual("$123.1235", amount)

    def test_add_thousand_separator(self):
        amount = format_currency(1000)
        self.assertEqual("$1,000.00", amount)

    def test_show_empty_string_when_value_is_none_and_show_zero_is_False(self):
        amount = format_currency(None, show_zero=False)
        self.assertEqual("", amount)

    def test_show_zero_when_value_is_none_and_show_zero_is_True(self):
        amount = format_currency(None)
        self.assertEqual("$0.00", amount)


class FormatCurrencyTemplateTagTests(test.TestCase):

    def test_show_empty_string_when_amount_is_zero_if_show_zero_is_false(self):
        amount = formatting_tags.format_currency(0, show_zero="False")
        self.assertEqual("", amount)

    def test_show_formatted_zero_amount(self):
        amount = formatting_tags.format_currency(0)
        self.assertEqual("$0.00", amount)

    def test_show_default_formatted_dollar_amount_when_amount_is_not_zero(self):
        amount = formatting_tags.format_currency(123)
        self.assertEqual("$123.00", amount)

    def test_allow_decimal_precision_to_be_specified(self):
        amount = formatting_tags.format_currency(123.123456, 4)
        self.assertEqual("$123.1235", amount)

    def test_add_thousand_separator(self):
        amount = formatting_tags.format_currency(1000)
        self.assertEqual("$1,000.00", amount)

    def test_show_empty_string_when_value_is_none_and_show_zero_is_False(self):
        amount = formatting_tags.format_currency(None, show_zero="False")
        self.assertEqual("", amount)

    def test_show_zero_when_value_is_none_and_show_zero_is_True(self):
        amount = formatting_tags.format_currency(None, show_zero="True")
        self.assertEqual("$0.00", amount)


class TrackEventTemplateTagTests(test.TestCase):

    def test_leaves_label_hyphens(self):
        output = analytics_tags.track_event("Category", "action", "company-id")
        expected = "onClick=\"_gaq.push(['_trackEvent', 'Category', 'action', 'company-id']);\""
        self.assertEqual(expected, output)

    def test_escapes_js_for_label(self):
        output = analytics_tags.track_event("Category", "action", "company's bad;-stuff.")
        expected = "onClick=\"_gaq.push(['_trackEvent', 'Category', 'action', 'company\\u0027s bad\\u003B-stuff.']);\""
        self.assertEqual(expected, output)


class UniversalTrackEventTemplateTagTests(test.TestCase):

    def test_leaves_label_hyphens(self):
        output = analytics_tags.universal_track_event("Category", "action", "company-id")
        expected = "onClick=\"ga('send', 'event', 'Category', 'action', 'company-id');\""
        self.assertEqual(expected, output)

    def test_escapes_js_for_label(self):
        output = analytics_tags.universal_track_event("Category", "action", "company's bad;-stuff.")
        expected = "onClick=\"ga('send', 'event', 'Category', 'action', 'company\\u0027s bad\\u003B-stuff.');\""
        self.assertEqual(expected, output)


class GTagTrackEventTemplateTagTests(test.TestCase):

    def test_leaves_label_hyphens(self):
        output = analytics_tags.gtag_track_event("Category", "action", "company-id")
        expected = "onClick=\"gtag('event', 'action', {'event_category': 'Category', 'event_label': 'company-id'});\""
        self.assertEqual(expected, output)

    def test_escapes_js_for_label(self):
        output = analytics_tags.gtag_track_event("Category", "action", "company's bad;-stuff.")
        expected = "onClick=\"gtag('event', 'action', {'event_category': 'Category', 'event_label': 'company\\u0027s bad\\u003B-stuff.'});\""  # noqa: E501
        self.assertEqual(expected, output)


class AnalyticsSnippetTemplateTagTests(test.TestCase):

    def _render_template(self):
        t = template.Template("""
            {% load analytics_tags %}
            {% analytics_snippet %}
        """)
        request = test.RequestFactory().get('/my/path/')
        context = template.RequestContext(request)
        return t.render(context)

    @test.override_settings(GOOGLE_ANALYTICS_ID="UA-1234567", GOOGLE_ANALYTICS_DOMAIN="www.example.com")
    def test_renders_analytics_snippet(self):
        response = self._render_template()
        self.assertIn("ga('create', 'UA-1234567', 'www.example.com');", response)

    def test_raises_improperly_configured_when_neither_settings_not_defined(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            self._render_template()
        self.assertEqual(
            "You must define GOOGLE_ANALYTICS_ID and GOOGLE_ANALYTICS_DOMAIN in settings.", str(e.exception)
        )

    @test.override_settings(GOOGLE_ANALYTICS_ID="UA-1234567")
    def test_raises_improperly_configured_when_only_analytics_id_defined(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            self._render_template()
        self.assertEqual(
            "You must define GOOGLE_ANALYTICS_ID and GOOGLE_ANALYTICS_DOMAIN in settings.", str(e.exception)
        )

    @test.override_settings(GOOGLE_ANALYTICS_DOMAIN="www.example.com")
    def test_raises_improperly_configured_when_only_analytics_domain_defined(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            self._render_template()
        self.assertEqual(
            "You must define GOOGLE_ANALYTICS_ID and GOOGLE_ANALYTICS_DOMAIN in settings.", str(e.exception)
        )


class AnalyticsGtagSnippetTemplateTagTests(test.TestCase):

    def _render_template(self):
        t = template.Template(
            """
            {% load analytics_tags %}
            {% analytics_gtag_snippet %}
        """
        )
        request = test.RequestFactory().get('/my/path/')
        context = template.RequestContext(request)
        return t.render(context)

    @test.override_settings(GOOGLE_ANALYTICS_ID="UA-1234567")
    def test_renders_analytics_snippet(self):
        response = self._render_template()
        self.assertIn("gtag('config', 'UA-1234567');", response)

    def test_raises_improperly_configured_when_neither_settings_not_defined(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            self._render_template()
        self.assertEqual("You must define GOOGLE_ANALYTICS_ID in settings.", str(e.exception))


class ActivateTemplateTagTests(test.TestCase):

    def test_returns_active_when_request_is_same_path(self):
        t = template.Template(
            """
            {% load html_tags %}
            <a href="/my/path/" class="{% activate '/my/path/' %}">Nav Tab</a>
        """
        )
        request = test.RequestFactory().get('/my/path/')
        context = template.RequestContext(request)
        response = t.render(context)
        self.assertEqual('<a href="/my/path/" class="active">Nav Tab</a>', response.strip())

    def test_returns_active_when_request_is_same_path_as_additional_url(self):
        t = template.Template(
            """
            {% load html_tags %}
            <a href="/my/path/" class="{% activate '/one-path' '/two-path/' '/my/path/' %}">Nav Tab</a>
        """
        )
        request = test.RequestFactory().get('/two-path/')
        context = template.RequestContext(request)
        response = t.render(context)
        self.assertEqual('<a href="/my/path/" class="active">Nav Tab</a>', response.strip())

    def test_returns_empty_string_when_nav_tab_is_not_current_request(self):
        t = template.Template(
            """
            {% load html_tags %}
            <a href="/home/page/" class="{% activate '/home/page/' %}">Nav Tab</a>
        """
        )
        request = test.RequestFactory().get('/other/path/')
        context = template.RequestContext(request)
        response = t.render(context)
        self.assertEqual('<a href="/home/page/" class="">Nav Tab</a>', response.strip())

    def test_returns_empty_string_when_doesnt_have_request_context(self):
        context = template.Context({})
        result = html_tags.activate(context, "/")
        self.assertEqual("", result)


class PaginatorTests(test.TestCase):

    def test_returns_next_list_of_pages_when_starting_with_first(self):
        places = paginator_tags.get_pages_to_show(1, 5)
        self.assertEqual([1, 2, 3, 4, 5], list(places))

    def test_returns_places_in_decent_order_when_second(self):
        places = paginator_tags.get_pages_to_show(2, 5)
        self.assertEqual([1, 2, 3, 4, 5], list(places))

    def test_returns_places_in_decent_order_when_third(self):
        places = paginator_tags.get_pages_to_show(3, 5)
        self.assertEqual([1, 2, 3, 4, 5], list(places))

    def test_keeps_current_page_in_middle_when_has_more_than_two_previous_and_two_next(self):
        places = paginator_tags.get_pages_to_show(4, 6)
        self.assertEqual([2, 3, 4, 5, 6], list(places))

    def test_returns_straight_list_when_less_than_5_pages(self):
        places = paginator_tags.get_pages_to_show(1, 2)
        self.assertEqual([1, 2], list(places))

    def test_returns_correct_list_when_on_last_page_and_less_than_5(self):
        places = paginator_tags.get_pages_to_show(3, 3)
        self.assertEqual([1, 2, 3], list(places))


class ShowPaginatorTests(test.TestCase):

    @mock.patch.object(paginator_tags, 'get_pages_to_show')
    def test_sends_page_numbers_to_template(self, get_pages_to_show):
        paginator = mock.Mock(Paginator, num_pages=5)
        page_obj = mock.Mock(Page, number=2)

        result = paginator_tags.show_paginator(page_obj, paginator)
        self.assertEqual(get_pages_to_show.return_value, result["page_numbers"])
        get_pages_to_show.assert_called_once_with(page_obj.number, paginator.num_pages)

    def test_sends_page_obj_to_template(self):
        paginator = mock.Mock(Paginator, num_pages=5)
        page_obj = mock.Mock(Page, number=2)

        result = paginator_tags.show_paginator(page_obj, paginator)
        self.assertEqual(page_obj, result["page_obj"])

    def test_sends_query_string_to_context(self):
        request = test.RequestFactory().get("/", data={"this": "thing", "that": "way"})
        paginator = mock.Mock(Paginator, num_pages=5)
        page_obj = mock.Mock(Page, number=2)

        result = paginator_tags.show_paginator(page_obj, paginator, request.GET)
        self.assertEqual(dict(request.GET), dict(parse_qs(result["query_string"])))

    def test_sends_query_string_without_page_param_to_context(self):
        request = test.RequestFactory().get("/", data={"this": "thing", "that": "way", "page": 4})
        paginator = mock.Mock(Paginator, num_pages=5)
        page_obj = mock.Mock(Page, number=2)

        data_copy = request.GET.copy()
        del (data_copy["page"])
        result = paginator_tags.show_paginator(page_obj, paginator, request.GET)
        self.assertEqual(data_copy.urlencode(), result["query_string"])


class GetSettingTagTests(test.TestCase):

    def test_puts_setting_value_in_template(self):
        expected = "Some Value"

        with self.settings(TEST_VARIABLE=expected):
            t = template.Template(
                """
                {% load settings_tags %}
                {% get_setting 'TEST_VARIABLE' %}
            """
            )
            self.assertEqual(expected, t.render(template.Context({})).strip())

    def test_defaults_to_empty_string_when_setting_not_found(self):

        t = template.Template(
            """
            {% load settings_tags %}
            {% get_setting 'SOME_CRAZY_SETTING_THAT_DOESNT_EXIST' %}
        """
        )
        self.assertEqual("", t.render(template.Context({})).strip())
