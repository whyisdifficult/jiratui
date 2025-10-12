from unittest.mock import AsyncMock, patch

import pytest

from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.git_screen import GitScreen
from jiratui.widgets.screens import WorkItemSearchResult


@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_git_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == 'feature/key-2'
        assert app.screen.create_branch_button.disabled is True


@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_select_repo(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == 'feature/key-2'
        assert app.screen.create_branch_button.disabled is False
        assert app.screen.repository_selector.selection == 'path/a/.git'
        assert app.screen.label_input.content == 'Target Repository: path/a/.git'
