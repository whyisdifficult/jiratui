from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

import pytest

from src.jiratui.api.api import JiraAPI
from src.jiratui.api_controller.controller import APIController, APIControllerResponse
from src.jiratui.config import ApplicationConfiguration
from src.jiratui.models import IssueStatus, IssueType, JiraUser, Project


# TODO extract and reuse: see src.tests.test_main_screen.py
@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
    return ApplicationConfiguration(
        jira_api_username='foo',
        jira_api_token='12345',
        jira_api_base_url='foo.bar',
        jira_user_group_id='qwerty',
    )


@pytest.fixture
def api() -> JiraAPI:
    return JiraAPI('', '', '')


@pytest.fixture
def jira_api_controller(config_for_testing) -> APIController:
    return APIController(config_for_testing)


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_project')
async def test_get_project(get_project_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    get_project_mock.return_value = {'id': '123', 'name': 'a', 'key': '1'}
    # WHEN
    response = await jira_api_controller.get_project('1')
    # THEN
    assert response == APIControllerResponse(
        success=True, result=Project(id='123', name='a', key='1'), error=None
    )
    get_project_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_project')
async def test_get_project_with_error(get_project_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    get_project_mock.side_effect = ValueError('testing an error')
    # WHEN
    response = await jira_api_controller.get_project('1')
    # THEN
    assert response == APIControllerResponse(success=False, result=None, error='testing an error')
    get_project_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'search_projects')
async def test_search_projects(search_projects_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    search_projects_mock.side_effect = [
        {'values': [{'id': '123', 'name': 'a', 'key': '1'}], 'isLast': False},
        ValueError('some error'),
    ]
    # WHEN
    response = await jira_api_controller.search_projects('query1')
    # THEN
    assert response == APIControllerResponse(
        success=True, result=[Project(id='123', name='a', key='1')], error='some error'
    )
    search_projects_mock.assert_has_calls(
        [
            call(offset=0, limit=100, query='query1', order_by=None, keys=None),
            call(offset=100, limit=100, query='query1', order_by=None, keys=None),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'search_projects')
async def test_search_projects_multiple_successful_requests(
    search_projects_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    search_projects_mock.side_effect = [
        {'values': [{'id': '123', 'name': 'a', 'key': '1'}], 'isLast': False},
        {'values': [{'id': '456', 'name': 'b', 'key': '2'}], 'isLast': True},
    ]
    # WHEN
    response = await jira_api_controller.search_projects('query1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[Project(id='123', name='a', key='1'), Project(id='456', name='b', key='2')],
        error=None,
    )
    search_projects_mock.assert_has_calls(
        [
            call(offset=0, limit=100, query='query1', order_by=None, keys=None),
            call(offset=100, limit=100, query='query1', order_by=None, keys=None),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'search_projects')
async def test_search_projects_all_requests_raise_error(
    search_projects_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    search_projects_mock.side_effect = [
        ValueError('some error 1'),
    ]
    # WHEN
    response = await jira_api_controller.search_projects('query1')
    # THEN
    assert response == APIControllerResponse(success=True, result=[], error='some error 1')
    search_projects_mock.assert_has_calls(
        [
            call(offset=0, limit=100, query='query1', order_by=None, keys=None),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'status')
async def test_status(status_mock: Mock, jira_api_controller: APIController):
    status_mock.return_value = [{'id': 1, 'name': 'To Do', 'description': 'some description'}]
    response = await jira_api_controller.status()
    assert response == APIControllerResponse(
        success=True,
        result=[IssueStatus(id=1, name='To Do', description='some description')],
        error=None,
    )
    status_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'status')
async def test_status_with_error(status_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    status_mock.side_effect = ValueError('testing an error')
    # WHEN
    response = await jira_api_controller.status()
    # THEN
    assert response == APIControllerResponse(success=False, result=None, error='testing an error')
    status_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_users_in_group')
async def test_list_active_users_in_group(
    get_users_in_group_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_users_in_group_mock.side_effect = [
        {
            'values': [
                {
                    'accountId': '123',
                    'emailAddress': 'a@a.com',
                    'displayName': 'john',
                    'active': True,
                }
            ],
            'isLast': False,
        },
        ValueError('some error'),
    ]
    # WHEN
    response = await jira_api_controller.list_all_active_users_in_group('1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[JiraUser(account_id='123', email='a@a.com', display_name='john', active=True)],
        error='some error',
    )
    get_users_in_group_mock.assert_has_calls(
        [
            call(group_id='1', offset=0, limit=50),
            call(group_id='1', offset=50, limit=50),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_users_in_group')
async def test_list_active_users_in_group_sorted_results(
    get_users_in_group_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_users_in_group_mock.side_effect = [
        {
            'values': [
                {
                    'accountId': '123',
                    'emailAddress': 'a@a.com',
                    'displayName': 'john',
                    'active': True,
                }
            ],
            'isLast': False,
        },
        {
            'values': [
                {
                    'accountId': '456',
                    'emailAddress': 'b@b.com',
                    'displayName': 'homer',
                    'active': True,
                }
            ],
            'isLast': True,
        },
    ]
    # WHEN
    response = await jira_api_controller.list_all_active_users_in_group('1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(account_id='456', email='b@b.com', display_name='homer', active=True),
            JiraUser(account_id='123', email='a@a.com', display_name='john', active=True),
        ],
        error=None,
    )
    get_users_in_group_mock.assert_has_calls(
        [
            call(group_id='1', offset=0, limit=50),
            call(group_id='1', offset=50, limit=50),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_users_in_group')
async def test_list_active_users_in_group_ignore_inactive_users(
    get_users_in_group_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_users_in_group_mock.side_effect = [
        {
            'values': [
                {
                    'accountId': '123',
                    'emailAddress': 'a@a.com',
                    'displayName': 'john',
                    'active': False,
                }
            ],
            'isLast': False,
        },
        {
            'values': [
                {
                    'accountId': '456',
                    'emailAddress': 'b@b.com',
                    'displayName': 'homer',
                    'active': True,
                }
            ],
            'isLast': True,
        },
    ]
    # WHEN
    response = await jira_api_controller.list_all_active_users_in_group('1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(account_id='456', email='b@b.com', display_name='homer', active=True),
        ],
        error=None,
    )
    get_users_in_group_mock.assert_has_calls(
        [
            call(group_id='1', offset=0, limit=50),
            call(group_id='1', offset=50, limit=50),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_users_in_group')
async def test_list_active_users_in_group_ignore_users_without_email_and_name(
    get_users_in_group_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_users_in_group_mock.side_effect = [
        {
            'values': [
                {
                    'accountId': '123',
                    'emailAddress': 'a@a.com',
                    'displayName': 'john',
                    'active': True,
                }
            ],
            'isLast': False,
        },
        {
            'values': [{'accountId': '456', 'emailAddress': '', 'displayName': '', 'active': True}],
            'isLast': True,
        },
    ]
    # WHEN
    response = await jira_api_controller.list_all_active_users_in_group('1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(account_id='123', email='a@a.com', display_name='john', active=True),
        ],
        error=None,
    )
    get_users_in_group_mock.assert_has_calls(
        [
            call(group_id='1', offset=0, limit=50),
            call(group_id='1', offset=50, limit=50),
        ],
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_project_statuses')
async def test_get_project_statuses(
    get_project_statuses_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_project_statuses_mock.return_value = [
        {
            'id': '1',
            'name': 'a',
            'statuses': [
                {
                    'id': '1',
                    'name': 'name 1',
                    'description': 'd1',
                }
            ],
        },
        {'id': '2', 'name': 'b', 'statuses': []},
    ]
    # WHEN
    response = await jira_api_controller.get_project_statuses('PK1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result={
            '1': {
                'issue_type_name': 'a',
                'issue_type_statuses': [IssueStatus(id=1, name='name 1', description='d1')],
            },
            '2': {
                'issue_type_name': 'b',
                'issue_type_statuses': [],
            },
        },
        error=None,
    )
    get_project_statuses_mock.assert_called_once_with('PK1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_project_statuses')
async def test_get_project_statuses_with_error(
    get_project_statuses_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_project_statuses_mock.side_effect = ValueError('testing an error')
    # WHEN
    response = await jira_api_controller.get_project_statuses('PK1')
    # THEN
    assert response == APIControllerResponse(success=False, result=None, error='testing an error')
    get_project_statuses_mock.assert_called_once_with('PK1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_project')
async def test_get_issue_types_for_project(
    get_project_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_project_mock.return_value = {
        'issueTypes': [{'id': '1', 'name': 'Task'}, {'id': '2', 'name': 'Bug'}]
    }
    # WHEN
    response = await jira_api_controller.get_issue_types_for_project('PK1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            IssueType(id=1, name='Task'),
            IssueType(id=2, name='Bug'),
        ],
        error=None,
    )
    get_project_mock.assert_called_once_with('PK1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_project')
async def test_get_issue_types_for_project_with_exception(
    get_project_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_project_mock.side_effect = ValueError('test error')
    # WHEN
    response = await jira_api_controller.get_issue_types_for_project('PK1')
    # THEN
    assert response == APIControllerResponse(
        success=False,
        result=None,
        error='test error',
    )
    get_project_mock.assert_called_once_with('PK1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_search')
async def test_search_users(user_search_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    user_search_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users('john')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
            JiraUser(
                email='b@b.com',
                account_id='456',
                active=False,
                display_name='homer',
            ),
        ],
        error=None,
    )
    user_search_mock.assert_called_once_with(query='john')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_search')
async def test_search_users_skip_users_without_email(
    user_search_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    user_search_mock.return_value = [
        {'accountId': '123', 'emailAddress': '', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users('john')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='b@b.com',
                account_id='456',
                active=False,
                display_name='homer',
            ),
        ],
        error=None,
    )
    user_search_mock.assert_called_once_with(query='john')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_search')
async def test_search_users_include_users_without_email(
    user_search_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    jira_api_controller.skip_users_without_email = False
    user_search_mock.return_value = [
        {'accountId': '123', 'emailAddress': '', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users('john')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='',
                account_id='123',
                active=True,
                display_name='john',
            ),
            JiraUser(
                email='b@b.com',
                account_id='456',
                active=False,
                display_name='homer',
            ),
        ],
        error=None,
    )
    user_search_mock.assert_called_once_with(query='john')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_search')
async def test_search_users_with_exception(
    user_search_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    user_search_mock.side_effect = ValueError('test error')
    # WHEN
    response = await jira_api_controller.search_users('john')
    # THEN
    assert response == APIControllerResponse(
        success=False,
        result=None,
        error='test error',
    )
    user_search_mock.assert_called_once_with(query='john')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_search')
async def test_search_users_assignable_to_issue(
    user_assignable_search_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    user_assignable_search_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_issue('key1')
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
        ],
        error=None,
    )
    user_assignable_search_mock.assert_called_once_with(
        issue_key='key1',
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_search')
async def test_search_users_assignable_to_issue_active_and_non_active_users(
    user_assignable_search_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    user_assignable_search_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_issue('key1', active=None)
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='b@b.com',
                account_id='456',
                active=False,
                display_name='homer',
            ),
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
        ],
        error=None,
    )
    user_assignable_search_mock.assert_called_once_with(
        issue_key='key1',
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_search')
async def test_search_users_assignable_to_issue_include_users_without_email(
    user_assignable_search_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    jira_api_controller.skip_users_without_email = False
    user_assignable_search_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': '', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_issue('key1', active=None)
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='',
                account_id='456',
                active=False,
                display_name='homer',
            ),
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
        ],
        error=None,
    )
    user_assignable_search_mock.assert_called_once_with(
        issue_key='key1',
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_search')
async def test_search_users_assignable_to_issue_with_exception(
    user_assignable_search_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    user_assignable_search_mock.side_effect = ValueError('test error')
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_issue('key1')
    # THEN
    assert response == APIControllerResponse(
        success=False,
        result=None,
        error='test error',
    )
    user_assignable_search_mock.assert_called_once_with(
        issue_key='key1',
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_multi_projects')
async def test_search_users_assignable_to_projects(
    user_assignable_multi_projects_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    user_assignable_multi_projects_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_projects(
        project_keys=['key1', 'key2']
    )
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
        ],
        error=None,
    )
    user_assignable_multi_projects_mock.assert_called_once_with(
        project_keys=['key1', 'key2'],
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_multi_projects')
async def test_search_users_assignable_to_projects_active_and_non_active_users(
    user_assignable_multi_projects_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    user_assignable_multi_projects_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': 'b@b.com', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_projects(
        project_keys=['key1', 'key2'], active=None
    )
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='b@b.com',
                account_id='456',
                active=False,
                display_name='homer',
            ),
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
        ],
        error=None,
    )
    user_assignable_multi_projects_mock.assert_called_once_with(
        project_keys=['key1', 'key2'],
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_multi_projects')
async def test_search_users_assignable_to_projects_include_users_without_email(
    user_assignable_multi_projects_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    jira_api_controller.skip_users_without_email = False
    user_assignable_multi_projects_mock.return_value = [
        {'accountId': '123', 'emailAddress': 'a@a.com', 'displayName': 'john', 'active': True},
        {'accountId': '456', 'emailAddress': '', 'displayName': 'homer', 'active': False},
    ]
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_projects(
        project_keys=['key1', 'key2'], active=None
    )
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            JiraUser(
                email='',
                account_id='456',
                active=False,
                display_name='homer',
            ),
            JiraUser(
                email='a@a.com',
                account_id='123',
                active=True,
                display_name='john',
            ),
        ],
        error=None,
    )
    user_assignable_multi_projects_mock.assert_called_once_with(
        project_keys=['key1', 'key2'],
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'user_assignable_multi_projects')
async def test_search_users_assignable_to_projects_with_exception(
    user_assignable_multi_projects_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    user_assignable_multi_projects_mock.side_effect = ValueError('test error')
    # WHEN
    response = await jira_api_controller.search_users_assignable_to_projects(
        project_keys=['key1', 'key2']
    )
    # THEN
    assert response == APIControllerResponse(
        success=False,
        result=None,
        error='test error',
    )
    user_assignable_multi_projects_mock.assert_called_once_with(
        project_keys=['key1', 'key2'],
        query=None,
        offset=0,
        limit=1000,
    )


@pytest.mark.parametrize(
    'project_key, created_from, created_until, status, assignee, issue_type, jql_query, expected_criteria',
    [
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        ('', None, None, None, '', None, 'key=value ', {'jql': 'key=value', 'updated_from': None}),
        ('PR1', None, None, None, '', None, '', {}),
    ],
)
def test_build_criteria_for_searching_work_items(
    project_key,
    created_from,
    created_until,
    status,
    assignee,
    issue_type,
    jql_query,
    expected_criteria,
    jira_api_controller: APIController,
):
    # WHEN
    criteria = jira_api_controller._build_criteria_for_searching_work_items(
        project_key=project_key,
        created_from=created_from,
        created_until=created_until,
        status=status,
        assignee=assignee,
        issue_type=issue_type,
        jql_query=jql_query,
    )
    # THEN
    assert criteria == expected_criteria


@pytest.mark.parametrize(
    'project_key, created_from, created_until, status, assignee, issue_type, jql_query, expression_id, pre_defined_jql_expressions, expected_criteria',
    [
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            1,
            None,
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            None,
            {1: {'expression': 'key=value'}},
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            None,
            None,
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            1,
            {2: {'expression': 'key=value'}},
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            1,
            {1: {'expression': ''}},
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            1,
            {1: {'expression': ' '}},
            {'jql': None, 'updated_from': datetime.now().date() - timedelta(days=15)},
        ),
        (
            '',
            None,
            None,
            None,
            '',
            None,
            '',
            1,
            {1: {'expression': 'key1=value\n\nAND key2=value '}},
            {'jql': 'key1=value  AND key2=value', 'updated_from': None},
        ),
    ],
)
def test_build_criteria_for_searching_work_items_with_config_values(
    project_key,
    created_from,
    created_until,
    status,
    assignee,
    issue_type,
    jql_query,
    expression_id,
    pre_defined_jql_expressions,
    expected_criteria,
    jira_api_controller: APIController,
):
    # GIVEN
    jira_api_controller.config.jql_expression_id_for_work_items_search = expression_id
    jira_api_controller.config.pre_defined_jql_expressions = pre_defined_jql_expressions
    # WHEN
    criteria = jira_api_controller._build_criteria_for_searching_work_items(
        project_key=project_key,
        created_from=created_from,
        created_until=created_until,
        status=status,
        assignee=assignee,
        issue_type=issue_type,
        jql_query=jql_query,
    )
    # THEN
    assert criteria == expected_criteria
