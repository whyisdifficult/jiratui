from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

import pytest

from jiratui.api.api import JiraAPI
from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.exceptions import (
    ServiceInvalidResponseException,
    ServiceUnavailableException,
    UpdateWorkItemException,
    ValidationError,
)
from jiratui.models import (
    Attachment,
    IssueComment,
    IssueRemoteLink,
    IssueStatus,
    IssueTransition,
    IssueTransitionState,
    IssueType,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraMyselfInfo,
    JiraServerInfo,
    JiraUser,
    JiraUserGroup,
    LinkIssueType,
    Project,
    UpdateWorkItemResponse,
)
from jiratui.utils.test_utilities import load_json_response


@pytest.fixture
def transitions() -> list[IssueTransition]:
    return [
        IssueTransition(
            id='1',
            name='To Do',
            to_state=IssueTransitionState(
                id='3',
                name='To Do',
                description='a task to do',
            ),
        ),
        IssueTransition(
            id='2',
            name='Done',
            to_state=IssueTransitionState(
                id='4',
                name='To Do',
                description='a task done',
            ),
        ),
    ]


@pytest.fixture
def work_item() -> JiraIssue:
    return Mock(spec=JiraIssue)


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
        result=[IssueStatus(id='1', name='To Do', description='some description')],
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
                'issue_type_statuses': [IssueStatus(id='1', name='name 1', description='d1')],
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
            IssueType(id='1', name='Task'),
            IssueType(id='2', name='Bug'),
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
async def test_search_users_assignable_to_issue_skip_users_without_email(
    user_assignable_search_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    jira_api_controller.skip_users_without_email = True
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
async def test_search_users_assignable_to_projects_skip_users_without_email(
    user_assignable_multi_projects_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    jira_api_controller.skip_users_without_email = True
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


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_issue')
async def test_get_issue(
    get_issue_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_mock.return_value = load_json_response(__file__, 'issue.json')
    # WHEN
    response = await jira_api_controller.get_issue('10002')
    # THEN
    assert response.success is True
    assert isinstance(response.result.issues[0], JiraIssue)
    assert isinstance(response.result, JiraIssueSearchResponse)
    assert response.result.next_page_token is None
    assert response.result.is_last is None
    assert response.result.issues[0].id == '10002'
    assert response.result.issues[0].key == 'SCRUM-10'
    assert response.result.issues[0].summary == '(Sample) Set Up Payment Logging'
    assert response.result.issues[0].status == IssueStatus(
        name='In Progress',
        id='10001',
    )
    assert response.result.issues[0].project == Project(
        id='10000', name='Test Project', key='SCRUM'
    )
    assert response.result.issues[0].created == datetime(2025, 7, 5, 14, 34, 59)
    assert response.result.issues[0].updated == datetime(2025, 7, 14, 22, 33, 38)
    assert response.result.issues[0].due_date == datetime(2025, 12, 31).date()
    assert response.result.issues[0].reporter == JiraUser(
        account_id='abe10be',
        active=True,
        display_name='Bart',
        email='bart@simpson.com',
    )
    assert response.result.issues[0].issue_type == IssueType(
        id='10003', name='Task', scope_project=None
    )
    assert response.result.issues[0].description == {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': 'Create a logging system to store payment transaction metadata.',
                    }
                ],
            }
        ],
    }
    assert response.result.issues[0].attachments == [
        Attachment(
            id='2',
            filename='foo.txt',
            size=1000,
            created=datetime(2025, 12, 31),
            mime_type='text',
            author=JiraUser(
                account_id='1',
                active=True,
                display_name='John Doe',
                email='foo@bar',
            ),
        )
    ]
    get_issue_mock.assert_has_calls(
        [
            call(issue_id_or_key='10002', fields=None, properties=None),
        ],
    )


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_issue')
async def test_get_issue_with_api_error(
    get_issue_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_mock.side_effect = ValueError('an error')
    # WHEN
    response = await jira_api_controller.get_issue('10002')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.result is None
    assert response.error == 'Failed to retrieve the work item 10002: an error.'


@pytest.mark.asyncio
@patch('jiratui.api_controller.controller.build_issue_instance')
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_issue')
async def test_get_issue_with_instance_building_error(
    get_issue_mock: Mock,
    configuration_mock: Mock,
    build_issue_instance_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_issue_mock.return_value = load_json_response(__file__, 'issue.json')
    build_issue_instance_mock.side_effect = ValueError('another error')
    # WHEN
    response = await jira_api_controller.get_issue('10002')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.result is None
    assert (
        response.error
        == 'Failed to extract the details of the requested work item 10002: another error'
    )


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_issue')
async def test_get_issue_with_additional_parameters(
    get_issue_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_mock.return_value = load_json_response(__file__, 'issue.json')
    # WHEN
    response = await jira_api_controller.get_issue('10002', fields=['f1', 'f2'], properties='p1,p2')
    # THEN
    assert response.success is True
    assert isinstance(response.result.issues[0], JiraIssue)
    assert isinstance(response.result, JiraIssueSearchResponse)
    assert response.result.next_page_token is None
    assert response.result.is_last is None
    get_issue_mock.assert_has_calls(
        [
            call(issue_id_or_key='10002', fields='f1,f2', properties='p1,p2'),
        ],
    )


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_groups_in_bulk')
async def test_find_groups(
    get_groups_in_bulk_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_groups_in_bulk_mock.return_value = {
        'values': [{'groupId': '5', 'name': 'g1'}, {'groupId': '6', 'name': 'g2'}]
    }
    # WHEN
    response = await jira_api_controller.find_groups(
        2, limit=5, groups_ids=['5,,6'], groups_names=['g1', 'g2']
    )
    # THEN
    assert response.success is True
    assert isinstance(response.result, list)
    assert isinstance(response.result[0], JiraUserGroup)
    get_groups_in_bulk_mock.assert_has_calls(
        [
            call(offset=2, limit=5, groups_ids=['5,,6'], groups_names=['g1', 'g2']),
        ],
    )


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_groups_in_bulk')
async def test_find_groups_with_api_error(
    get_groups_in_bulk_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_groups_in_bulk_mock.side_effect = ValueError('an error')
    # WHEN
    response = await jira_api_controller.find_groups(
        2, limit=5, groups_ids=['5,,6'], groups_names=['g1', 'g2']
    )
    # THEN
    assert response.success is False
    assert response.result is None
    assert response.error == 'an error'
    get_groups_in_bulk_mock.assert_has_calls(
        [
            call(offset=2, limit=5, groups_ids=['5,,6'], groups_names=['g1', 'g2']),
        ],
    )


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_users_in_group')
async def test_count_users_in_group(
    get_users_in_group_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_users_in_group_mock.return_value = {'total': '5'}
    # WHEN
    response = await jira_api_controller.count_users_in_group('g1')
    # THEN
    assert response.success is True
    assert isinstance(response.result, int)
    assert response.result == 5
    get_users_in_group_mock.assert_has_calls([call(group_id='g1')])


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_users_in_group')
async def test_count_users_in_group_with_api_error(
    get_users_in_group_mock: Mock, configuration_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_users_in_group_mock.side_effect = ValueError('an error')
    # WHEN
    response = await jira_api_controller.count_users_in_group('g1')
    # THEN
    assert response.success is False
    assert response.result is None
    assert response.error == 'an error'
    get_users_in_group_mock.assert_has_calls([call(group_id='g1')])


@pytest.mark.asyncio
@patch.object(APIController, 'search_projects')
@patch.object(JiraAPI, 'get_issue_types_for_user')
async def test_get_issue_types(
    get_issue_types_for_user_mock: Mock,
    search_projects_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_issue_types_for_user_mock.return_value = [
        {'id': '1', 'name': 'Task', 'scope': {'type': 'Project', 'project': {'id': '1'}}},
        {'id': '2', 'name': 'Bug', 'scope': {'type': 'Another', 'project': {'id': '2'}}},
    ]
    search_projects_mock.return_value = APIControllerResponse(
        result=[
            Project(id='1', name='Project 1', key='P1'),
            Project(id='2', name='Project 2', key='P2'),
        ]
    )
    # WHEN
    response = await jira_api_controller.get_issue_types()
    # THEN
    assert response == APIControllerResponse(
        success=True,
        result=[
            IssueType(
                id='1', name='Task', scope_project=Project(id='1', name='Project 1', key='P1')
            ),
            IssueType(id='2', name='Bug', scope_project=None),
        ],
        error=None,
    )
    get_issue_types_for_user_mock.assert_called_once()
    search_projects_mock.assert_called_once()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_types_for_user')
async def test_get_issue_types_with_api_error(
    get_issue_types_for_user_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_types_for_user_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.get_issue_types()
    # THEN
    assert response == APIControllerResponse(success=False, error='some error')
    get_issue_types_for_user_mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'raised_error, expected_error_message',
    [
        (ServiceUnavailableException(), 'Unable to connect to the Jira server.'),
        (ServiceInvalidResponseException(), 'The response from the server contains errors.'),
        (
            ValueError('some error'),
            'There was an unknown error while searching for work items: some error',
        ),
    ],
)
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'search_issues')
async def test_search_issues_with_api_error(
    search_issues_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    raised_error,
    expected_error_message: str,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    search_issues_mock.side_effect = raised_error
    # WHEN
    response = await jira_api_controller.search_issues()
    # THEN
    assert response == APIControllerResponse(success=False, error=expected_error_message)
    build_criteria_for_searching_work_items_mock.assert_called_once()
    search_issues_mock.assert_called_once()


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'search_issues')
async def test_search_issues(
    search_issues_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    configuration_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    search_issues_mock.return_value = {'issues': [load_json_response(__file__, 'issue.json')]}
    # WHEN
    response = await jira_api_controller.search_issues()
    # THEN
    assert response.success is True
    assert response.error is None
    assert isinstance(response.result, JiraIssueSearchResponse)
    assert response.result.is_last is None
    assert response.result.next_page_token is None
    assert response.result.issues[0].id == '10002'
    assert response.result.issues[0].key == 'SCRUM-10'
    assert response.result.issues[0].summary == '(Sample) Set Up Payment Logging'
    assert response.result.issues[0].status == IssueStatus(
        name='In Progress',
        id='10001',
    )
    assert response.result.issues[0].project == Project(
        id='10000', name='Test Project', key='SCRUM'
    )
    assert response.result.issues[0].created == datetime(2025, 7, 5, 14, 34, 59)
    assert response.result.issues[0].updated == datetime(2025, 7, 14, 22, 33, 38)
    assert response.result.issues[0].due_date == datetime(2025, 12, 31).date()
    assert response.result.issues[0].reporter == JiraUser(
        account_id='abe10be',
        active=True,
        display_name='Bart',
        email='bart@simpson.com',
    )
    assert response.result.issues[0].issue_type == IssueType(
        id='10003', name='Task', scope_project=None
    )
    assert response.result.issues[0].description == {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': 'Create a logging system to store payment transaction metadata.',
                    }
                ],
            }
        ],
    }
    assert response.result.issues[0].attachments == [
        Attachment(
            id='2',
            filename='foo.txt',
            size=1000,
            created=datetime(2025, 12, 31),
            mime_type='text',
            author=JiraUser(
                account_id='1',
                active=True,
                display_name='John Doe',
                email='foo@bar',
            ),
        )
    ]
    build_criteria_for_searching_work_items_mock.assert_called_once()
    search_issues_mock.assert_called_once()


@pytest.mark.asyncio
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'search_issues')
async def test_search_issues_with_next_page(
    search_issues_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    search_issues_mock.return_value = {
        'issues': [load_json_response(__file__, 'issue.json')],
        'nextPageToken': 't1',
        'isLast': False,
    }
    # WHEN
    response = await jira_api_controller.search_issues()
    # THEN
    assert response.success is True
    assert response.error is None
    assert isinstance(response.result, JiraIssueSearchResponse)
    assert response.result.is_last is False
    assert response.result.next_page_token == 't1'
    build_criteria_for_searching_work_items_mock.assert_called_once()
    search_issues_mock.assert_called_once()


@pytest.mark.asyncio
@patch('jiratui.api_controller.controller.build_issue_instance')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'search_issues')
async def test_search_issues_with_missing_issues(
    search_issues_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    build_issue_instance_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    search_issues_mock.return_value = {
        'issues': [load_json_response(__file__, 'issue.json')],
        'nextPageToken': 't1',
        'isLast': False,
    }
    build_issue_instance_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.search_issues()
    # THEN
    assert response.success is True
    assert response.error is None
    assert isinstance(response.result, JiraIssueSearchResponse)
    assert response.result.is_last is False
    assert response.result.next_page_token == 't1'
    assert response.result.issues == []
    build_criteria_for_searching_work_items_mock.assert_called_once()
    search_issues_mock.assert_called_once()


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'work_items_search_approximate_count')
async def test_count_issues(
    work_items_search_approximate_count_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    configuration_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    work_items_search_approximate_count_mock.return_value = {'count': '5'}
    # WHEN
    response = await jira_api_controller.count_issues()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert isinstance(response.result, int)
    assert response.result == 5
    work_items_search_approximate_count_mock.assert_called_once()


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'work_items_search_approximate_count')
async def test_count_issues_with_api_error(
    work_items_search_approximate_count_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    configuration_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    work_items_search_approximate_count_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.count_issues()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.result is None
    assert response.error == 'Failed to count the number of work items: some error'
    work_items_search_approximate_count_mock.assert_called_once()


@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'work_items_search_approximate_count')
async def test_count_issues_with_criteria(
    work_items_search_approximate_count_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    configuration_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {
        'updated_from': datetime(2025, 12, 31).date(),
        'jql': 'query',
    }
    work_items_search_approximate_count_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.count_issues()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.result is None
    assert response.error == 'Failed to count the number of work items: some error'
    work_items_search_approximate_count_mock.assert_called_once_with(
        project_key=None,
        created_from=None,
        created_until=None,
        updated_from=datetime(2025, 12, 31).date(),
        status=None,
        assignee=None,
        issue_type=None,
        jql_query='query',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_remote_links')
async def test_get_issue_remote_links(
    get_issue_remote_links_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_remote_links_mock.return_value = load_json_response(
        __file__, 'issue_remote_links.json'
    )
    # WHEN
    response = await jira_api_controller.get_issue_remote_links('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert isinstance(response.result, list)
    assert isinstance(response.result[0], IssueRemoteLink)
    assert response.result == [
        IssueRemoteLink(
            id='10000',
            global_id='system=http://www.mycompany.com/support&id=1',
            relationship='causes',
            title='TSTSUP-111',
            summary='Customer support issue',
            url='http://www.mycompany.com/support?id=1',
            application_name='My Acme Tracker',
            status_title=None,
            status_resolved=True,
        ),
        IssueRemoteLink(
            id='10001',
            global_id='system=http://www.anothercompany.com/tester&id=1234',
            relationship='is tested by',
            title='Test Case #1234',
            summary='Test that the submit button saves the item',
            url='http://www.anothercompany.com/tester/testcase/1234',
            application_name='My Acme Tester',
            status_title=None,
            status_resolved=False,
        ),
    ]
    get_issue_remote_links_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_remote_links')
async def test_get_issue_remote_links_with_api_error(
    get_issue_remote_links_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_remote_links_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.get_issue_remote_links('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    get_issue_remote_links_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_issue_remote_link')
async def test_create_issue_remote_link_with_api_error(
    create_issue_remote_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    create_issue_remote_link_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.create_issue_remote_link(
        '1', 'http://www.a.com', 'a title'
    )
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    create_issue_remote_link_mock.assert_called_once_with('1', 'http://www.a.com', 'a title')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_issue_remote_link')
async def test_create_issue_remote_link_with_invalid_url(
    create_issue_remote_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    create_issue_remote_link_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.create_issue_remote_link('1', 'www.a.com', 'a title')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'The url must be a full url including the http:// schema.'
    assert response.result is None
    create_issue_remote_link_mock.assert_not_called()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_issue_remote_link')
async def test_create_issue_remote_link_without_title(
    create_issue_remote_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    create_issue_remote_link_mock.return_value = None
    # WHEN
    response = await jira_api_controller.create_issue_remote_link('1', 'http://www.a.com', '')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result is None
    create_issue_remote_link_mock.assert_called_once_with(
        '1', 'http://www.a.com', 'http://www.a.com'
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_issue_remote_link')
async def test_delete_issue_remote_link(
    delete_issue_remote_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    delete_issue_remote_link_mock.return_value = None
    # WHEN
    response = await jira_api_controller.delete_issue_remote_link('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result is None
    delete_issue_remote_link_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_issue_remote_link')
async def test_delete_issue_remote_link_with_api_error(
    delete_issue_remote_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    delete_issue_remote_link_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.delete_issue_remote_link('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    delete_issue_remote_link_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'server_info')
async def test_server_info(server_info_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    server_info_mock.return_value = {
        'baseUrl': 'url1',
        'displayUrlServicedeskHelpCenter': 'url3',
        'displayUrlConfluence': 'url4',
        'version': '1',
        'deploymentType': 'dev',
        'buildNumber': '2',
        'buildDate': '2025-12-31',
        'serverTime': '10:00',
        'scmInfo': 'info',
        'serverTitle': 'title',
        'serverTimeZone': 'UTC',
        'defaultLocale': {'locale': 'EU'},
    }
    # WHEN
    response = await jira_api_controller.server_info()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == JiraServerInfo(
        base_url='url1',
        display_url_servicedesk_help_center='url3',
        display_url_confluence='url4',
        version='1',
        deployment_type='dev',
        build_number=2,
        build_date='2025-12-31',
        server_time='10:00',
        scm_info='info',
        server_title='title',
        default_locale='EU',
        server_time_zone='UTC',
    )
    server_info_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'server_info')
async def test_server_info_with_api_error(
    server_info_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    server_info_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.server_info()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    server_info_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'myself')
async def test_myself(myself_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    myself_mock.return_value = {
        'accountId': '1',
        'accountType': 'user',
        'active': True,
        'displayName': 'bart',
        'emailAddress': 'bart@simpson.com',
        'groups': {'items': [{'id': '1', 'name': 'g1'}]},
    }
    # WHEN
    response = await jira_api_controller.myself()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == JiraMyselfInfo(
        account_id='1',
        account_type='user',
        active=True,
        display_name='bart',
        email='bart@simpson.com',
        groups=[JiraUserGroup(id='1', name='g1')],
    )
    myself_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'myself')
async def test_myself_with_api_error(myself_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    myself_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.myself()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    myself_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'issue_edit_metadata')
async def test_get_edit_metadata_for_issue(
    issue_edit_metadata_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    issue_edit_metadata_mock.return_value = {'key': 'value'}
    # WHEN
    response = await jira_api_controller.get_edit_metadata_for_issue('1')
    # THEN
    assert isinstance(response, dict)
    assert response == {'key': 'value'}
    issue_edit_metadata_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'issue_edit_metadata')
async def test_get_edit_metadata_for_issue_with_api_error(
    issue_edit_metadata_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    issue_edit_metadata_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.get_edit_metadata_for_issue('1')
    # THEN
    assert isinstance(response, dict)
    assert response == {}
    issue_edit_metadata_mock.assert_called_once_with('1')


@pytest.mark.asyncio
async def test_update_issue_with_missing_edit_meta(
    work_item: JiraIssue, jira_api_controller: APIController
):
    # GIVEN
    work_item.edit_meta = None
    # WHEN/THEN
    with pytest.raises(
        UpdateWorkItemException,
        match='Missing expected metadata.',
    ):
        await jira_api_controller.update_issue(work_item, {})


@pytest.mark.asyncio
async def test_update_issue_with_missing_edit_meta_fields(
    work_item: JiraIssue, jira_api_controller: APIController
):
    # GIVEN
    work_item.edit_meta = {'fields': {}}
    # WHEN/THEN
    with pytest.raises(
        UpdateWorkItemException,
        match='The selected work item does not include the required fields metadata.',
    ):
        await jira_api_controller.update_issue(work_item, {})


@pytest.mark.asyncio
async def test_update_issue_with_missing_summary(
    work_item: JiraIssue, jira_api_controller: APIController
):
    # GIVEN
    work_item.edit_meta = {'fields': {'field': 'value'}}
    # WHEN/THEN
    with pytest.raises(
        ValidationError,
        match='The summary field can not be empty.',
    ):
        await jira_api_controller.update_issue(work_item, {'summary': ' '})


@pytest.mark.asyncio
async def test_update_issue_with_no_updates(
    work_item: JiraIssue, jira_api_controller: APIController
):
    # GIVEN
    work_item.edit_meta = {'fields': {'field': 'value'}}
    # WHEN
    result = await jira_api_controller.update_issue(work_item, {})
    # THEN
    assert result == APIControllerResponse(result=UpdateWorkItemResponse(success=True))


@pytest.mark.parametrize('field_name', ['summary', 'due_date', 'priority', 'assignee_account_id'])
@pytest.mark.asyncio
async def test_update_issue_with_update_fields(
    field_name: str,
    work_item: JiraIssue,
    jira_api_controller: APIController,
):
    # GIVEN
    work_item.edit_meta = {'fields': {'field': 'value'}}
    work_item.key = 'WI1'
    # WHEN/THEN
    with pytest.raises(
        UpdateWorkItemException,
        match=f'The field "{field_name}" can not be updated for the selected work item.',
    ):
        await jira_api_controller.update_issue(work_item, {field_name: 'value'})


@pytest.mark.parametrize(
    'field_name, field_key',
    [
        ('summary', 'summary'),
        ('due_date', 'duedate'),
        ('priority', 'priority'),
        ('assignee_account_id', 'assignee'),
    ],
)
@pytest.mark.asyncio
async def test_update_issue_with_update_fields_no_update_allowed(
    field_name: str,
    field_key: str,
    work_item: JiraIssue,
    jira_api_controller: APIController,
):
    # GIVEN
    work_item.edit_meta = {'fields': {field_key: {'operations': {}}}}
    work_item.key = 'WI1'
    # WHEN/THEN
    with pytest.raises(
        UpdateWorkItemException,
        match=f'The field "{field_key}" can not be updated for the selected work item.',
    ):
        await jira_api_controller.update_issue(work_item, {field_name: 'value'})


@pytest.mark.parametrize(
    'field_name, field_key, updated_fields',
    [
        ('summary', 'summary', ['summary']),
        ('due_date', 'duedate', ['due_date']),
        ('priority', 'priority', ['priority']),
        ('assignee_account_id', 'assignee', ['assignee_account_id']),
    ],
)
@pytest.mark.asyncio
@patch.object(JiraAPI, 'update_issue')
async def test_update_issue_with_update_fields_update_allowed(
    update_issue_mock: Mock,
    field_name: str,
    field_key: str,
    updated_fields: list[str],
    work_item: JiraIssue,
    jira_api_controller: APIController,
):
    # GIVEN
    work_item.edit_meta = {'fields': {field_key: {'operations': {'set': 'new value'}}}}
    work_item.key = 'WI1'
    update_issue_mock.return_value = {'fields': {field_name: 'new value'}}
    # WHEN
    result = await jira_api_controller.update_issue(work_item, {field_name: 'value'})
    # THEN
    assert result == APIControllerResponse(
        result=UpdateWorkItemResponse(success=True, updated_fields=updated_fields)
    )


@pytest.mark.asyncio
async def test_update_issue_with_update_labels(
    work_item: JiraIssue, jira_api_controller: APIController
):
    # GIVEN
    work_item.edit_meta = {'fields': {'summary': {'operations': {}}}}
    work_item.key = 'WI1'
    # WHEN
    result = await jira_api_controller.update_issue(work_item, {'labels': 'value'})
    # THEN
    assert result == APIControllerResponse(result=UpdateWorkItemResponse(success=True))


@pytest.mark.asyncio
async def test_update_issue_with_update_labels_not_allowed(
    work_item: JiraIssue, jira_api_controller: APIController
):
    # GIVEN
    work_item.edit_meta = {'fields': {'labels': {'operations': {'add': 'allowed'}}}}
    work_item.key = 'WI1'
    # WHEN
    result = await jira_api_controller.update_issue(work_item, {'labels': 'value'})
    # THEN
    assert result == APIControllerResponse(result=UpdateWorkItemResponse(success=True))


@pytest.mark.asyncio
@patch.object(JiraAPI, 'update_issue')
async def test_update_issue_with_update_labels_allowed(
    update_issue_mock: Mock,
    work_item: JiraIssue,
    jira_api_controller: APIController,
):
    # GIVEN
    work_item.edit_meta = {'fields': {'labels': {'operations': {'set': 'allowed'}}}}
    work_item.key = 'WI1'
    update_issue_mock.return_value = {'fields': {'labels': 'new value'}}
    # WHEN
    result = await jira_api_controller.update_issue(work_item, {'labels': 'value'})
    # THEN
    assert result == APIControllerResponse(
        result=UpdateWorkItemResponse(success=True, updated_fields=['labels'])
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'transitions')
async def test_transitions(transitions_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    transitions_mock.return_value = {
        'transitions': [
            {
                'to': {
                    'description': 'a description',
                    'name': 'a name',
                    'id': '5',
                },
                'id': '2',
                'name': 'T2',
            },
            {'id': '3', 'name': 'T3'},
        ]
    }
    # WHEN
    response = await jira_api_controller.transitions('1')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == [
        IssueTransition(
            id='2',
            name='T2',
            to_state=IssueTransitionState(
                id='5',
                name='a name',
                description='a description',
            ),
        )
    ]
    transitions_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'transitions')
async def test_transitions_with_api_error(
    transitions_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    transitions_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.transitions('1')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    transitions_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'transition_issue')
@patch.object(APIController, 'transitions')
async def test_transition_issue_status(
    transitions_mock: Mock,
    transition_issue_mock: Mock,
    transitions: list[IssueTransition],
    jira_api_controller: APIController,
):
    # GIVEN
    transitions_mock.return_value = APIControllerResponse(result=transitions)
    transition_issue_mock.return_value = APIControllerResponse(result=[])
    # WHEN
    response = await jira_api_controller.transition_issue_status('1', '3')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result is None
    transitions_mock.assert_called_once_with('1')
    transition_issue_mock.assert_called_once()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'transition_issue')
@patch.object(APIController, 'transitions')
async def test_transition_issue_status_with_transition_issue_api_error(
    transitions_mock: Mock,
    transition_issue_mock: Mock,
    transitions: list[IssueTransition],
    jira_api_controller: APIController,
):
    # GIVEN
    transitions_mock.return_value = APIControllerResponse(result=transitions)
    transition_issue_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.transition_issue_status('1', '3')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    transitions_mock.assert_called_once_with('1')
    transition_issue_mock.assert_called_once()


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
async def test_transition_issue_status_status_not_found(
    transitions_mock: Mock,
    transitions: list[IssueTransition],
    jira_api_controller: APIController,
):
    # GIVEN
    transitions_mock.return_value = APIControllerResponse(result=transitions)
    # WHEN
    response = await jira_api_controller.transition_issue_status('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'Unable to find a valid transition for the given status ID.'
    assert response.result is None
    transitions_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
async def test_transition_issue_status_with_api_error(
    transitions_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    transitions_mock.return_value = APIControllerResponse(success=False, error='some error')
    # WHEN
    response = await jira_api_controller.transition_issue_status('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert (
        response.error
        == 'Unable to find valid status transitions for the selected item: some error'
    )
    assert response.result is None
    transitions_mock.assert_called_once_with('1')


@pytest.fixture
def comment_response() -> dict:
    return {
        'author': {
            'accountId': '1',
            'emailAddress': 'bart@foo.com',
            'active': True,
            'displayName': 'Bart',
        },
        'updateAuthor': {
            'accountId': '2',
            'emailAddress': 'homer@foo.com',
            'active': True,
            'displayName': 'Homer',
        },
        'created': '2025-12-31T10:20:00',
        'updated': '2025-12-31T10:20:00',
        'id': '1',
        'body': {},
    }


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_comment')
async def test_get_comment(
    get_comment_mock: Mock,
    comment_response: dict,
    jira_api_controller: APIController,
):
    # GIVEN
    get_comment_mock.return_value = comment_response
    # WHEN
    response = await jira_api_controller.get_comment('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == IssueComment(
        id='1',
        author=JiraUser(
            account_id='1',
            display_name='Bart',
            active=True,
            email='bart@foo.com',
        ),
        created=datetime(2025, 12, 31, 10, 20, 0),
        updated=datetime(2025, 12, 31, 10, 20, 0),
        update_author=JiraUser(
            account_id='2',
            display_name='Homer',
            active=True,
            email='homer@foo.com',
        ),
        body=None,
    )
    get_comment_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_comment')
async def test_get_comment_with_api_error(
    get_comment_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_comment_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.get_comment('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    get_comment_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_comments')
async def test_get_comments(
    get_comments_mock: Mock,
    comment_response: dict,
    jira_api_controller: APIController,
):
    # GIVEN
    get_comments_mock.return_value = {'comments': [comment_response]}
    # WHEN
    response = await jira_api_controller.get_comments('1', 0, 10)
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == [
        IssueComment(
            id='1',
            author=JiraUser(
                account_id='1',
                display_name='Bart',
                active=True,
                email='bart@foo.com',
            ),
            created=datetime(2025, 12, 31, 10, 20, 0),
            updated=datetime(2025, 12, 31, 10, 20, 0),
            update_author=JiraUser(
                account_id='2',
                display_name='Homer',
                active=True,
                email='homer@foo.com',
            ),
            body=None,
        )
    ]
    get_comments_mock.assert_called_once_with('1', 0, 10)


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_comments')
async def test_get_comments_with_api_error(
    get_comments_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_comments_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.get_comments('1', 0, 10)
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'Failed to retrieve the comments: some error'
    assert response.result is None
    get_comments_mock.assert_called_once_with('1', 0, 10)


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_comment')
async def test_add_comment(
    add_comment_mock: Mock, comment_response: dict, jira_api_controller: APIController
):
    # GIVEN
    add_comment_mock.return_value = comment_response
    # WHEN
    response = await jira_api_controller.add_comment('1', 'text')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == IssueComment(
        id='1',
        author=JiraUser(
            account_id='1',
            display_name='Bart',
            active=True,
            email='bart@foo.com',
        ),
        created=datetime(2025, 12, 31, 10, 20, 0),
        updated=datetime(2025, 12, 31, 10, 20, 0),
        update_author=JiraUser(
            account_id='2',
            display_name='Homer',
            active=True,
            email='homer@foo.com',
        ),
        body=None,
    )
    add_comment_mock.assert_called_once_with('1', 'text')


@pytest.mark.asyncio
async def test_add_comment_without_message(jira_api_controller: APIController):
    # WHEN
    response = await jira_api_controller.add_comment('1', '')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'Missing required message.'
    assert response.result is None


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_comment')
async def test_add_comment_with_api_error(
    add_comment_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    add_comment_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.add_comment('1', 'text')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    add_comment_mock.assert_called_once_with('1', 'text')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_comment')
async def test_delete_comment(delete_comment_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    delete_comment_mock.return_value = APIControllerResponse()
    # WHEN
    response = await jira_api_controller.delete_comment('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    delete_comment_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_comment')
async def test_delete_comment_with_api_error(
    delete_comment_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    delete_comment_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.delete_comment('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    delete_comment_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_issue_link')
async def test_link_work_items(create_issue_link_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    create_issue_link_mock.return_value = APIControllerResponse()
    # WHEN
    response = await jira_api_controller.link_work_items('1', '2', 'causes', '4')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    create_issue_link_mock.assert_called_once_with(
        left_issue_key='1',
        right_issue_key='2',
        link_type='causes',
        link_type_id='4',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_issue_link')
async def test_link_work_items_with_api_error(
    create_issue_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    create_issue_link_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.link_work_items('1', '2', 'causes', '4')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    create_issue_link_mock.assert_called_once_with(
        left_issue_key='1',
        right_issue_key='2',
        link_type='causes',
        link_type_id='4',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_issue_link')
async def test_delete_issue_link(delete_issue_link_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    delete_issue_link_mock.return_value = APIControllerResponse()
    # WHEN
    response = await jira_api_controller.delete_issue_link('1')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    delete_issue_link_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_issue_link')
async def test_delete_issue_link_with_api_error(
    delete_issue_link_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    delete_issue_link_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.delete_issue_link('1')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    delete_issue_link_mock.assert_called_once_with('1')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'issue_link_types')
async def test_issue_link_types(issue_link_types_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    issue_link_types_mock.return_value = {
        'issueLinkTypes': [
            {
                'id': '1',
                'name': 'type 1',
                'inward': 'in',
                'outward': 'out',
            }
        ]
    }
    # WHEN
    response = await jira_api_controller.issue_link_types()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == [LinkIssueType(id='1', name='type 1', inward='in', outward='out')]
    issue_link_types_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'issue_link_types')
async def test_issue_link_types_with_api_error(
    issue_link_types_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    issue_link_types_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.issue_link_types()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    issue_link_types_mock.assert_called_once_with()
