from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api_controller.controller import APIController, APIControllerResponse
from src.app import JiraApp
from src.config import ApplicationConfiguration
from src.models import JiraServerInfo


# TODO extract and reuse
@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
    return MagicMock(
        spec=ApplicationConfiguration(
            jira_api_username='foo',
            jira_api_token='12345',
            jira_api_base_url='foo.bar',
            jira_user_group_id='qwerty',
            tui_title=None,
            tui_title_include_jira_server_title=False,
        )
    )


@pytest.fixture
def api(config_for_testing) -> APIController:
    return APIController(config_for_testing)


@pytest.fixture()
def app(config_for_testing, api) -> JiraApp:
    app = JiraApp(config_for_testing)
    app.api = api
    app._setup_logging = MagicMock()
    return app


@patch('src.widgets.screens.MainScreen.get_users')
@patch('src.widgets.screens.MainScreen.fetch_statuses')
@patch('src.widgets.screens.MainScreen.fetch_issue_types')
@patch('src.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    config_for_testing,
    app,
):
    config_for_testing.tui_title = ''
    config_for_testing.tui_title_include_jira_server_title = False
    async with app.run_test() as pilot:
        assert pilot.app.title == 'Jira TUI'


@patch('src.widgets.screens.MainScreen.get_users')
@patch('src.widgets.screens.MainScreen.fetch_statuses')
@patch('src.widgets.screens.MainScreen.fetch_issue_types')
@patch('src.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title_with_custom_title(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    config_for_testing,
    app,
):
    config_for_testing.tui_title = 'Hello World!'
    config_for_testing.tui_title_include_jira_server_title = False
    async with app.run_test() as pilot:
        assert pilot.app.title == 'Hello World!'


@patch('src.widgets.screens.APIController.server_info')
@patch('src.widgets.screens.MainScreen.get_users')
@patch('src.widgets.screens.MainScreen.fetch_statuses')
@patch('src.widgets.screens.MainScreen.fetch_issue_types')
@patch('src.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title_without_custom_title_with_server_info(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    server_info_mock: AsyncMock,
    config_for_testing,
    app,
):
    config_for_testing.tui_title = None
    config_for_testing.tui_title_include_jira_server_title = True
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
        assert pilot.app.title == 'Jira TUI - my title'


@patch('src.widgets.screens.APIController.server_info')
@patch('src.widgets.screens.MainScreen.get_users')
@patch('src.widgets.screens.MainScreen.fetch_statuses')
@patch('src.widgets.screens.MainScreen.fetch_issue_types')
@patch('src.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_application_title_with_custom_title_with_server_info(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    server_info_mock: AsyncMock,
    config_for_testing,
    app,
):
    config_for_testing.tui_title = 'Hello World!'
    config_for_testing.tui_title_include_jira_server_title = True
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
