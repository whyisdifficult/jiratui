from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from pydantic import SecretStr
import pytest
from textual.widgets import Input

from jiratui.api_controller.controller import APIController
from jiratui.app import JiraApp
from jiratui.config import ApplicationConfiguration
from jiratui.models import WorkItemsSearchOrderBy
from jiratui.widgets.screens import MainScreen
from jiratui.widgets.text_search import TextSearchScreen


@pytest.fixture()
def app() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token=SecretStr('foo'),
        jira_api_version=3,
        cloud=True,
        ssl=None,
        use_bearer_authentication=False,
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
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        enable_advanced_full_text_search=True,
        full_text_search_minimum_term_length=3,
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
async def test_open_fulltext_search_screen(
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
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('/')
        # THEN
        assert isinstance(app.screen, TextSearchScreen)
        assert isinstance(app.focused, Input)


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_fulltext_search_screen(
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
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('/')
        # THEN
        assert isinstance(app.screen, TextSearchScreen)
        await pilot.press('escape')
        assert isinstance(app.screen, MainScreen)


@patch('jiratui.widgets.screens.MainScreen.action_search')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_fulltext_search_screen_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    action_search_mock: AsyncMock,
    app,
):
    action_search_mock.return_value = None
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('/')
        # THEN
        assert isinstance(app.screen, TextSearchScreen)
        await pilot.press('t')
        await pilot.press('e')
        await pilot.press('s')
        await pilot.press('t')
        await pilot.press('enter')
        assert isinstance(app.screen, MainScreen)
        action_search_mock.assert_called_once_with(search_term='test')


@patch('jiratui.widgets.screens.MainScreen.action_search')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_fulltext_search_screen_with_value_shorter_than_minimum_length(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    action_search_mock: AsyncMock,
    app,
):
    action_search_mock.return_value = None
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('/')
        # THEN
        assert isinstance(app.screen, TextSearchScreen)
        await pilot.press('t')
        await pilot.press('e')
        await pilot.press('enter')
        assert isinstance(app.screen, MainScreen)
        action_search_mock.assert_not_called()


@patch('jiratui.widgets.screens.MainScreen.action_search')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_fulltext_search_screen_with_empty_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    action_search_mock: AsyncMock,
    app,
):
    action_search_mock.return_value = None
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('/')
        # THEN
        assert isinstance(app.screen, TextSearchScreen)
        await pilot.press(' ')
        await pilot.press('enter')
        assert isinstance(app.screen, MainScreen)
        action_search_mock.assert_not_called()


@patch('jiratui.widgets.screens.MainScreen.action_search')
@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_dismiss_fulltext_search_screen_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    action_search_mock: AsyncMock,
    app,
):
    action_search_mock.return_value = None
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.focus()
        # WHEN
        await pilot.press('/')
        # THEN
        assert isinstance(app.screen, TextSearchScreen)
        await pilot.press('t')
        await pilot.press('escape')
        assert isinstance(app.screen, MainScreen)
        action_search_mock.assert_not_called()


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
    # GIVEN
    screen = MainScreen(api=jira_api_controller)
    # WHEN
    query = screen._build_jql_query(search_term, jql_expression, advanced_search)
    # THEN
    assert query == expected_query
