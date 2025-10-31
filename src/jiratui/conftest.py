from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock

from pydantic import SecretStr
import pytest

from jiratui.api.api import JiraAPI, JiraAPIv2, JiraDataCenterAPI
from jiratui.api_controller.controller import APIController
from jiratui.app import JiraApp
from jiratui.config import ApplicationConfiguration
from jiratui.models import (
    Attachment,
    IssueStatus,
    IssueType,
    JiraIssue,
    JiraUser,
    JiraWorklog,
    Project,
    WorkItemsSearchOrderBy,
)


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
        search_on_startup=False,
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
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
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
def jira_worklogs() -> list[JiraWorklog]:
    return [
        JiraWorklog(
            id='1',
            issue_id='key-2',
            started=datetime(2025, 10, 18, 13, 45, 0, tzinfo=timezone.utc),
            time_spent='1h',
            time_spent_seconds=3600,
            author=Mock(spec=JiraUser),
            update_author=Mock(spec=JiraUser),
            comment='-',
        ),
        JiraWorklog(
            id='2',
            issue_id='key-2',
            started=datetime(2025, 10, 19, 13, 45, 0, tzinfo=timezone.utc),
            time_spent='1h',
            time_spent_seconds=3600,
            author=Mock(spec=JiraUser),
            update_author=Mock(spec=JiraUser),
            comment='-',
        ),
    ]


@pytest.fixture
def jira_issues() -> list[JiraIssue]:
    return [
        JiraIssue(
            id='1',
            key='key-1',
            summary='abcd',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
            edit_meta={
                'fields': {
                    'customfield_10021': {
                        'required': False,
                        'schema': {
                            'type': 'array',
                            'items': 'option',
                            'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                            'customId': 10021,
                        },
                        'name': 'Flagged',
                        'key': 'customfield_10021',
                        'operations': ['add', 'set', 'remove'],
                        'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
                    },
                }
            },
        ),
        JiraIssue(
            id='2',
            key='key-2',
            summary='qwerty',
            status=IssueStatus(name='Done', id='3'),
            issue_type=IssueType(id='2', name='Bug'),
            project=Project(id='1', name='Project 1', key='P1'),
            created=datetime(2025, 10, 11),
            updated=datetime(2025, 10, 11),
            edit_meta={
                'fields': {
                    'customfield_10021': {
                        'required': False,
                        'schema': {
                            'type': 'array',
                            'items': 'option',
                            'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                            'customId': 10021,
                        },
                        'name': 'Flagged',
                        'key': 'customfield_10021',
                        'operations': ['add', 'set', 'remove'],
                        'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
                    },
                }
            },
            attachments=[
                Attachment(
                    id='1',
                    filename='file-one.csv',
                    mime_type='text/csv',
                    size=10,
                    created=datetime(2025, 10, 11),
                    author=JiraUser(
                        account_id='12345',
                        active=True,
                        display_name='Bart',
                        email='bart@simpson.com',
                        username='bart',
                    ),
                ),
                Attachment(
                    id='2',
                    filename='file-two.txt',
                    mime_type='text/plain',
                    size=10,
                    created=datetime(2025, 10, 11),
                    author=JiraUser(
                        account_id='12345',
                        active=True,
                        display_name='Bart',
                        email='bart@simpson.com',
                        username='bart',
                    ),
                ),
                Attachment(
                    id='3',
                    filename='file-three.xml',
                    mime_type='application/xml',
                    size=10,
                    created=datetime(2025, 10, 11),
                    author=JiraUser(
                        account_id='12345',
                        active=True,
                        display_name='Bart',
                        email='bart@simpson.com',
                        username='bart',
                    ),
                ),
                Attachment(
                    id='4',
                    filename='file-four.md',
                    mime_type='text/markdown',
                    size=10,
                    created=datetime(2025, 10, 11),
                    author=JiraUser(
                        account_id='12345',
                        active=True,
                        display_name='Bart',
                        email='bart@simpson.com',
                        username='bart',
                    ),
                ),
                Attachment(
                    id='5',
                    filename='file-five.abc',
                    mime_type='text/abc',
                    size=10,
                    created=datetime(2025, 10, 11),
                    author=JiraUser(
                        account_id='12345',
                        active=True,
                        display_name='Bart',
                        email='bart@simpson.com',
                        username='bart',
                    ),
                ),
            ],
        ),
    ]
