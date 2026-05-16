from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import (
    IssuePriority,
    IssueStatus,
    IssueType,
    JiraIssue,
    JiraIssueSearchResponse,
    Project,
    RelatedJiraIssue,
)
from jiratui.widgets.confirmation_screen import ConfirmationScreen
from jiratui.widgets.related_work_items.add import AddWorkItemRelationshipScreen
from jiratui.widgets.related_work_items.related_issues import (
    RelatedIssueCollapsible,
    RelatedIssuesWidget,
)
from jiratui.widgets.screens import MainScreen
from jiratui.widgets.work_item_details.read_only_details import WorkItemReadOnlyDetailsScreen


@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'link_work_items')
@pytest.mark.asyncio
async def test_link_work_items_link_creation_success_false(
    link_work_items_mock: AsyncMock, get_issue_mock: AsyncMock, app
):
    # GIVEN
    data = {
        'right_issue_key': 'WI-2',
        'link_type': '1',
        'link_type_id': '2',
    }
    link_work_items_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.link_work_items(data)
        # THEN
        get_issue_mock.assert_not_called()
        link_work_items_mock.assert_called_once_with(
            left_issue_key='WI-1',
            right_issue_key='WI-2',
            link_type='1',
            link_type_id='2',
        )


@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'link_work_items')
@pytest.mark.asyncio
async def test_link_work_items_no_related_issues_found(
    link_work_items_mock: AsyncMock, get_issue_mock: AsyncMock, app
):
    # GIVEN
    data = {
        'right_issue_key': 'WI-2',
        'link_type': '1',
        'link_type_id': '2',
    }
    link_work_items_mock.return_value = APIControllerResponse()
    get_issue_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.link_work_items(data)
        # THEN
        assert widget.issues is None
        get_issue_mock.assert_called_once_with('WI-1', fields=['issuelinks'])
        link_work_items_mock.assert_called_once_with(
            left_issue_key='WI-1',
            right_issue_key='WI-2',
            link_type='1',
            link_type_id='2',
        )


@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'link_work_items')
@pytest.mark.asyncio
async def test_link_work_items_no_related_issues_found_none(
    link_work_items_mock: AsyncMock, get_issue_mock: AsyncMock, app
):
    # GIVEN
    data = {
        'right_issue_key': 'WI-2',
        'link_type': '1',
        'link_type_id': '2',
    }
    link_work_items_mock.return_value = APIControllerResponse()
    get_issue_mock.return_value = APIControllerResponse(result=None)
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.link_work_items(data)
        # THEN
        assert widget.issues is None
        get_issue_mock.assert_called_once_with('WI-1', fields=['issuelinks'])
        link_work_items_mock.assert_called_once_with(
            left_issue_key='WI-1',
            right_issue_key='WI-2',
            link_type='1',
            link_type_id='2',
        )


@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'link_work_items')
@pytest.mark.asyncio
async def test_link_work_items_no_related_issues_found_empty_list(
    link_work_items_mock: AsyncMock, get_issue_mock: AsyncMock, app
):
    # GIVEN
    data = {
        'right_issue_key': 'WI-2',
        'link_type': '1',
        'link_type_id': '2',
    }
    link_work_items_mock.return_value = APIControllerResponse()
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.link_work_items(data)
        # THEN
        assert widget.issues is None
        get_issue_mock.assert_called_once_with('WI-1', fields=['issuelinks'])
        link_work_items_mock.assert_called_once_with(
            left_issue_key='WI-1',
            right_issue_key='WI-2',
            link_type='1',
            link_type_id='2',
        )


@patch('jiratui.widgets.related_work_items.related_issues.build_external_url_for_issue')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'link_work_items')
@pytest.mark.asyncio
async def test_link_work_items(
    link_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    build_external_url_for_issue_mock: Mock,
    app,
):
    # GIVEN
    build_external_url_for_issue_mock.return_value = 'foo.bar'
    data = {
        'right_issue_key': 'WI-2',
        'link_type': '1',
        'link_type_id': '2',
    }
    link_work_items_mock.return_value = APIControllerResponse()
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(
            issues=[
                JiraIssue(
                    id='1',
                    key='key-1',
                    summary='abcd',
                    project=Project(id='2', name='Project 2', key='P2'),
                    created=datetime(2025, 10, 31),
                    updated=datetime(2025, 10, 31),
                    status=IssueStatus(name='Done', id='1'),
                    issue_type=IssueType(id='1', name='Task'),
                    related_issues=[
                        RelatedJiraIssue(
                            id='1',
                            key='key-1',
                            summary='abcd',
                            status=IssueStatus(name='Done', id='1'),
                            issue_type=IssueType(id='1', name='Task'),
                        ),
                        RelatedJiraIssue(
                            id='2',
                            key='key-2',
                            summary='qwerty',
                            status=IssueStatus(name='Done', id='1'),
                            issue_type=IssueType(id='1', name='Task'),
                        ),
                    ],
                )
            ]
        )
    )
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.link_work_items(data)
        # THEN
        assert widget.issues == [
            RelatedJiraIssue(
                id='1',
                key='key-1',
                summary='abcd',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
            ),
            RelatedJiraIssue(
                id='2',
                key='key-2',
                summary='qwerty',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
            ),
        ]
        get_issue_mock.assert_called_once_with('WI-1', fields=['issuelinks'])
        link_work_items_mock.assert_called_once_with(
            left_issue_key='WI-1',
            right_issue_key='WI-2',
            link_type='1',
            link_type_id='2',
        )


@patch('jiratui.widgets.related_work_items.related_issues.build_external_url_for_issue')
@pytest.mark.asyncio
async def test_related_issues_widget_set_issues(
    build_external_url_for_issue_mock: Mock,
    app,
):
    # GIVEN
    build_external_url_for_issue_mock.return_value = 'foo.bar'
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        widget.issues = [
            RelatedJiraIssue(
                id='1',
                key='key-1',
                summary='abcd',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
            ),
            RelatedJiraIssue(
                id='2',
                key='key-2',
                summary='qwerty',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
                priority=IssuePriority(id='1', name='Medium'),
            ),
        ]
        # THEN
        assert widget.issues == [
            RelatedJiraIssue(
                id='1',
                key='key-1',
                summary='abcd',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
            ),
            RelatedJiraIssue(
                id='2',
                key='key-2',
                summary='qwerty',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
                priority=IssuePriority(id='1', name='Medium'),
            ),
        ]
        assert len(list(widget.query_children(RelatedIssueCollapsible))) == 2


@pytest.mark.asyncio
async def test_action_link_work_item_with_issue_key_set(app):
    # GIVEN
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.action_link_work_item()
        # THEN
        assert isinstance(app.screen, AddWorkItemRelationshipScreen)


@pytest.mark.asyncio
async def test_action_link_work_item_without_issue_key_set(app):
    # GIVEN
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = None
        # WHEN
        await widget.action_link_work_item()
        # THEN
        assert isinstance(app.screen, MainScreen)


@pytest.mark.asyncio
async def test_action_unlink_work_item_opens_modal_screen_to_confirm(app):
    # GIVEN
    async with app.run_test():
        widget = RelatedIssueCollapsible(work_item_key='WI-1', link_id='1')
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = None
        # WHEN
        await widget.action_unlink_work_item()
        # THEN
        assert isinstance(app.screen, ConfirmationScreen)


@pytest.mark.asyncio
async def test_action_view_work_item_opens_modal_screen_to_view(app):
    # GIVEN
    async with app.run_test():
        widget = RelatedIssueCollapsible(work_item_key='WI-1', link_id='1')
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = None
        # WHEN
        await widget.action_view_work_item()
        # THEN
        assert isinstance(app.screen, WorkItemReadOnlyDetailsScreen)


@patch.object(APIController, 'delete_issue_link')
@pytest.mark.asyncio
async def test_delete_link(delete_issue_link_mock: AsyncMock, app):
    # GIVEN
    delete_issue_link_mock.return_value = APIControllerResponse()
    async with app.run_test():
        widget = RelatedIssueCollapsible(work_item_key='WI-1', link_id='1')
        await app.screen.mount(widget)
        # WHEN
        await widget.delete_link()
        # THEN
        delete_issue_link_mock.assert_called_once_with('1')


@patch.object(APIController, 'delete_issue_link')
@pytest.mark.asyncio
async def test_delete_link_delete_fails(delete_issue_link_mock: AsyncMock, app):
    # GIVEN
    delete_issue_link_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        widget = RelatedIssueCollapsible(work_item_key='WI-1', link_id='1')
        await app.screen.mount(widget)
        # WHEN
        await widget.delete_link()
        # THEN
        delete_issue_link_mock.assert_called_once_with('1')


@patch('jiratui.widgets.related_work_items.related_issues.build_external_url_for_issue')
@pytest.mark.asyncio
async def test_refresh_issues_after_delete(
    build_external_url_for_issue_mock: Mock,
    app,
):
    # GIVEN
    build_external_url_for_issue_mock.return_value = 'foo.bar'
    async with app.run_test():
        widget = RelatedIssuesWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue_key = 'WI-1'
        widget.issues = [
            RelatedJiraIssue(
                id='1',
                key='key-1',
                summary='abcd',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
            ),
            RelatedJiraIssue(
                id='2',
                key='key-2',
                summary='qwerty',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
                priority=IssuePriority(id='1', name='Medium'),
            ),
        ]
        # WHEN
        widget._refresh_issues_after_delete(RelatedIssueCollapsible.LinkDeleted(link_id='1'))
        # THEN
        assert widget.issues == [
            RelatedJiraIssue(
                id='2',
                key='key-2',
                summary='qwerty',
                status=IssueStatus(name='Done', id='1'),
                issue_type=IssueType(id='1', name='Task'),
                priority=IssuePriority(id='1', name='Medium'),
            )
        ]
