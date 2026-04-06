from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.commons.users import JiraUserInput
from jiratui.widgets.screens import WorkItemSearchResult
from jiratui.widgets.work_item_details.details import IssueDetailsWidget


@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_by_issue_key(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        get_issue_mock.return_value = APIControllerResponse(
            result=JiraIssueSearchResponse(issues=[jira_issues[1]])
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.resize_terminal(600, 400)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('right')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('q')
        await pilot.press('w')
        await pilot.press('r')
        # THEN
        assert isinstance(main_screen.focused, JiraUserInput)
        assert main_screen.focused.id == 'edit-work-item-input-assignee'
        assert main_screen.search_results_table.focus()
        assert main_screen.search_results_table.page == 1
        search_work_items_mock.assert_called_once()
        assert main_screen.search_results_table.search_results == JiraIssueSearchResponse(
            issues=jira_issues, next_page_token=None, is_last=None
        )
        assert main_screen.search_results_table.current_work_item_key == 'key-2'
        search_users_assignable_to_issue_mock.assert_called_once_with(
            issue_key='key-2', query='qwr'
        )


@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_select_and_display_work_item(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        get_issue_mock.return_value = APIControllerResponse(
            result=JiraIssueSearchResponse(issues=[jira_issues[1]])
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('right')
        await pilot.press('tab')
        # THEN
        assert main_screen.search_results_table.focus()
        assert main_screen.search_results_table.page == 1
        search_work_items_mock.assert_called_once()
        assert main_screen.search_results_table.search_results == JiraIssueSearchResponse(
            issues=jira_issues, next_page_token=None, is_last=None
        )
        assert main_screen.search_results_table.current_work_item_key == 'key-2'
        focused_widget = main_screen.focused
        assert isinstance(focused_widget, IssueDetailsWidget)
        assert focused_widget.issue_key_field.value == 'key-2'
        assert focused_widget.issue_summary_field.value == 'qwerty'
        assert focused_widget.project_id_field.value == '(P1) Project 1'
        assert focused_widget.issue_created_date_field.value == '2025-10-11 00:00'
        assert focused_widget.issue_created_date_field.value == '2025-10-11 00:00'
        assert focused_widget.issue_due_date_field.value == '2025-10-12'
        assert focused_widget.issue_resolution_date_field.value == '2025-10-11 00:00'
        assert focused_widget.issue_parent_field.value == 'P2'
        assert focused_widget.issue_type_field.value == 'Bug'
        assert focused_widget.priority_selector.selection == '1'
        assert focused_widget.reporter_field.value == 'Bart Simpson'
        assert focused_widget.assignee_selector.value == ''
        assert focused_widget.issue_resolution_field.value == 'this was done'
        assert focused_widget.issue_sprint_field.value == 'This Sprint'
