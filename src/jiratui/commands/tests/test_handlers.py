from datetime import date
import re
from unittest.mock import AsyncMock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.commands.handler import CommandHandler
from jiratui.exceptions import CLIException, UpdateWorkItemException, ValidationError
from jiratui.models import (
    IssueComment,
    IssuePriority,
    IssueStatus,
    IssueTransition,
    IssueType,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraUser,
    JiraUserGroup,
    UpdateWorkItemResponse,
    WorkItemsSearchOrderBy,
)


@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_users_without_email_or_name(config_mock, config_for_testing):
    config_mock.return_value = config_for_testing
    handler = CommandHandler()
    with pytest.raises(
        CLIException,
        match=re.escape('You need do provide a value (name or email) to search users.'),
    ):
        handler.users('')


@patch.object(APIController, 'search_users')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_users_with_email_or_name_not_found(
    config_mock, search_users_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    search_users_mock.return_value = APIControllerResponse(
        success=False, error='some error occurred'
    )
    handler = CommandHandler()
    with pytest.raises(
        CLIException, match='An error occurred while searching for users: some error occurred'
    ):
        handler.users('foo@bar')
        search_users_mock.assert_called_once_with(email_or_name='foo@bar')


@patch.object(APIController, 'search_users')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_users_with_email_or_name_found(
    config_mock, search_users_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    search_users_mock.return_value = APIControllerResponse(
        result=[JiraUser(account_id='1', display_name='Bart Simpson', active=True)]
    )
    handler = CommandHandler()
    # WHEN
    result = handler.users('foo@bar')
    # THEN
    search_users_mock.assert_called_once_with(email_or_name='foo@bar')
    assert result == [JiraUser(account_id='1', display_name='Bart Simpson', active=True)]


@patch.object(APIController, 'find_groups')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_search_user_groups(config_mock, find_groups_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    find_groups_mock.return_value = APIControllerResponse(result=[JiraUserGroup(id='1', name='G1')])
    handler = CommandHandler()
    # WHEN
    result = handler.search_user_groups(group_ids=['1'], group_names=['G1'])
    # THEN
    find_groups_mock.assert_called_once_with(
        offset=0, limit=25, groups_ids=['1'], groups_names=['G1']
    )
    assert result == [JiraUserGroup(id='1', name='G1')]


@patch.object(APIController, 'find_groups')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_search_user_groups_no_success(
    config_mock, find_groups_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    find_groups_mock.return_value = APIControllerResponse(
        success=False, error='some error occurred'
    )
    handler = CommandHandler()
    # WHEN
    with pytest.raises(
        CLIException, match='An error occurred while searching for user groups: some error occurred'
    ):
        handler.search_user_groups(group_ids=['1'], group_names=['G1'])


@patch.object(APIController, 'count_users_in_group')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_total_users_in_group(
    config_mock, count_users_in_group_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    count_users_in_group_mock.return_value = APIControllerResponse(result=1)
    handler = CommandHandler()
    # WHEN
    result = handler.total_users_in_group(group_id='1')
    # THEN
    count_users_in_group_mock.assert_called_once_with(group_id='1')
    assert result == 1


@patch.object(APIController, 'add_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_add_comment_success(config_mock, add_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    expected_comment = IssueComment(
        id='123',
        author=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        body='Test comment',
    )
    add_comment_mock.return_value = APIControllerResponse(result=expected_comment)
    handler = CommandHandler()
    # WHEN
    result = handler.add_comment(key='PROJ-1', message='Test comment')
    # THEN
    add_comment_mock.assert_called_once_with('PROJ-1', 'Test comment')
    assert result == expected_comment


@patch.object(APIController, 'add_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_add_comment_failure(config_mock, add_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    add_comment_mock.return_value = APIControllerResponse(
        success=False, error='Comment failed to post'
    )
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='An error occurred while adding a comment.'):
        handler.add_comment(key='PROJ-2', message='Failed comment')
    # THEN
    add_comment_mock.assert_called_once_with('PROJ-2', 'Failed comment')


@patch.object(APIController, 'get_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comments_single_comment_success(
    config_mock, get_comment_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    expected_comment = {'id': '123', 'author': 'user', 'body': 'Test comment'}
    get_comment_mock.return_value = APIControllerResponse(result=expected_comment)
    handler = CommandHandler()
    # WHEN
    result = handler.get_comments(key='PROJ-1', comment_id='123')
    # THEN
    get_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-1', comment_id='123')
    assert result == {'comments': [expected_comment], 'total': 1}


@patch.object(APIController, 'get_comments')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comments_multiple_comments_success(
    config_mock, get_comments_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    expected_comments = [
        {'id': '1', 'author': 'user1', 'body': 'Comment 1'},
        {'id': '2', 'author': 'user2', 'body': 'Comment 2'},
    ]
    get_comments_mock.return_value = APIControllerResponse(result=expected_comments)
    handler = CommandHandler()
    # WHEN
    result = handler.get_comments(key='PROJ-1', page=1)
    # THEN
    get_comments_mock.assert_called_once_with(issue_key_or_id='PROJ-1', offset=0, limit=10)
    assert result == {'comments': expected_comments, 'total': 2}


@patch.object(APIController, 'get_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comments_single_comment_failure(
    config_mock, get_comment_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_comment_mock.return_value = APIControllerResponse(success=False, error='Comment not found')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='An error occurred while fetching the comments.'):
        handler.get_comments(key='PROJ-1', comment_id='999')
    # THEN
    get_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-1', comment_id='999')


@patch.object(APIController, 'get_comments')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comments_multiple_comments_failure(
    config_mock, get_comments_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_comments_mock.return_value = APIControllerResponse(
        success=False, error='Failed to fetch comments'
    )
    handler = CommandHandler()
    # WHEN
    with pytest.raises(
        CLIException, match='There was an error while trying to fetch the comments.'
    ):
        handler.get_comments(key='PROJ-2', page=2)
    # THEN
    get_comments_mock.assert_called_once_with(issue_key_or_id='PROJ-2', offset=10, limit=10)


@patch.object(APIController, 'get_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comment_success(config_mock, get_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    expected_comment = IssueComment(
        id='123',
        author=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        body='Test comment',
    )
    get_comment_mock.return_value = APIControllerResponse(result=expected_comment)
    handler = CommandHandler()
    # WHEN
    result = handler.get_comment(key='PROJ-1', comment_id='123')
    # THEN
    get_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-1', comment_id='123')
    assert result == expected_comment


@patch.object(APIController, 'get_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comment_not_found(config_mock, get_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_comment_mock.return_value = APIControllerResponse(result=None)
    handler = CommandHandler()
    # WHEN
    result = handler.get_comment(key='PROJ-1', comment_id='999')
    # THEN
    get_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-1', comment_id='999')
    assert result is None


@patch.object(APIController, 'get_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_comment_failure(config_mock, get_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_comment_mock.return_value = APIControllerResponse(success=False, error='Access denied')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='An error occurred while fetching the comment.'):
        handler.get_comment(key='PROJ-2', comment_id='456')
    # THEN
    get_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-2', comment_id='456')


@patch.object(APIController, 'delete_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_delete_comment_success(config_mock, delete_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    delete_comment_mock.return_value = APIControllerResponse(success=True)
    handler = CommandHandler()
    # WHEN
    result = handler.delete_comment(key='PROJ-1', comment_id='123')
    # THEN
    delete_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-1', comment_id='123')
    assert result is True


@patch.object(APIController, 'delete_comment')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_delete_comment_failure(config_mock, delete_comment_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    delete_comment_mock.return_value = APIControllerResponse(
        success=False, error='Comment not found'
    )
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='An error occurred while trying to delete the comment'):
        handler.delete_comment(key='PROJ-2', comment_id='456')
    # THEN
    delete_comment_mock.assert_called_once_with(issue_key_or_id='PROJ-2', comment_id='456')


@pytest.mark.asyncio
@patch('jiratui.commands.handler.work_item_priority_has_changed')
@patch('jiratui.commands.handler.work_item_assignee_has_changed')
@patch.object(APIController, 'update_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_with_assignee_and_priority_changes(
    config_mock,
    get_issue_mock: AsyncMock,
    update_issue_mock: AsyncMock,
    work_item_assignee_has_changed_mock,
    work_item_priority_has_changed_mock,
    config_for_testing,
):
    # GIVEN
    config_mock.return_value = config_for_testing
    existing_issue = JiraIssue(
        id='1',
        status=IssueStatus(id='1', name='done'),
        key='PROJ-1',
        summary='Summary',
        assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        priority=IssuePriority(id='5', name='low'),
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[existing_issue])
    )
    work_item_assignee_has_changed_mock.return_value = True
    work_item_priority_has_changed_mock.return_value = True
    update_issue_mock.return_value = APIControllerResponse(
        result=UpdateWorkItemResponse(
            success=True, updated_fields=['summary', 'assignee', 'priority']
        )
    )
    handler = CommandHandler()
    # WHEN
    result = await handler.update_issue(
        key='PROJ-1', summary='New summary', assignee_account_id='user2', priority_id=3
    )
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    work_item_assignee_has_changed_mock.assert_called_once_with(
        JiraUser(
            account_id='1', active=True, display_name='Bart Simpson', email=None, username=None
        ),
        'user2',
    )
    work_item_priority_has_changed_mock.assert_called_once_with(
        IssuePriority(id='5', name='low'), '3'
    )
    update_issue_mock.assert_called_once()
    assert result is True


@pytest.mark.asyncio
@patch('jiratui.commands.handler.work_item_priority_has_changed')
@patch('jiratui.commands.handler.work_item_assignee_has_changed')
@patch.object(APIController, 'update_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_no_changes(
    config_mock,
    get_issue_mock: AsyncMock,
    update_issue_mock: AsyncMock,
    work_item_assignee_has_changed_mock,
    work_item_priority_has_changed_mock,
    config_for_testing,
):
    # GIVEN
    config_mock.return_value = config_for_testing
    existing_issue = JiraIssue(
        id='1',
        status=IssueStatus(id='1', name='done'),
        key='PROJ-1',
        summary='Summary',
        assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        priority=IssuePriority(id='5', name='low'),
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[existing_issue])
    )
    work_item_assignee_has_changed_mock.return_value = False
    work_item_priority_has_changed_mock.return_value = False
    handler = CommandHandler()
    # WHEN
    result = await handler.update_issue(key='PROJ-1')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    work_item_assignee_has_changed_mock.assert_called_once()
    work_item_priority_has_changed_mock.assert_called_once()
    update_issue_mock.assert_not_called()
    assert result is False


@pytest.mark.asyncio
@patch('jiratui.commands.handler.work_item_priority_has_changed')
@patch('jiratui.commands.handler.work_item_assignee_has_changed')
@patch.object(APIController, 'update_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_update_work_item_exception(
    config_mock,
    get_issue_mock: AsyncMock,
    update_issue_mock: AsyncMock,
    work_item_assignee_has_changed_mock,
    work_item_priority_has_changed_mock,
    config_for_testing,
):
    # GIVEN
    config_mock.return_value = config_for_testing
    existing_issue = JiraIssue(
        id='1',
        status=IssueStatus(id='1', name='done'),
        key='PROJ-1',
        summary='Summary',
        assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        priority=IssuePriority(id='5', name='low'),
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[existing_issue])
    )
    work_item_assignee_has_changed_mock.return_value = True
    work_item_priority_has_changed_mock.return_value = False
    update_issue_mock.side_effect = UpdateWorkItemException('Update failed')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='Unable to update the work item'):
        await handler.update_issue(key='PROJ-1', assignee_account_id='user2')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    update_issue_mock.assert_called_once()


@pytest.mark.asyncio
@patch('jiratui.commands.handler.work_item_priority_has_changed')
@patch('jiratui.commands.handler.work_item_assignee_has_changed')
@patch.object(APIController, 'update_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_validation_error(
    config_mock,
    get_issue_mock: AsyncMock,
    update_issue_mock: AsyncMock,
    work_item_assignee_has_changed_mock,
    work_item_priority_has_changed_mock,
    config_for_testing,
):
    # GIVEN
    config_mock.return_value = config_for_testing
    existing_issue = JiraIssue(
        id='1',
        status=IssueStatus(id='1', name='done'),
        key='PROJ-1',
        summary='Summary',
        assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        priority=IssuePriority(id='5', name='low'),
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[existing_issue])
    )
    work_item_assignee_has_changed_mock.return_value = False
    work_item_priority_has_changed_mock.return_value = True
    update_issue_mock.side_effect = ValidationError('Invalid priority')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='One or more fields are not valid'):
        await handler.update_issue(key='PROJ-1', priority_id=10)
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    update_issue_mock.assert_called_once()


@pytest.mark.asyncio
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_status_success(
    config_mock,
    get_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    config_for_testing,
):
    # GIVEN
    config_mock.return_value = config_for_testing
    existing_issue = JiraIssue(
        id='1',
        status=IssueStatus(id='1', name='done'),
        key='PROJ-1',
        summary='Summary',
        assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        priority=IssuePriority(id='5', name='low'),
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[existing_issue])
    )
    transition_issue_status_mock.return_value = APIControllerResponse(success=True)
    handler = CommandHandler()
    # WHEN
    result = await handler.update_issue_status(key='PROJ-1', status_id=3)
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transition_issue_status_mock.assert_called_once_with('PROJ-1', '3')
    assert result is True


@pytest.mark.asyncio
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_status_issue_not_found(
    config_mock, get_issue_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_issue_mock.return_value = APIControllerResponse(success=False, error='Issue not found')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='Unable to find the work item'):
        await handler.update_issue_status(key='PROJ-999', status_id=3)
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-999')


@pytest.mark.asyncio
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_update_issue_status_transition_failure(
    config_mock,
    get_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    config_for_testing,
):
    # GIVEN
    config_mock.return_value = config_for_testing
    existing_issue = JiraIssue(
        id='1',
        status=IssueStatus(id='1', name='done'),
        key='PROJ-1',
        summary='Summary',
        assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        priority=IssuePriority(id='5', name='low'),
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[existing_issue])
    )
    transition_issue_status_mock.return_value = APIControllerResponse(
        success=False, error='Invalid status transition'
    )
    handler = CommandHandler()
    # WHEN
    with pytest.raises(
        CLIException, match='Unable to transition the selected work item to the status with ID: 10.'
    ):
        await handler.update_issue_status(key='PROJ-1', status_id=10)
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transition_issue_status_mock.assert_called_once_with('PROJ-1', '10')


@patch.object(APIController, 'search_issues')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_search_issues_success(config_mock, search_issues_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_for_testing.search_results_default_order = WorkItemsSearchOrderBy.CREATED_DESC
    config_mock.return_value = config_for_testing
    expected_response = JiraIssueSearchResponse(
        issues=[
            JiraIssue(
                id='1',
                status=IssueStatus(id='1', name='done'),
                key='PROJ-1',
                summary='Summary 1',
                assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
                priority=IssuePriority(id='5', name='low'),
            ),
            JiraIssue(
                id='2',
                status=IssueStatus(id='1', name='done'),
                key='PROJ-2',
                summary='Summary 2',
                assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
                priority=IssuePriority(id='5', name='low'),
            ),
        ],
        total=2,
    )
    search_issues_mock.return_value = APIControllerResponse(result=expected_response)
    handler = CommandHandler()
    # WHEN
    result = handler.search_issues(
        project_key='PROJ',
        assignee_account_id='user1',
        limit=10,
        created_from=date(2026, 1, 1),
        created_until=date(2026, 5, 17),
    )
    # THEN
    search_issues_mock.assert_called_once_with(
        project_key='PROJ',
        fields=[
            'id',
            'key',
            'status',
            'summary',
            'created',
            'updated',
            'author',
            'reporter',
            'issuetype',
            'assignee',
        ],
        assignee='user1',
        limit=10,
        created_from=date(2026, 1, 1),
        created_until=date(2026, 5, 17),
        order_by=config_for_testing.search_results_default_order,
    )
    assert result == expected_response


@patch.object(APIController, 'search_issues')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_search_issues_failure(config_mock, search_issues_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_for_testing.search_results_default_order = WorkItemsSearchOrderBy.CREATED_DESC
    config_mock.return_value = config_for_testing
    search_issues_mock.return_value = APIControllerResponse(success=False, error='Search failed')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='Search failed'):
        handler.search_issues(project_key='PROJ')
    # THEN
    search_issues_mock.assert_called_once_with(
        project_key='PROJ',
        fields=[
            'id',
            'key',
            'status',
            'summary',
            'created',
            'updated',
            'author',
            'reporter',
            'issuetype',
            'assignee',
        ],
        assignee=None,
        limit=None,
        created_from=None,
        created_until=None,
        order_by=config_for_testing.search_results_default_order,
    )


@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_issue_success(config_mock, get_issue_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    expected_response = JiraIssueSearchResponse(
        issues=[
            JiraIssue(
                id='1',
                status=IssueStatus(id='1', name='done'),
                key='PROJ-1',
                summary='Summary 1',
                assignee=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
                priority=IssuePriority(id='5', name='low'),
            )
        ]
    )
    get_issue_mock.return_value = APIControllerResponse(result=expected_response)
    handler = CommandHandler()
    # WHEN
    result = handler.get_issue(key='PROJ-1', fields=['key', 'summary', 'status', 'assignee'])
    # THEN
    get_issue_mock.assert_called_once_with(
        issue_id_or_key='PROJ-1', fields=['key', 'summary', 'status', 'assignee']
    )
    assert result == expected_response


@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
def test_get_issue_failure(config_mock, get_issue_mock: AsyncMock, config_for_testing):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_issue_mock.return_value = APIControllerResponse(success=False, error='Issue not found')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(
        CLIException, match='An error occurred while trying to retrieve the work item.'
    ):
        handler.get_issue(key='PROJ-999')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-999', fields=None)


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_success_with_priority_and_issue_type(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    issue = JiraIssue(
        id='1',
        summary='Summary 1',
        key='PROJ-1',
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='10001', name='Bug'),
        priority=IssuePriority(id='3', name='Medium'),
        edit_meta={
            'fields': {
                'priority': {
                    'allowedValues': [
                        {'id': '1', 'name': 'Low'},
                        {'id': '3', 'name': 'Medium'},
                        {'id': '5', 'name': 'High'},
                    ]
                },
                'issuetype': {
                    'allowedValues': [
                        {'id': '10001', 'name': 'Bug', 'description': 'A bug'},
                        {'id': '10002', 'name': 'Task', 'description': 'A task'},
                    ]
                },
            }
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    transition1 = IssueTransition(id='1', name='To In Progress')
    transitions_mock.return_value = APIControllerResponse(result=[transition1])
    handler = CommandHandler()
    # WHEN
    result = await handler.get_metadata(key='PROJ-1')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transitions_mock.assert_called_once_with('PROJ-1')
    assert len(result['priorities']) == 3
    assert result['priorities'][0] == {'id': '1', 'name': 'Low'}
    assert len(result['types']) == 2
    assert result['types'][0] == {'id': '10001', 'name': 'Bug', 'description': 'A bug'}
    assert result['current_priority'] == '3'
    assert result['field_edit_metadata'] is None


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_no_edit_meta(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    issue = JiraIssue(
        id='1',
        summary='Summary 1',
        key='PROJ-1',
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='10001', name='Bug'),
        priority=IssuePriority(id='3', name='Medium'),
        edit_meta={},
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    transition1 = IssueTransition(id='1', name='To In Progress')
    transitions_mock.return_value = APIControllerResponse(result=[transition1])
    handler = CommandHandler()
    # WHEN
    result = await handler.get_metadata(key='PROJ-1')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transitions_mock.assert_called_once_with('PROJ-1')
    assert result['priorities'] == []
    assert result['types'] == []
    assert result['field_edit_metadata'] is None


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_priority_but_no_issue_type(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    issue = JiraIssue(
        id='1',
        summary='Summary 1',
        key='PROJ-1',
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='10001', name='Bug'),
        priority=IssuePriority(id='3', name='Medium'),
        edit_meta={
            'fields': {
                'priority': {
                    'allowedValues': [
                        {'id': '1', 'name': 'Low'},
                        {'id': '3', 'name': 'Medium'},
                    ]
                }
            }
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    transition1 = IssueTransition(id='1', name='To In Progress')
    transitions_mock.return_value = APIControllerResponse(result=[transition1])
    handler = CommandHandler()
    # WHEN
    result = await handler.get_metadata(key='PROJ-1')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transitions_mock.assert_called_once_with('PROJ-1')
    assert len(result['priorities']) == 2
    assert result['types'] == []
    assert result['field_edit_metadata'] is None


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_issue_type_but_no_priority(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    issue = JiraIssue(
        id='1',
        summary='Summary 1',
        key='PROJ-1',
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='10001', name='Bug'),
        priority=IssuePriority(id='3', name='Medium'),
        edit_meta={
            'fields': {
                'issuetype': {
                    'allowedValues': [
                        {'id': '10001', 'name': 'Bug', 'description': 'A bug'},
                        {'id': '10002', 'name': 'Task', 'description': 'A task'},
                    ]
                },
            }
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    transition1 = IssueTransition(id='1', name='To In Progress')
    transitions_mock.return_value = APIControllerResponse(result=[transition1])
    handler = CommandHandler()
    # WHEN
    result = await handler.get_metadata(key='PROJ-1')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transitions_mock.assert_called_once_with('PROJ-1')
    assert result['priorities'] == []
    assert len(result['types']) == 2
    assert result['field_edit_metadata'] is None


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_get_issue_failure(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_issue_mock.return_value = APIControllerResponse(success=False, error='Issue not found')
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='Issue not found'):
        await handler.get_metadata(key='PROJ-999')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-999')
    transitions_mock.assert_not_called()


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_success_with_unknown_field_id(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    issue = JiraIssue(
        id='1',
        summary='Summary 1',
        key='PROJ-1',
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='10001', name='Bug'),
        priority=IssuePriority(id='3', name='Medium'),
        edit_meta={
            'fields': {
                'priority': {
                    'allowedValues': [
                        {'id': '1', 'name': 'Low'},
                        {'id': '3', 'name': 'Medium'},
                        {'id': '5', 'name': 'High'},
                    ]
                },
                'issuetype': {
                    'allowedValues': [
                        {'id': '10001', 'name': 'Bug', 'description': 'A bug'},
                        {'id': '10002', 'name': 'Task', 'description': 'A task'},
                    ]
                },
            }
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    transition1 = IssueTransition(id='1', name='To In Progress')
    transitions_mock.return_value = APIControllerResponse(result=[transition1])
    handler = CommandHandler()
    # WHEN
    result = await handler.get_metadata(key='PROJ-1', field_id='some_field_id')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transitions_mock.assert_called_once_with('PROJ-1')
    assert len(result['priorities']) == 3
    assert result['priorities'][0] == {'id': '1', 'name': 'Low'}
    assert len(result['types']) == 2
    assert result['types'][0] == {'id': '10001', 'name': 'Bug', 'description': 'A bug'}
    assert result['current_priority'] == '3'
    assert result['field_edit_metadata'] is None


@pytest.mark.asyncio
@patch.object(APIController, 'transitions')
@patch.object(APIController, 'get_issue')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_metadata_success_with_known_field_id_metadata(
    config_mock, get_issue_mock: AsyncMock, transitions_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    issue = JiraIssue(
        id='1',
        summary='Summary 1',
        key='PROJ-1',
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='10001', name='Bug'),
        priority=IssuePriority(id='3', name='Medium'),
        edit_meta={
            'fields': {
                'priority': {
                    'allowedValues': [
                        {'id': '1', 'name': 'Low'},
                        {'id': '3', 'name': 'Medium'},
                        {'id': '5', 'name': 'High'},
                    ]
                },
                'issuetype': {
                    'allowedValues': [
                        {'id': '10001', 'name': 'Bug', 'description': 'A bug'},
                        {'id': '10002', 'name': 'Task', 'description': 'A task'},
                    ]
                },
            }
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    transition1 = IssueTransition(id='1', name='To In Progress')
    transitions_mock.return_value = APIControllerResponse(result=[transition1])
    handler = CommandHandler()
    # WHEN
    result = await handler.get_metadata(key='PROJ-1', field_id='priority')
    # THEN
    get_issue_mock.assert_called_once_with(issue_id_or_key='PROJ-1')
    transitions_mock.assert_called_once_with('PROJ-1')
    assert len(result['priorities']) == 3
    assert result['priorities'][0] == {'id': '1', 'name': 'Low'}
    assert len(result['types']) == 2
    assert result['types'][0] == {'id': '10001', 'name': 'Bug', 'description': 'A bug'}
    assert result['current_priority'] == '3'
    assert result['field_edit_metadata'] == {
        'field_id': 'priority',
        'metadata': {
            'allowedValues': [
                {'id': '1', 'name': 'Low'},
                {'id': '3', 'name': 'Medium'},
                {'id': '5', 'name': 'High'},
            ]
        },
    }


@pytest.mark.asyncio
@patch.object(APIController, 'get_issue_create_metadata')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_create_metadata_success(
    config_mock, get_issue_create_metadata_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    expected_metadata = {
        'fields': {
            'summary': {'name': 'Summary', 'required': True},
            'description': {'name': 'Description', 'required': False},
            'priority': {'name': 'Priority', 'required': True},
        }
    }
    get_issue_create_metadata_mock.return_value = APIControllerResponse(result=expected_metadata)
    handler = CommandHandler()
    # WHEN
    result = await handler.get_create_metadata(project_key='PROJ', work_item_type_id='10001')
    # THEN
    get_issue_create_metadata_mock.assert_called_once_with(
        project_id_or_key='PROJ',
        issue_type_id='10001',
    )
    assert result == {'metadata': expected_metadata}


@pytest.mark.asyncio
@patch.object(APIController, 'get_issue_create_metadata')
@patch('jiratui.commands.handler.ApplicationConfiguration')
async def test_get_create_metadata_failure(
    config_mock, get_issue_create_metadata_mock: AsyncMock, config_for_testing
):
    # GIVEN
    config_mock.return_value = config_for_testing
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        success=False, error='Project or issue type not found'
    )
    handler = CommandHandler()
    # WHEN
    with pytest.raises(CLIException, match='Project or issue type not found'):
        await handler.get_create_metadata(project_key='INVALID', work_item_type_id='99999')
    # THEN
    get_issue_create_metadata_mock.assert_called_once_with(
        project_id_or_key='INVALID',
        issue_type_id='99999',
    )
