from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.config import ApplicationConfiguration
from jiratui.models import JiraServerInfo
from jiratui.widgets.quit import QuitScreen
from jiratui.widgets.screens import MainScreen


@pytest.fixture()
def app_with_unrecognized_config_theme() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='WARNING',
        theme='foo',
    )
    app = JiraApp(config_mock)
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.fixture()
def app_with_input_and_config_theme() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='WARNING',
        theme='flexoki',
    )
    app = JiraApp(config_mock, user_theme='monokai')
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.fixture()
def app_with_input_theme() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='WARNING',
        theme=None,
    )
    app = JiraApp(config_mock, user_theme='monokai')
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.fixture()
def app_without_config_theme() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='WARNING',
        theme=None,
    )
    app = JiraApp(config_mock)
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.fixture()
def app() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='WARNING',
        theme='dracula',
    )
    app = JiraApp(config_mock)
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    app.config.tui_title = ''
    app.config.tui_title_include_jira_server_title = False
    async with app.run_test() as pilot:
        assert pilot.app.title == 'JiraTUI'


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title_with_custom_title(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    app.config.tui_title = 'Hello World!'
    app.config.tui_title_include_jira_server_title = False
    async with app.run_test() as pilot:
        assert pilot.app.title == 'Hello World!'


@patch('jiratui.widgets.screens.APIController.server_info')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title_without_custom_title_with_server_info(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    server_info_mock: AsyncMock,
    app,
):
    app.config.tui_title = None
    app.config.tui_title_include_jira_server_title = True
    server_info_mock.return_value = APIControllerResponse(
        result=JiraServerInfo(
            base_url='foo.bar',
            display_url_servicedesk_help_center='nothing',
            display_url_confluence='nothing',
            version='1',
            deployment_type='nothing',
            build_number=1,
            build_date='nothing',
            server_time='nothing',
            scm_info='nothing',
            server_title='my title',
            default_locale='nothing',
            server_time_zone='nothing',
        )
    )
    async with app.run_test() as pilot:
        assert pilot.app.title == 'JiraTUI - my title'


@patch('jiratui.widgets.screens.APIController.server_info')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title_with_custom_title_with_server_info(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    server_info_mock: AsyncMock,
    app,
):
    app.config.tui_title = 'Hello World!'
    app.config.tui_title_include_jira_server_title = True
    server_info_mock.return_value = APIControllerResponse(
        result=JiraServerInfo(
            base_url='foo.bar',
            display_url_servicedesk_help_center='nothing',
            display_url_confluence='nothing',
            version='1',
            deployment_type='nothing',
            build_number=1,
            build_date='nothing',
            server_time='nothing',
            scm_info='nothing',
            server_title='my title',
            default_locale='nothing',
            server_time_zone='nothing',
        )
    )
    async with app.run_test() as pilot:
        assert pilot.app.title == 'Hello World! - my title'


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_quits_without_confirmation(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    app.config.confirm_before_quit = False
    async with app.run_test() as pilot:
        await pilot.press('ctrl+q')
        assert isinstance(app.screen, MainScreen)


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_quits_with_confirmation_no_exit(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    app.config.confirm_before_quit = True
    async with app.run_test() as pilot:
        await pilot.press('ctrl+q')
        assert isinstance(app.screen, QuitScreen)
        assert app.focused.id == 'button-quit'
        await pilot.press('tab')
        assert app.focused.id == 'button-cancel'
        await pilot.press('enter')
        assert isinstance(app.screen, MainScreen)


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_theme_from_config(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        assert pilot.app.theme == 'dracula'


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_with_default_theme(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app_without_config_theme,
):
    async with app_without_config_theme.run_test() as pilot:
        assert pilot.app.theme == 'textual-dark'


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_with_input_theme(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app_with_input_theme,
):
    async with app_with_input_theme.run_test() as pilot:
        assert pilot.app.theme == 'monokai'


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_with_input_and_config_theme(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app_with_input_and_config_theme,
):
    async with app_with_input_and_config_theme.run_test() as pilot:
        assert pilot.app.theme == 'monokai'


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_with_unrecognized_config_theme(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app_with_unrecognized_config_theme,
):
    async with app_with_unrecognized_config_theme.run_test() as pilot:
        assert pilot.app.theme == 'textual-dark'
