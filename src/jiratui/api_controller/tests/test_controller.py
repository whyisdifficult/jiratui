from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from jiratui.api.api import JiraAPI, JiraDataCenterAPI
from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.api_controller.factories import WorkItemFactory
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
    JiraField,
    JiraGlobalSettings,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraMyselfInfo,
    JiraServerInfo,
    JiraTimeTrackingConfiguration,
    JiraUser,
    JiraUserGroup,
    JiraWorklog,
    LinkIssueType,
    PaginatedJiraWorklog,
    Project,
    UpdateWorkItemResponse,
)
from jiratui.utils.test_utilities import load_json_response


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
        'body': {
            'type': 'doc',
            'version': 1,
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello World!'}]}
            ],
        },
    }


@pytest.fixture
def comment_response_without_adf() -> dict:
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
        'body': 'Hello World!',
    }


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
    # GIVEN
    jira_api_controller.config.jql_expression_id_for_work_items_search = None
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
        id='10003',
        name='Task',
        scope_project=None,
        hierarchy_level=0,
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
    assert response.error == 'an error'


@pytest.mark.asyncio
@patch.object(WorkItemFactory, 'create_work_item')
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(JiraAPI, 'get_issue')
async def test_get_issue_with_instance_building_error(
    get_issue_mock: Mock,
    configuration_mock: Mock,
    create_work_item_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_issue_mock.return_value = load_json_response(__file__, 'issue.json')
    create_work_item_mock.side_effect = ValueError('another error')
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
        id='10003',
        name='Task',
        scope_project=None,
        hierarchy_level=0,
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
@patch.object(WorkItemFactory, 'create_work_item')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraAPI, 'search_issues')
async def test_search_issues_with_missing_issues(
    search_issues_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    create_work_item_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    search_issues_mock.return_value = {
        'issues': [load_json_response(__file__, 'issue.json')],
        'nextPageToken': 't1',
        'isLast': False,
    }
    create_work_item_mock.side_effect = ValueError('some error')
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


@pytest.mark.parametrize('page, expected_offset', [(0, 0), (1, 0), (2, 50), (None, 0)])
@pytest.mark.asyncio
@patch('jiratui.api_controller.factories.CONFIGURATION')
@patch.object(APIController, '_build_criteria_for_searching_work_items')
@patch.object(JiraDataCenterAPI, 'search_issues')
async def test_search_issues_for_jira_dc(
    search_issues_mock: Mock,
    build_criteria_for_searching_work_items_mock: Mock,
    configuration_mock: Mock,
    jira_api_controller_for_jira_dc: APIController,
    page,
    expected_offset,
):
    # GIVEN
    build_criteria_for_searching_work_items_mock.return_value = {}
    search_issues_mock.return_value = {
        'expand': 'names,schema',
        'startAt': 0,
        'maxResults': 50,
        'total': 1,
        'issues': [
            {
                'expand': '',
                'id': '10001',
                'self': 'http://www.example.com/jira/rest/api/2/issue/10001',
                'key': 'HSP-1',
                'fields': {'summary': '(Sample) Set Up Payment Logging'},
            }
        ],
        'warningMessages': ["The value 'splat' does not exist for the field 'Foo'."],
    }
    # WHEN
    response = await jira_api_controller_for_jira_dc.search_issues_by_page_number(page=page)
    # THEN
    assert response.success is True
    assert response.error is None
    assert isinstance(response.result, JiraIssueSearchResponse)
    assert response.result.is_last is None
    assert response.result.next_page_token is None
    assert response.result.issues[0].id == '10001'
    assert response.result.issues[0].key == 'HSP-1'
    assert response.result.issues[0].summary == '(Sample) Set Up Payment Logging'
    build_criteria_for_searching_work_items_mock.assert_called_once()
    search_issues_mock.assert_called_once_with(
        project_key=None,
        created_from=None,
        created_until=None,
        updated_from=None,
        status=None,
        assignee=None,
        issue_type=None,
        search_in_active_sprint=False,
        jql_query=None,
        offset=expected_offset,
        fields=['id', 'key', 'status', 'summary', 'issuetype', 'parent'],
        limit=None,
        order_by=None,
    )


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
    assert response.error == 'some error'
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
    assert response.error == 'some error'
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
@patch.object(JiraAPI, 'global_settings')
async def test_global_settings_with_api_error(
    global_settings_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    global_settings_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.global_settings()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    global_settings_mock.assert_called_once_with()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'global_settings')
async def test_global_settings(global_settings_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    global_settings_mock.return_value = {
        'attachmentsEnabled': True,
        'issueLinkingEnabled': True,
        'subTasksEnabled': False,
        'timeTrackingConfiguration': {
            'defaultUnit': 'day',
            'timeFormat': 'pretty',
            'workingDaysPerWeek': 5,
            'workingHoursPerDay': 8,
        },
        'timeTrackingEnabled': True,
        'unassignedIssuesAllowed': False,
        'votingEnabled': True,
        'watchingEnabled': True,
    }
    # WHEN
    response = await jira_api_controller.global_settings()
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == JiraGlobalSettings(
        attachments_enabled=True,
        issue_linking_enabled=True,
        subtasks_enabled=False,
        unassigned_issues_allowed=False,
        voting_enabled=True,
        watching_enabled=True,
        time_tracking_enabled=True,
        time_tracking_configuration=JiraTimeTrackingConfiguration(
            default_unit='day',
            time_format='pretty',
            working_days_per_week=5,
            working_hours_per_day=8,
        ),
    )
    global_settings_mock.assert_called_once_with()


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


@pytest.mark.parametrize('field_name', ['summary', 'duedate', 'priority', 'assignee_account_id'])
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
        match=f'The field {field_name} can not be updated for the selected work item.',
    ):
        await jira_api_controller.update_issue(work_item, {field_name: 'value'})


@pytest.mark.parametrize(
    'field_name, field_key',
    [
        ('summary', 'summary'),
        ('duedate', 'duedate'),
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
        match=f'The field {field_key} can not be updated for the selected work item.',
    ):
        await jira_api_controller.update_issue(work_item, {field_name: 'value'})


@pytest.mark.parametrize(
    'field_id, field_key, updated_fields',
    [
        ('summary', 'summary', ['summary']),
        ('duedate', 'duedate', ['duedate']),
        ('priority', 'priority', ['priority']),
        ('assignee_account_id', 'assignee', ['assignee_account_id']),
    ],
)
@pytest.mark.asyncio
@patch.object(JiraAPI, 'update_issue')
async def test_update_issue_with_update_fields_update_allowed(
    update_issue_mock: Mock,
    field_id: str,
    field_key: str,
    updated_fields: list[str],
    work_item: JiraIssue,
    jira_api_controller: APIController,
):
    # GIVEN
    work_item.edit_meta = {'fields': {field_key: {'operations': {'set': 'new value'}}}}
    work_item.key = 'WI1'
    update_issue_mock.return_value = {'fields': {field_id: 'new value'}}
    # WHEN
    result = await jira_api_controller.update_issue(work_item, {field_id: 'value'})
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
        body={
            'type': 'doc',
            'version': 1,
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello World!'}]}
            ],
        },
    )
    get_comment_mock.assert_called_once_with('1', '2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_comment')
async def test_get_comment_without_adf(
    get_comment_mock: Mock,
    comment_response_without_adf: dict,
    jira_api_controller: APIController,
):
    # GIVEN
    get_comment_mock.return_value = comment_response_without_adf
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
        body='Hello World!',
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
            body={
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello World!'}]}
                ],
            },
        )
    ]
    get_comments_mock.assert_called_once_with('1', 0, 10)


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_comments')
async def test_get_comments_without_adf(
    get_comments_mock: Mock,
    comment_response_without_adf: dict,
    jira_api_controller: APIController,
):
    # GIVEN
    get_comments_mock.return_value = {'comments': [comment_response_without_adf]}
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
            body='Hello World!',
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
    assert response.error == 'some error'
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
        body={
            'type': 'doc',
            'version': 1,
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello World!'}]}
            ],
        },
    )
    add_comment_mock.assert_called_once_with('1', 'text')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_comment')
async def test_add_comment_without_adf(
    add_comment_mock: Mock, comment_response_without_adf: dict, jira_api_controller: APIController
):
    # GIVEN
    add_comment_mock.return_value = comment_response_without_adf
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
        body='Hello World!',
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


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_work_log')
async def test_get_work_item_worklog(
    get_issue_work_log_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_work_log_mock.return_value = {
        'maxResults': 10,
        'startAt': 0,
        'total': 1,
        'worklogs': [
            {
                'author': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'comment': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'I did some work here.'}],
                        }
                    ],
                },
                'id': '100028',
                'issueId': '10002',
                'started': '2021-01-17T12:34:00.000+0000',
                'timeSpent': '3h 20m',
                'timeSpentSeconds': 12000,
                'updateAuthor': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'emailAddress': 'foo@barr',
                },
                'updated': '2021-01-18T23:45:00.000+0000',
            }
        ],
    }
    # WHEN
    response = await jira_api_controller.get_work_item_worklog('1')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == PaginatedJiraWorklog(
        logs=[
            JiraWorklog(
                id='100028',
                issue_id='10002',
                started=datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
                updated=datetime(2021, 1, 18, 23, 45, 0, tzinfo=timezone.utc),
                time_spent='3h 20m',
                time_spent_seconds=12000,
                author=JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    display_name='Mia Krystof',
                    active=False,
                    email=None,
                    username=None,
                ),
                update_author=JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    display_name='Mia Krystof',
                    active=False,
                    email='foo@barr',
                    username=None,
                ),
                comment={
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'I did some work here.'}],
                        }
                    ],
                },
            )
        ],
        start_at=0,
        max_results=10,
        total=1,
    )
    get_issue_work_log_mock.assert_called_once_with('1', None, None)


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_work_log')
async def test_get_work_item_worklog_with_api_error(
    get_issue_work_log_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    get_issue_work_log_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.get_work_item_worklog('1')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    get_issue_work_log_mock.assert_called_once_with('1', None, None)


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_issue_work_log')
async def test_add_work_item_worklog(
    add_issue_work_log_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    add_issue_work_log_mock.return_value = {
        'author': {
            'accountId': '5b10a2844c20165700ede21g',
            'active': True,
            'displayName': 'bart simpson',
            'emailAddress': 'bart@simpson.com',
            'key': 'bart',
            'name': 'bart',
        },
        'created': '2021-01-17T12:34:00.000+0000',
        'id': '2',
        'issueId': '1',
        'started': '2021-01-16T12:34:00.000+0000',
        'timeSpent': '1h',
        'timeSpentSeconds': 3600,
        'updateAuthor': {
            'accountId': '5b10a2844c20165700ede21g',
            'active': True,
            'displayName': 'bart simpson',
            'emailAddress': 'bart@simpson.com',
            'key': 'bart',
            'name': 'bart',
        },
        'updated': '2021-01-17T12:34:00.000+0000',
    }
    # WHEN
    response = await jira_api_controller.add_work_item_worklog(
        '1',
        datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        '1h',
        '2h',
        'some comment',
        '3h',
    )
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result == JiraWorklog(
        id='2',
        issue_id='1',
        started=datetime(2021, 1, 16, 12, 34, 0, tzinfo=timezone.utc),
        updated=datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        time_spent='1h',
        time_spent_seconds=3600,
        author=JiraUser(
            account_id='5b10a2844c20165700ede21g',
            display_name='bart simpson',
            active=True,
            email='bart@simpson.com',
            username=None,
        ),
        update_author=JiraUser(
            account_id='5b10a2844c20165700ede21g',
            display_name='bart simpson',
            active=True,
            email='bart@simpson.com',
            username=None,
        ),
        comment=None,
    )
    add_issue_work_log_mock.assert_called_once_with(
        issue_id_or_key='1',
        started=datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        time_spent='1h',
        time_remaining='2h',
        comment='some comment',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_issue_work_log')
async def test_add_work_item_worklog_with_api_error(
    add_issue_work_log_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    add_issue_work_log_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.add_work_item_worklog(
        '1',
        datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        '1h',
        '2h',
        'some comment',
        '3h',
    )
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    add_issue_work_log_mock.assert_called_once_with(
        issue_id_or_key='1',
        started=datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        time_spent='1h',
        time_remaining='2h',
        comment='some comment',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_issue_work_log')
async def test_add_work_item_worklog_without_current_time_remaining(
    add_issue_work_log_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    add_issue_work_log_mock.return_value = {}
    # WHEN
    await jira_api_controller.add_work_item_worklog(
        '1',
        datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        '1h',
        '2h',
        'some comment',
        None,
    )
    # THEN
    add_issue_work_log_mock.assert_called_once_with(
        issue_id_or_key='1',
        started=datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        time_spent='1h',
        time_remaining=None,
        comment='some comment',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'add_issue_work_log')
async def test_add_work_item_worklog_without_time_remaining(
    add_issue_work_log_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    add_issue_work_log_mock.return_value = {}
    # WHEN
    await jira_api_controller.add_work_item_worklog(
        '1',
        datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        '1h',
        None,
        'some comment',
        None,
    )
    # THEN
    add_issue_work_log_mock.assert_called_once_with(
        issue_id_or_key='1',
        started=datetime(2021, 1, 17, 12, 34, 0, tzinfo=timezone.utc),
        time_spent='1h',
        time_remaining=None,
        comment='some comment',
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_work_log')
async def test_remove_worklog(delete_work_log_mock: Mock, jira_api_controller: APIController):
    # GIVEN
    delete_work_log_mock.return_value = None
    # WHEN
    response = await jira_api_controller.remove_worklog('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is True
    assert response.error is None
    assert response.result is None
    delete_work_log_mock.assert_called_once_with(issue_id_or_key='1', worklog_id='2')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'delete_work_log')
async def test_remove_worklog_with_api_error(
    delete_work_log_mock: Mock, jira_api_controller: APIController
):
    # GIVEN
    delete_work_log_mock.side_effect = ValueError('some error')
    # WHEN
    response = await jira_api_controller.remove_worklog('1', '2')
    # THEN
    assert isinstance(response, APIControllerResponse)
    assert response.success is False
    assert response.error == 'some error'
    assert response.result is None
    delete_work_log_mock.assert_called_once_with(issue_id_or_key='1', worklog_id='2')


@pytest.mark.asyncio
@patch.object(APIController, 'get_fields')
async def test_update_issue_flagged_status_without_fields_configuration(
    get_fields_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_fields_mock.return_value = APIControllerResponse(success=False)
    # WHEN
    result = await jira_api_controller.update_issue_flagged_status('1')
    # THEN
    assert result == APIControllerResponse(
        success=False, error='Unable to flag the item. Missing fields configuration.'
    )
    get_fields_mock.assert_called_once_with('flagged')


@pytest.mark.asyncio
@patch.object(APIController, 'get_fields')
async def test_update_issue_flagged_status_without_field_configuration(
    get_fields_mock: Mock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_fields_mock.return_value = APIControllerResponse(
        result=[JiraField(id='1', name='a', key='', custom=True, schema={})]
    )
    # WHEN
    result = await jira_api_controller.update_issue_flagged_status('1')
    # THEN
    assert result == APIControllerResponse(
        success=False,
        error='Unable to flag the item. Missing configuration for "flagged" field.',
    )
    get_fields_mock.assert_called_once_with('flagged')


@pytest.mark.asyncio
@patch.object(JiraAPI, 'update_issue')
@patch.object(APIController, 'get_fields')
async def test_update_issue_flagged_status_updating_fails(
    get_fields_mock: Mock,
    update_issue_mock: AsyncMock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_fields_mock.return_value = APIControllerResponse(
        result=[
            JiraField(
                id='10021',
                name='Flagged',
                key='customfield_10021',
                custom=True,
                schema={
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                    'customId': 10021,
                },
            )
        ]
    )
    update_issue_mock.side_effect = ValueError('some error')
    # WHEN
    result = await jira_api_controller.update_issue_flagged_status('1')
    # THEN
    assert result == APIControllerResponse(success=False, error='some error')
    get_fields_mock.assert_called_once_with('flagged')
    update_issue_mock.assert_called_once_with(
        '1', {'customfield_10021': [{'set': [{'value': 'Impediment'}]}]}
    )


@pytest.mark.asyncio
@patch.object(JiraAPI, 'update_issue')
@patch.object(APIController, 'get_fields')
async def test_update_issue_flagged_status_updating_fails_when_removing_flag(
    get_fields_mock: Mock,
    update_issue_mock: AsyncMock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_fields_mock.return_value = APIControllerResponse(
        result=[
            JiraField(
                id='10021',
                name='Flagged',
                key='customfield_10021',
                custom=True,
                schema={
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                    'customId': 10021,
                },
            )
        ]
    )
    update_issue_mock.side_effect = ValueError('some error')
    # WHEN
    result = await jira_api_controller.update_issue_flagged_status('1', add_flag=False)
    # THEN
    assert result == APIControllerResponse(success=False, error='some error')
    get_fields_mock.assert_called_once_with('flagged')
    update_issue_mock.assert_called_once_with('1', {'customfield_10021': [{'set': [{'id': None}]}]})


@pytest.mark.asyncio
@patch.object(APIController, 'add_comment')
@patch.object(JiraAPI, 'update_issue')
@patch.object(APIController, 'get_fields')
async def test_update_issue_flagged_status_updating_succeeds_with_note(
    get_fields_mock: Mock,
    update_issue_mock: AsyncMock,
    add_comment_mock: AsyncMock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_fields_mock.return_value = APIControllerResponse(
        result=[
            JiraField(
                id='10021',
                name='Flagged',
                key='customfield_10021',
                custom=True,
                schema={
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                    'customId': 10021,
                },
            )
        ]
    )
    update_issue_mock.return_value = {}
    add_comment_mock.return_value = APIControllerResponse()
    # WHEN
    result = await jira_api_controller.update_issue_flagged_status(
        '1', add_flag=True, note='comment'
    )
    # THEN
    assert result == APIControllerResponse(
        result=UpdateWorkItemResponse(success=True, updated_fields=[])
    )
    get_fields_mock.assert_called_once_with('flagged')
    update_issue_mock.assert_called_once_with(
        '1', {'customfield_10021': [{'set': [{'value': 'Impediment'}]}]}
    )
    add_comment_mock.assert_called_once_with('1', 'comment')


@pytest.mark.asyncio
@patch.object(APIController, 'add_comment')
@patch.object(JiraAPI, 'update_issue')
@patch.object(APIController, 'get_fields')
async def test_update_issue_flagged_status_updating_succeeds_without_note(
    get_fields_mock: Mock,
    update_issue_mock: AsyncMock,
    add_comment_mock: AsyncMock,
    jira_api_controller: APIController,
):
    # GIVEN
    get_fields_mock.return_value = APIControllerResponse(
        result=[
            JiraField(
                id='10021',
                name='Flagged',
                key='customfield_10021',
                custom=True,
                schema={
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                    'customId': 10021,
                },
            )
        ]
    )
    update_issue_mock.return_value = {}
    add_comment_mock.return_value = APIControllerResponse()
    # WHEN
    result = await jira_api_controller.update_issue_flagged_status('1', add_flag=True)
    # THEN
    assert result == APIControllerResponse(
        result=UpdateWorkItemResponse(success=True, updated_fields=[])
    )
    get_fields_mock.assert_called_once_with('flagged')
    update_issue_mock.assert_called_once_with(
        '1', {'customfield_10021': [{'set': [{'value': 'Impediment'}]}]}
    )
    add_comment_mock.assert_not_called()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_integration_success(
    create_work_item_mock: Mock, jira_api_controller: APIController, caplog
):
    """Integration test: Successful issue creation without reporter field.

    Verifies that:
    - Issue creation succeeds when reporter field is not included
    - No errors are raised during the full creation flow
    - Response contains valid work item data
    """
    # GIVEN
    create_work_item_mock.return_value = {
        'id': '10001',
        'key': 'TEST-1',
        'self': 'https://example.atlassian.net/rest/api/3/issue/10001',
    }

    data = {
        'project_key': 'TEST',
        'summary': 'Test issue without reporter field',
        'issue_type_id': '10001',
        'description': 'This is a test issue',
    }

    # WHEN
    result = await jira_api_controller.create_work_item(data)

    # THEN
    assert result.success is True
    assert result.error is None
    assert result.result is not None
    assert result.result.id == '10001'
    assert result.result.key == 'TEST-1'

    # Verify the API was called with correct fields (no reporter)
    call_args = create_work_item_mock.call_args
    assert call_args is not None
    fields = call_args[0][0]  # First positional argument
    assert 'reporter' not in fields
    assert fields['project'] == {'key': 'TEST'}
    assert fields['summary'] == 'Test issue without reporter field'


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_integration_reporter_field_included_when_provided(
    create_work_item_mock: Mock, jira_api_controller: APIController
):
    """Integration test: Reporter field is included when provided.

    Verifies that:
    - reporter_account_id in input data is properly passed to the API
    - Users with appropriate privileges can set the reporter
    - Issue creation succeeds with reporter field
    - Reporter field is included in the API call
    """
    # GIVEN
    create_work_item_mock.return_value = {
        'id': '10002',
        'key': 'TEST-2',
        'self': 'https://example.atlassian.net/rest/api/3/issue/10002',
    }

    data = {
        'project_key': 'TEST',
        'summary': 'Test issue with reporter field',
        'issue_type_id': '10001',
        'description': 'This issue includes reporter_account_id',
        'reporter_account_id': '5e12345abcdef',
    }

    # WHEN
    result = await jira_api_controller.create_work_item(data)

    # THEN
    assert result.success is True
    assert result.error is None

    # Verify the API was called WITH reporter field
    call_args = create_work_item_mock.call_args
    assert call_args is not None
    fields = call_args[0][0]
    assert 'reporter' in fields, 'Reporter field should be sent to API'
    assert fields['reporter'] == {'id': '5e12345abcdef'}


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_integration_field_validation_error_handling(
    create_work_item_mock: Mock, jira_api_controller: APIController
):
    """Integration test: Enhanced error messages for field validation errors.

    Verifies that:
    - Field validation errors from Jira API are caught
    - Error messages are enhanced with user-friendly context
    - The error response includes actionable information
    """
    # GIVEN
    from jiratui.exceptions import ServiceInvalidRequestException

    # Simulate a field validation error from Jira API
    error = ServiceInvalidRequestException(
        "Field 'priority' cannot be set. It is not on the appropriate screen, or unknown."
    )
    error.extra = {
        'errors': {
            'priority': "Field 'priority' cannot be set. It is not on the appropriate screen, or unknown."
        },
        'errorMessages': [],
    }
    create_work_item_mock.side_effect = error

    data = {
        'project_key': 'TEST',
        'summary': 'Test issue with invalid priority',
        'issue_type_id': '10001',
        'priority': '999',  # Invalid priority
    }

    # WHEN
    result = await jira_api_controller.create_work_item(data)

    # THEN
    assert result.success is False
    assert result.result is None
    assert result.error is not None
    # Error should contain the field name and problem description
    assert 'priority' in result.error.lower()


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_integration_multiple_validation_errors(
    create_work_item_mock: Mock, jira_api_controller: APIController
):
    """Integration test: Multiple field validation errors are handled.

    Verifies that:
    - Multiple validation errors are caught and reported
    - Error response includes all field-specific errors
    """
    # GIVEN
    from jiratui.exceptions import ServiceInvalidRequestException

    error = ServiceInvalidRequestException('Multiple fields have errors')
    error.extra = {
        'errors': {
            'priority': "Field 'priority' cannot be set.",
            'customfield_10001': 'Custom field is required.',
        },
        'errorMessages': ['Issue type is missing'],
    }
    create_work_item_mock.side_effect = error

    data = {
        'project_key': 'TEST',
        'summary': 'Test issue with multiple errors',
        'issue_type_id': '10001',
    }

    # WHEN
    result = await jira_api_controller.create_work_item(data)

    # THEN
    assert result.success is False
    assert result.result is None
    assert result.error is not None
    # Error message should contain indication of validation failure
    assert len(result.error) > 0


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_integration_full_flow_with_all_fields(
    create_work_item_mock: Mock, jira_api_controller: APIController
):
    """Integration test: Full creation flow with all supported fields including reporter.

    Verifies that:
    - All supported fields are properly passed through
    - Reporter field is included when provided
    - Issue creation completes successfully with all fields
    """
    # GIVEN
    create_work_item_mock.return_value = {
        'id': '10003',
        'key': 'TEST-3',
        'self': 'https://example.atlassian.net/rest/api/3/issue/10003',
    }

    data = {
        'project_key': 'TEST',
        'summary': 'Complete test issue',
        'issue_type_id': '10001',
        'description': 'Full test with all fields',
        'reporter_account_id': '5e12345abcdef',
        'assignee_account_id': '5e67890ghijkl',
        'priority': '2',
        'parent_key': 'TEST-1',
    }

    # WHEN
    result = await jira_api_controller.create_work_item(data)

    # THEN
    assert result.success is True

    # Verify the API was called with correct fields
    call_args = create_work_item_mock.call_args
    assert call_args is not None
    fields = call_args[0][0]

    # Reporter should be present
    assert 'reporter' in fields
    assert fields['reporter'] == {'id': '5e12345abcdef'}

    # Other fields should be present
    assert fields['project'] == {'key': 'TEST'}
    assert fields['summary'] == 'Complete test issue'
    assert fields['issuetype'] == {'id': '10001'}
    assert fields['assignee'] == {'id': '5e67890ghijkl'}
    assert fields['priority'] == {'id': '2'}
    assert fields['parent'] == {'key': 'TEST-1'}


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_create_meta')
async def test_get_required_fields_for_issue_type_different_cache_keys(
    get_issue_create_meta_mock,
    jira_api_controller,
):
    """Test that different project/issue type combinations have separate cache entries."""
    # GIVEN
    metadata1 = {'fields': [{'key': 'summary', 'required': True}]}
    metadata2 = {'fields': [{'key': 'description', 'required': True}]}
    get_issue_create_meta_mock.side_effect = [metadata1, metadata2]

    # WHEN - Different project
    result1 = await jira_api_controller.get_required_fields_for_issue_type('TEST', '10001')
    result2 = await jira_api_controller.get_required_fields_for_issue_type('PROJ', '10001')

    # THEN
    assert result1.result == ['summary']
    assert result2.result == ['description']
    assert get_issue_create_meta_mock.call_count == 2


@pytest.mark.asyncio
@patch.object(JiraAPI, 'get_issue_create_meta')
async def test_get_required_fields_for_issue_type_api_error(
    get_issue_create_meta_mock,
    jira_api_controller,
):
    """Test error handling when API call fails."""
    # GIVEN
    get_issue_create_meta_mock.side_effect = Exception('API Error')

    # WHEN
    result = await jira_api_controller.get_required_fields_for_issue_type('TEST', '10001')

    # THEN
    assert result.success is False
    assert 'API Error' in result.error


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_with_dynamic_fields(
    create_work_item_mock,
    jira_api_controller,
):
    """Test create_work_item with dynamic required fields."""
    # GIVEN
    create_work_item_mock.return_value = {'id': '10004', 'key': 'TEST-4'}

    data = {
        'project_key': 'TEST',
        'summary': 'Test with dynamic fields',
        'issue_type_id': '10001',
    }

    # WHEN - Pass dynamic fields as kwargs
    result = await jira_api_controller.create_work_item(
        data,
        customfield_10712='test value',
        customfield_10713={'id': '123'},
    )

    # THEN
    assert result.success is True
    call_args = create_work_item_mock.call_args
    fields = call_args[0][0]

    # Standard fields
    assert fields['project'] == {'key': 'TEST'}
    assert fields['summary'] == 'Test with dynamic fields'

    # Dynamic custom fields
    assert fields['customfield_10712'] == 'test value'
    assert fields['customfield_10713'] == {'id': '123'}


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_with_components_list_of_ids(
    create_work_item_mock,
    jira_api_controller,
):
    """Test create_work_item handles components as list of IDs correctly."""
    # GIVEN
    create_work_item_mock.return_value = {'id': '10005', 'key': 'TEST-5'}

    data = {
        'project_key': 'TEST',
        'summary': 'Test with components',
        'issue_type_id': '10001',
    }

    # WHEN - Pass components as list of IDs
    result = await jira_api_controller.create_work_item(
        data,
        components=['10100', '10101'],
    )

    # THEN
    assert result.success is True
    call_args = create_work_item_mock.call_args
    fields = call_args[0][0]

    # Components should be converted to array of objects
    assert fields['components'] == [{'id': '10100'}, {'id': '10101'}]


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_with_components_single_id(
    create_work_item_mock,
    jira_api_controller,
):
    """Test create_work_item handles single component ID correctly."""
    # GIVEN
    create_work_item_mock.return_value = {'id': '10006', 'key': 'TEST-6'}

    data = {
        'project_key': 'TEST',
        'summary': 'Test with single component',
        'issue_type_id': '10001',
    }

    # WHEN - Pass single component ID
    result = await jira_api_controller.create_work_item(
        data,
        components='10100',
    )

    # THEN
    assert result.success is True
    call_args = create_work_item_mock.call_args
    fields = call_args[0][0]

    # Single component should be converted to array with one object
    assert fields['components'] == [{'id': '10100'}]


@pytest.mark.asyncio
@patch.object(JiraAPI, 'create_work_item')
async def test_create_work_item_with_components_already_formatted(
    create_work_item_mock,
    jira_api_controller,
):
    """Test create_work_item handles pre-formatted components correctly."""
    # GIVEN
    create_work_item_mock.return_value = {'id': '10007', 'key': 'TEST-7'}

    data = {
        'project_key': 'TEST',
        'summary': 'Test with pre-formatted components',
        'issue_type_id': '10001',
    }

    # WHEN - Pass components already in correct format
    result = await jira_api_controller.create_work_item(
        data,
        components=[{'id': '10100'}, {'id': '10101'}],
    )

    # THEN
    assert result.success is True
    call_args = create_work_item_mock.call_args
    fields = call_args[0][0]

    # Pre-formatted components should be passed through as-is
    assert fields['components'] == [{'id': '10100'}, {'id': '10101'}]
