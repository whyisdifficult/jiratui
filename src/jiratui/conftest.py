import pytest

from jiratui.api.api import JiraAPI
from jiratui.api_controller.controller import APIController
from jiratui.config import ApplicationConfiguration


@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
    return ApplicationConfiguration(
        jira_api_username='foo',
        jira_api_token='12345',
        jira_api_base_url='foo.bar',
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
    )


@pytest.fixture
def jira_api_controller(config_for_testing) -> APIController:
    return APIController(config_for_testing)


@pytest.fixture
def jira_api() -> JiraAPI:
    return JiraAPI('https://foo.bar', 'foo', 'bar')
