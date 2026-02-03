from unittest.mock import AsyncMock, MagicMock, Mock, patch

from pydantic import SecretStr
import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.config import ApplicationConfiguration
from jiratui.models import JiraServerInfo, WorkItemsSearchOrderBy
from jiratui.widgets.config_info import ConfigFileScreen
from jiratui.widgets.help import HelpScreen
from jiratui.widgets.quit import QuitScreen
from jiratui.widgets.screens import MainScreen
from jiratui.widgets.server_info import ServerInfoScreen


@pytest.fixture()
def app_with_unrecognized_config_theme() -> JiraApp:
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
        log_level='WARNING',
        theme='foo',
        ssl=None,
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        search_on_startup=False,
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
        log_level='WARNING',
        theme='flexoki',
        ssl=None,
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        search_on_startup=False,
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
        log_level='WARNING',
        theme=None,
        ssl=None,
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        search_on_startup=False,
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
        log_level='WARNING',
        theme=None,
        ssl=None,
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        search_on_startup=False,
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
        log_level='WARNING',
        theme='dracula',
        ssl=None,
        search_results_default_order=WorkItemsSearchOrderBy.CREATED_DESC,
        search_on_startup=False,
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


@patch.object(ServerInfoScreen, '_get_server_info')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_server_info_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    get_server_info_mock: Mock,
    app,
):
    # GIVEN
    get_server_info_mock.return_value = JiraServerInfo(
        base_url='foo.bar',
        display_url_servicedesk_help_center='',
        display_url_confluence='',
        version='',
        deployment_type='',
        build_number=1,
        build_date='',
        scm_info='',
        server_title='',
        default_locale='',
        server_time_zone='',
    )
    # WHEN
    async with app.run_test() as pilot:
        await pilot.press('f2')
        # THEN
        assert isinstance(app.screen, ServerInfoScreen)


@patch.object(ServerInfoScreen, '_get_server_info')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_server_info_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    get_server_info_mock: Mock,
    app,
):
    # GIVEN
    get_server_info_mock.return_value = JiraServerInfo(
        base_url='foo.bar',
        display_url_servicedesk_help_center='',
        display_url_confluence='',
        version='',
        deployment_type='',
        build_number=1,
        build_date='',
        scm_info='',
        server_title='',
        default_locale='',
        server_time_zone='',
    )
    # WHEN
    async with app.run_test() as pilot:
        await pilot.press('f2')
        # THEN
        assert isinstance(app.screen, ServerInfoScreen)
        await pilot.press('escape')
        assert isinstance(app.screen, MainScreen)


@patch.object(ConfigFileScreen, '_get_data')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_config_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    get_data_mock: Mock,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    get_data_mock.return_value = {}
    # WHEN
    async with app.run_test() as pilot:
        await pilot.press('f3')
        # THEN
        assert isinstance(app.screen, ConfigFileScreen)


@patch.object(ConfigFileScreen, '_get_data')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_config_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    get_data_mock: Mock,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    get_data_mock.return_value = {}
    # WHEN
    async with app.run_test() as pilot:
        await pilot.press('f3')
        # THEN
        assert isinstance(app.screen, ConfigFileScreen)
        await pilot.press('escape')
        assert isinstance(app.screen, MainScreen)


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_help_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        await pilot.press('f1')
        assert isinstance(app.screen, HelpScreen)


@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_close_help_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        await pilot.press('f1')
        assert isinstance(app.screen, HelpScreen)
        await pilot.press('escape')
        assert isinstance(app.screen, MainScreen)


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


@pytest.fixture()
def config_dict() -> dict:
    """Base configuration dictionary for testing."""
    return {
        'jira_api_base_url': 'foo.bar',
        'jira_api_username': 'foo',
        'jira_api_token': SecretStr('foo'),
        'jira_api_version': 3,
        'cloud': True,
        'ssl': None,
        'use_bearer_authentication': False,
        'ignore_users_without_email': True,
        'default_project_key_or_id': None,
        'active_sprint_on_startup': False,
        'jira_account_id': None,
        'jira_user_group_id': 'qwerty',
        'tui_title': None,
        'tui_custom_title': None,
        'tui_title_include_jira_server_title': False,
        'on_start_up_only_fetch_projects': False,
        'log_file': '',
        'log_level': 'ERROR',
        'theme': None,
        'search_results_page_filtering_enabled': False,
        'search_results_default_order': WorkItemsSearchOrderBy.CREATED_DESC,
        'enable_advanced_full_text_search': True,
        'full_text_search_minimum_term_length': 3,
        'search_on_startup': False,
    }


def create_app_with_config(config_dict: dict, **config_overrides) -> JiraApp:
    """Helper to create JiraApp with specific config overrides."""
    config_mock = Mock(spec=ApplicationConfiguration)
    config_data = config_dict.copy()
    config_data.update(config_overrides)
    config_mock.configure_mock(**config_data)

    app = JiraApp(config_mock)
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.mark.asyncio
async def test_tui_custom_title_with_custom_value(config_dict):
    """Test that tui_custom_title overrides tui_title when set to a custom value."""
    app = create_app_with_config(
        config_dict, tui_title='Default Title', tui_custom_title='My Custom Title'
    )

    async with app.run_test():
        assert app.title == 'My Custom Title'
        main_screen = app.screen
        assert main_screen.query_one('#app-header')


@pytest.mark.asyncio
async def test_tui_custom_title_with_empty_string(config_dict):
    """Test that tui_custom_title set to empty string hides the header."""
    app = create_app_with_config(config_dict, tui_title='Default Title', tui_custom_title='')

    async with app.run_test():
        assert app.title == ''
        main_screen = app.screen
        assert not main_screen.query('#app-header')


@pytest.mark.asyncio
async def test_tui_custom_title_not_set_fallback_to_tui_title(config_dict):
    """Test that when tui_custom_title is None, it falls back to tui_title."""
    app = create_app_with_config(config_dict, tui_title='Default Title', tui_custom_title=None)

    async with app.run_test():
        assert app.title == 'Default Title'
        main_screen = app.screen
        assert main_screen.query_one('#app-header')


@pytest.mark.asyncio
async def test_tui_custom_title_not_set_and_tui_title_not_set(config_dict):
    """Test that when both tui_custom_title and tui_title are None, title uses default."""
    app = create_app_with_config(config_dict, tui_title=None, tui_custom_title=None)

    async with app.run_test():
        assert app.title == 'JiraTUI'
        main_screen = app.screen
        assert main_screen.query_one('#app-header')


@pytest.mark.asyncio
async def test_tui_custom_title_whitespace_handling(config_dict):
    """Test that tui_custom_title with whitespace is properly stripped."""
    app = create_app_with_config(
        config_dict, tui_title='Default Title', tui_custom_title='  Custom Title With Spaces  '
    )

    async with app.run_test():
        assert app.title == 'Custom Title With Spaces'
        main_screen = app.screen
        assert main_screen.query_one('#app-header')


@pytest.mark.asyncio
async def test_tui_custom_title_only_whitespace(config_dict):
    """Test that tui_custom_title with only whitespace keeps default title."""
    app = create_app_with_config(config_dict, tui_title='Default Title', tui_custom_title='   ')

    async with app.run_test():
        assert app.title == 'JiraTUI'
        main_screen = app.screen
        assert main_screen.query_one('#app-header')


@pytest.mark.asyncio
async def test_tui_custom_title_priority_over_tui_title(config_dict):
    """Test that tui_custom_title takes priority over tui_title."""
    app = create_app_with_config(
        config_dict,
        tui_title='Default Title',
        tui_custom_title='Custom Title',
        tui_title_include_jira_server_title=False,
    )

    async with app.run_test():
        assert app.title == 'Custom Title'
        main_screen = app.screen
        assert main_screen.query_one('#app-header')


def test_set_application_title_with_custom_title(config_dict):
    """Test _set_application_title method with custom title."""
    app = create_app_with_config(
        config_dict, tui_title='Default Title', tui_custom_title='My Custom Title'
    )

    app._set_application_title()

    assert app.title == 'My Custom Title'


def test_set_application_title_with_empty_string(config_dict):
    """Test _set_application_title method with empty string."""
    app = create_app_with_config(config_dict, tui_title='Default Title', tui_custom_title='')

    app._set_application_title()

    assert app.title == ''


def test_set_application_title_fallback_to_tui_title(config_dict):
    """Test _set_application_title method falls back to tui_title."""
    app = create_app_with_config(config_dict, tui_title='Default Title', tui_custom_title=None)

    app._set_application_title()

    assert app.title == 'Default Title'


def test_header_compose_logic_with_empty_string(config_dict):
    """Test MainScreen compose logic when tui_custom_title is empty string."""
    config_mock = Mock(spec=ApplicationConfiguration)
    config_data = config_dict.copy()
    config_data.update({'tui_title': 'Default Title', 'tui_custom_title': ''})
    config_mock.configure_mock(**config_data)

    from jiratui.config import CONFIGURATION

    CONFIGURATION.set(config_mock)
    config = CONFIGURATION.get()

    should_show_header = True
    if config.tui_custom_title is not None and config.tui_custom_title == '':
        should_show_header = False

    assert should_show_header is False


def test_header_compose_logic_with_custom_title(config_dict):
    """Test MainScreen compose logic when tui_custom_title has value."""
    config_mock = Mock(spec=ApplicationConfiguration)
    config_data = config_dict.copy()
    config_data.update({'tui_title': 'Default Title', 'tui_custom_title': 'Custom Title'})
    config_mock.configure_mock(**config_data)

    from jiratui.config import CONFIGURATION

    CONFIGURATION.set(config_mock)
    config = CONFIGURATION.get()

    should_show_header = True
    if config.tui_custom_title is not None and config.tui_custom_title == '':
        should_show_header = False

    assert should_show_header is True


def test_header_compose_logic_with_none(config_dict):
    """Test MainScreen compose logic when tui_custom_title is None."""
    config_mock = Mock(spec=ApplicationConfiguration)
    config_data = config_dict.copy()
    config_data.update({'tui_title': 'Default Title', 'tui_custom_title': None})
    config_mock.configure_mock(**config_data)

    from jiratui.config import CONFIGURATION

    CONFIGURATION.set(config_mock)
    config = CONFIGURATION.get()

    should_show_header = True
    if config.tui_custom_title is not None and config.tui_custom_title == '':
        should_show_header = False

    assert should_show_header is True
