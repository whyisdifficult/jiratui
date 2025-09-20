from unittest.mock import Mock

import pytest

from jiratui.api.api import JiraAPI, JiraAPIv2
from jiratui.api_controller.controller import APIController
from jiratui.config import ApplicationConfiguration


@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
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
        log_file='',  # empty filename disables logging to a text file
        log_level='ERROR',
    )
    return config_mock


@pytest.fixture
def jira_api_controller() -> APIController:
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
        log_level='ERROR',
        search_issues_default_day_interval=15,
    )
    return APIController(config_mock)


@pytest.fixture
def jira_api() -> JiraAPI:
    return JiraAPI('https://foo.bar', 'foo', 'bar')


@pytest.fixture
def jira_api_v2() -> JiraAPIv2:
    return JiraAPIv2('https://foo.bar', 'foo', 'bar')
