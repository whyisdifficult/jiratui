from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

from pydantic import SecretStr
import pytest

from jiratui.api_controller.controller import APIController
from jiratui.app import JiraApp
from jiratui.config import ApplicationConfiguration
from jiratui.models import JiraIssue, JiraIssueSearchResponse, WorkItemsSearchOrderBy
from jiratui.widgets.screens import WorkItemSearchResult
from jiratui.widgets.search import IssuesSearchResultsTable


@pytest.fixture()
def app() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token=SecretStr('bar'),
        jira_api_version=3,
        use_bearer_authentication=False,
        cloud=True,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        active_sprint_on_startup=False,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_custom_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='ERROR',
        theme=None,
        search_results_page_filtering_enabled=False,
        ssl=None,
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        search_on_startup=False,
    )
    app = JiraApp(config_mock)
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_next_page_search_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 1
        main_screen.search_results_table.token_by_page = {2: 'token_a'}
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('alt+right')
        # THEN
        assert main_screen.search_results_table.page == 2
        search_issues_mock.assert_called_once_with('token_a', page=2)


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_next_page_search_results_with_missing_token(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 0
        main_screen.search_results_table.token_by_page = {2: 'token_a'}
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('alt+right')
        # THEN
        search_issues_mock.assert_not_called()
        assert main_screen.search_results_table.page == 0


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_previous_page_search_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 2
        main_screen.search_results_table.token_by_page = {1: 'token_a'}
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('alt+left')
        # THEN
        search_issues_mock.assert_called_once_with('token_a', page=1)
        assert main_screen.search_results_table.page == 1


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_previous_page_search_results_with_missing_token(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 1
        main_screen.search_results_table.token_by_page = {2: 'token_a'}
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('alt+left')
        # THEN
        search_issues_mock.assert_not_called()
        assert main_screen.search_results_table.page == 1


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_filter_datatable_filtering_key_shows_input(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    app.config.search_results_page_filtering_enabled = True
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('.')
        # THEN
        assert main_screen.search_results_filter_input.display is True
        assert main_screen.search_results_table.page == 1


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_filter_datatable_filtering_key_feature_disabled(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    app.config.search_results_page_filtering_enabled = False
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('.')
        # THEN
        assert main_screen.search_results_filter_input.display is False
        assert main_screen.search_results_table.page == 1


@patch.object(IssuesSearchResultsTable, 'get_initial_results_set')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_filter_datatable_filtering_key_hides_input(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    get_initial_results_set_mock: Mock,
    app,
):
    app.config.search_results_page_filtering_enabled = True
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('.')
        # THEN
        assert main_screen.search_results_filter_input.display is True
        await pilot.press('escape')
        assert main_screen.search_results_filter_input.display is False
        get_initial_results_set_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'get_initial_results_set')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_datatable_filtering_yields_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    get_initial_results_set_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_page_filtering_enabled = True
    app.config.search_results_page_filtering_minimum_term_length = 3
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    get_initial_results_set_mock.side_effect = [
        JiraIssueSearchResponse(issues=jira_issues[0:]),
        JiraIssueSearchResponse(issues=jira_issues[0:]),
        JiraIssueSearchResponse(issues=jira_issues[0:]),
    ]
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('.')
        await pilot.press('a')
        await pilot.press('b')
        await pilot.press('c')
        # THEN
        assert main_screen.search_results_filter_input.value == 'abc'
        assert main_screen.search_results_table.page == 1
        get_initial_results_set_mock.assert_has_calls([call(), call(), call()])
        assert main_screen.search_results_filter_input.total == 1
        assert main_screen.search_results_filter_input.border_subtitle == 'Found: 1'


@patch.object(IssuesSearchResultsTable, 'get_initial_results_set')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_datatable_filtering_yields_no_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    get_initial_results_set_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_page_filtering_enabled = True
    app.config.search_results_page_filtering_minimum_term_length = 3
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    get_initial_results_set_mock.side_effect = [
        JiraIssueSearchResponse(issues=jira_issues[0:]),
        JiraIssueSearchResponse(issues=jira_issues[0:]),
        JiraIssueSearchResponse(issues=jira_issues[0:]),
    ]
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('.')
        await pilot.press('a')
        await pilot.press('b')
        await pilot.press('d')
        # THEN
        assert main_screen.search_results_filter_input.value == 'abd'
        assert main_screen.search_results_table.page == 1
        get_initial_results_set_mock.assert_has_calls([call(), call(), call()])
        assert main_screen.search_results_filter_input.total == 0
        assert main_screen.search_results_filter_input.border_subtitle == 'Found: 0'


@patch('jiratui.widgets.search.build_external_url_for_issue')
@patch.object(JiraApp, 'open_url')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_issue_in_browser(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    open_url_mock: Mock,
    build_external_url_for_issue_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    build_external_url_for_issue_mock.return_value = 'https://foo.bar/key-2'
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('down')
        await pilot.press('ctrl+o')
        # THEN
        assert main_screen.search_results_table.focus()
        assert main_screen.search_results_table.page == 1
        search_work_items_mock.assert_called_once()
        assert main_screen.search_results_table.search_results == JiraIssueSearchResponse(
            issues=jira_issues, next_page_token=None, is_last=None
        )
        assert main_screen.search_results_table.current_work_item_key == jira_issues[1].key
        open_url_mock.assert_called_once()
        assert main_screen.search_results_container.border_subtitle == 'Page 1 of 1 (total: 2)'


@patch('jiratui.widgets.screens.MainScreen.fetch_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_select_issue_in_search_results_datatable(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    fetch_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        # THEN
        assert main_screen.search_results_table.focus()
        assert main_screen.search_results_table.page == 1
        search_work_items_mock.assert_called_once()
        assert main_screen.search_results_table.search_results == JiraIssueSearchResponse(
            issues=jira_issues, next_page_token=None, is_last=None
        )
        assert main_screen.search_results_table.current_work_item_key == jira_issues[1].key
        assert main_screen.search_results_container.border_subtitle == 'Page 1 of 1 (total: 2)'
        fetch_issue_mock.assert_called_once_with('key-2')
