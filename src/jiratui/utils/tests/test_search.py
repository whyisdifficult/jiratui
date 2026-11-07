import pytest

from jiratui.utils.search import (
    build_jql_query,
    get_work_item_search_fields,
    get_work_item_search_results_table_columns,
)


def test_get_work_item_search_fields_without_search_results_columns():
    # WHEN
    fields = get_work_item_search_fields([])
    # THEN
    assert fields == ['id', 'key', 'status', 'issuetype', 'parent', 'summary']


def test_get_work_item_search_fields_with_search_results_columns():
    # WHEN
    fields = get_work_item_search_fields(
        ['Status', 'a', 'parent ', 'issuetype', 'summary', 'assignee', 'reporter']
    )
    # THEN
    assert fields == [
        'id',
        'key',
        'status',
        'parent',
        'issuetype',
        'summary',
        'assignee',
        'reporter',
    ]


def test_get_work_item_search_results_table_columns_without_search_results_columns():
    # WHEN
    columns = get_work_item_search_results_table_columns([])
    # THEN
    assert columns == ['Key', 'Status', 'Type', 'Parent', 'Summary']


def test_get_work_item_search_results_table_columns_with_search_results_columns():
    # WHEN
    columns = get_work_item_search_results_table_columns(
        ['Status', 'a', 'parent ', 'issuetype', 'summary', 'assignee', 'reporter']
    )
    # THEN
    assert columns == ['Key', 'Status', 'Parent', 'Type', 'Summary', 'Assignee', 'Reporter']


@pytest.mark.parametrize(
    'search_term, jql_expression, advanced_search, expected_query',
    [
        ('text search', None, False, 'summary ~ "text search" OR description ~ "text search"'),
        ('text search', None, True, 'text ~ "text search"'),
        ('text search', 'project = 1', True, 'text ~ "text search"'),
        (
            'text search',
            'project = 1',
            False,
            'summary ~ "text search" OR description ~ "text search"',
        ),
        (None, None, False, None),
        (None, None, True, None),
        (None, 'project = 1', False, 'project = 1'),
        (None, 'project = 1', True, 'project = 1'),
    ],
)
def test_build_jql_query(
    search_term, jql_expression, advanced_search, expected_query, jira_api_controller
):
    # WHEN
    query = build_jql_query(search_term, jql_expression, advanced_search)
    # THEN
    assert query == expected_query
