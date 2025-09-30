from unittest.mock import Mock

from pydantic import SecretStr
import pytest

from jiratui.api.api import JiraAPI, JiraAPIv2, JiraDataCenterAPI
from jiratui.api_controller.controller import APIController
from jiratui.config import ApplicationConfiguration
from jiratui.models import IssueStatus, IssueType, JiraIssue


@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
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
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',  # empty filename disables logging to a text file
        log_level='ERROR',
        ssl=None,
    )
    return config_mock


@pytest.fixture
def config_for_testing_jira_dc() -> ApplicationConfiguration:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token=SecretStr('bar'),
        jira_api_version=3,
        use_bearer_authentication=False,
        cloud=False,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',  # empty filename disables logging to a text file
        log_level='ERROR',
        ssl=None,
    )
    return config_mock


@pytest.fixture
def jira_api_controller() -> APIController:
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
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='ERROR',
        search_issues_default_day_interval=15,
        ssl=None,
    )
    return APIController(config_mock)


@pytest.fixture
def jira_api_controller_for_jira_dc() -> APIController:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token=SecretStr('bar'),
        jira_api_version=3,
        use_bearer_authentication=False,
        cloud=False,
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
        ssl=None,
    )
    return APIController(config_mock)


@pytest.fixture
def jira_api(config_for_testing) -> JiraAPI:
    return JiraAPI('https://foo.bar', 'foo', 'bar', config_for_testing)


@pytest.fixture
def jira_api_v2(config_for_testing) -> JiraAPIv2:
    return JiraAPIv2('https://foo.bar', 'foo', 'bar', config_for_testing)


@pytest.fixture
def jira_api_dc(config_for_testing_jira_dc) -> JiraDataCenterAPI:
    return JiraDataCenterAPI('https://foo.bar', 'foo', 'bar', config_for_testing_jira_dc)


@pytest.fixture
def jira_issues() -> list[JiraIssue]:
    return [
        JiraIssue(
            id='1',
            key='key-1',
            summary='abcd',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
        ),
        JiraIssue(
            id='2',
            key='key-2',
            summary='qwerty',
            status=IssueStatus(name='Done', id='3'),
            issue_type=IssueType(id='2', name='Bug'),
        ),
    ]
