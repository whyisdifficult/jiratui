from datetime import datetime

from jiratui.api.utils import build_issue_search_jql
from jiratui.models import WorkItemsSearchOrderBy


def test_build_issue_search_jql():
    # WHEN
    result = build_issue_search_jql()
    # THEN
    assert result == ''


def test_build_issue_search_jql_with_parameters():
    # WHEN
    result = build_issue_search_jql(
        project_key='P1',
        created_from=datetime(2025, 12, 1).date(),
        created_until=datetime(2025, 12, 2).date(),
        updated_from=datetime(2025, 12, 3).date(),
        updated_until=datetime(2025, 12, 4).date(),
        status=1,
        assignee='1',
        issue_type=2,
    )
    # THEN
    assert result == (
        'project = P1 and created >= "2025-12-01" and created <= "2025-12-02" and updated >= "2025-12-03" and updated <= "2025-12-04" and status = "1" and assignee = "1" and type = 2'
    )


def test_build_issue_search_jql_with_parameters_and_jql_query():
    # WHEN
    result = build_issue_search_jql(
        project_key='P1',
        created_from=datetime(2025, 12, 1).date(),
        created_until=datetime(2025, 12, 2).date(),
        updated_from=datetime(2025, 12, 3).date(),
        updated_until=datetime(2025, 12, 4).date(),
        status=1,
        assignee='1',
        issue_type=2,
        jql_query='q=5',
    )
    # THEN
    assert result == (
        'project = P1 and created >= "2025-12-01" and created <= "2025-12-02" and updated >= "2025-12-03" and updated <= "2025-12-04" and status = "1" and assignee = "1" and type = 2 and q=5'
    )


def test_build_issue_search_jql_without_parameters_and_jql_query():
    # WHEN
    result = build_issue_search_jql(jql_query='q=5')
    # THEN
    assert result == ('q=5')


def test_build_issue_search_jql_without_parameters_and_jql_query_with_order():
    # WHEN
    result = build_issue_search_jql(jql_query='q=5', order_by=WorkItemsSearchOrderBy.KEY_ASC)
    # THEN
    assert result == ('q=5 order by key asc')


def test_build_issue_search_jql_with_parameters_and_jql_query_with_order():
    # WHEN
    result = build_issue_search_jql(
        project_key='P1',
        created_from=datetime(2025, 12, 1).date(),
        created_until=datetime(2025, 12, 2).date(),
        updated_from=datetime(2025, 12, 3).date(),
        updated_until=datetime(2025, 12, 4).date(),
        status=1,
        assignee='1',
        issue_type=2,
        jql_query='q=5',
        order_by=WorkItemsSearchOrderBy.KEY_ASC,
    )
    # THEN
    assert result == (
        'project = P1 and created >= "2025-12-01" and created <= "2025-12-02" and updated >= "2025-12-03" and updated <= "2025-12-04" and status = "1" and assignee = "1" and type = 2 and q=5 order by key asc'
    )
