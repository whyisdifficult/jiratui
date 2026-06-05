from unittest.mock import AsyncMock, Mock, patch

import pytest
from textual.widgets import Input

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraIssueSearchResponse
from jiratui.widgets.commons.base import WorkItemKeyAutoComplete


@patch.object(WorkItemKeyAutoComplete, '_use_advanced_full_text_search')
@patch.object(APIController, 'search_issues')
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_without_search_term(
    search_issues_mock: AsyncMock,
    use_advanced_full_text_search_mock: Mock,
    jira_api_controller,
    app,
):
    # GIVEN
    widget = WorkItemKeyAutoComplete(Input(), jira_api_controller)
    # WHEN
    result = await widget._search('')
    # THEN
    assert result is None
    search_issues_mock.assert_not_called()


@patch.object(WorkItemKeyAutoComplete, '_use_advanced_full_text_search')
@patch.object(APIController, 'search_issues')
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_with_advanced_search_disabled(
    search_issues_mock: AsyncMock,
    use_advanced_full_text_search_mock: Mock,
    jira_api_controller,
    jira_issues,
    app,
):
    # GIVEN
    use_advanced_full_text_search_mock.return_value = False
    search_issues_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    widget = WorkItemKeyAutoComplete(Input(), jira_api_controller)
    # WHEN
    result = await widget._search('test')
    # THEN
    assert result == jira_issues
    search_issues_mock.assert_called_once_with(
        jql_query='summary ~ "test" OR description ~ "test" OR workItemKey ~ "test"',
        fields=['id', 'key', 'summary'],
    )


@patch.object(WorkItemKeyAutoComplete, '_use_advanced_full_text_search')
@patch.object(APIController, 'search_issues')
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_with_advanced_search_enabled(
    search_issues_mock: AsyncMock,
    use_advanced_full_text_search_mock: Mock,
    jira_api_controller,
    jira_issues,
    app,
):
    # GIVEN
    use_advanced_full_text_search_mock.return_value = True
    search_issues_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    widget = WorkItemKeyAutoComplete(Input(), jira_api_controller)
    # WHEN
    result = await widget._search('test')
    # THEN
    assert result == jira_issues
    search_issues_mock.assert_called_once_with(
        jql_query='text ~ "test" OR workItemKey ~ "test"',
        fields=['id', 'key', 'summary'],
    )


@patch.object(WorkItemKeyAutoComplete, '_use_advanced_full_text_search')
@patch.object(APIController, 'search_issues')
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_nothing_found(
    search_issues_mock: AsyncMock,
    use_advanced_full_text_search_mock: Mock,
    jira_api_controller,
    jira_issues,
    app,
):
    # GIVEN
    use_advanced_full_text_search_mock.return_value = True
    search_issues_mock.return_value = APIControllerResponse(result=None)
    widget = WorkItemKeyAutoComplete(Input(), jira_api_controller)
    # WHEN
    result = await widget._search('test')
    # THEN
    assert result is None
    search_issues_mock.assert_called_once_with(
        jql_query='text ~ "test" OR workItemKey ~ "test"',
        fields=['id', 'key', 'summary'],
    )


@pytest.mark.parametrize(
    'query',
    [
        None,
        'ts',
    ],
)
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_work_items(
    query,
    jira_api_controller,
    jira_issues,
    app,
):
    # GIVEN
    widget = WorkItemKeyAutoComplete(Input(), jira_api_controller)
    # WHEN
    result = await widget._search_work_items(query)
    # THEN
    assert result is None
    assert widget._cached_suggestions == []


@patch.object(WorkItemKeyAutoComplete, '_search')
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_work_items_none_found(
    search_mock,
    jira_api_controller,
    jira_issues,
    app,
):
    # GIVEN
    search_mock.return_value = None
    widget = WorkItemKeyAutoComplete(
        Input(),
        jira_api_controller,
    )
    # WHEN
    result = await widget._search_work_items('test')
    # THEN
    assert result is None
    assert widget._cached_suggestions == []


@patch.object(WorkItemKeyAutoComplete, '_handle_target_update')
@patch.object(WorkItemKeyAutoComplete, '_search')
@pytest.mark.asyncio
async def test_work_item_key_autocomplete_search_work_items_found(
    search_mock,
    jira_api_controller,
    jira_issues,
    app,
):
    # GIVEN
    search_mock.return_value = jira_issues
    widget = WorkItemKeyAutoComplete(
        Input(),
        jira_api_controller,
    )
    # WHEN
    result = await widget._search_work_items('test')
    # THEN
    assert result is None
    assert len(widget._cached_suggestions) == 2
