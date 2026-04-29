from unittest.mock import AsyncMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import Attachment, JiraIssueSearchResponse, JiraUser
from jiratui.widgets.attachments.add import AddAttachmentScreen
from jiratui.widgets.attachments.attachments import (
    AttachmentsDataTable,
    IssueAttachmentsWidget,
    WorkItemAttachments,
)
from jiratui.widgets.screens import MainScreen


@patch.object(AddAttachmentScreen, '_get_initial_directory_for_upload')
@pytest.mark.asyncio
async def test_add_attachment_cancel_without_attaching_file(
    get_initial_directory_for_upload_mock: Mock, app
):
    # GIVEN
    get_initial_directory_for_upload_mock.return_value = ''
    async with app.run_test() as pilot:
        screen = AddAttachmentScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        # WHEN
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert screen.save_button.disabled is True
        assert screen.dismiss.call_args[0][0] == ''


@patch.object(AddAttachmentScreen, '_get_initial_directory_for_upload')
@pytest.mark.asyncio
async def test_add_attachment_save_with_filename(get_initial_directory_for_upload_mock: Mock, app):
    # GIVEN
    get_initial_directory_for_upload_mock.return_value = ''
    async with app.run_test() as pilot:
        screen = AddAttachmentScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        # WHEN
        await pilot.press('tab')
        await pilot.press('a')
        await pilot.press('tab')
        await pilot.press('enter')
        assert screen.save_button.disabled is False
        assert screen.dismiss.call_args[0][0].strip() == 'a'


@pytest.mark.parametrize('attachments', [None, WorkItemAttachments(None, None)])
@pytest.mark.asyncio
async def test_no_attachments_available(attachments, app):
    async with app.run_test():
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.attachments = attachments
        # THEN
        assert widget.issue_key is None
        assert AttachmentsDataTable not in widget.children


@pytest.mark.asyncio
async def test_sets_attachments(app):
    async with app.run_test():
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # THEN
        assert widget.issue_key == 'WI-1'
        assert len(widget.children) == 1
        assert isinstance(widget.children[0], AttachmentsDataTable)


@pytest.mark.asyncio
async def test_sets_attachments_with_empty_list(app):
    async with app.run_test():
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=None,
        )
        # THEN
        assert widget.issue_key == 'WI-1'
        assert len(widget.children) == 0


@patch.object(AddAttachmentScreen, '_get_initial_directory_for_upload')
@pytest.mark.asyncio
async def test_open_screen_to_add_attachment(get_initial_directory_for_upload_mock: Mock, app):
    # GIVEN
    get_initial_directory_for_upload_mock.return_value = ''
    async with app.run_test():
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=None,
        )
        # WHEN
        widget.action_add_attachment()
        # THEN
        assert isinstance(app.screen, AddAttachmentScreen)


@patch.object(AddAttachmentScreen, '_get_initial_directory_for_upload')
@pytest.mark.asyncio
async def test_open_screen_to_add_attachment_without_issue_key(
    get_initial_directory_for_upload_mock: Mock, app
):
    # GIVEN
    get_initial_directory_for_upload_mock.return_value = ''
    async with app.run_test():
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='',
            attachments=None,
        )
        # WHEN
        widget.action_add_attachment()
        # THEN
        assert isinstance(app.screen, MainScreen)


@patch.object(APIController, 'add_attachment')
@patch.object(AddAttachmentScreen, '_get_initial_directory_for_upload')
@pytest.mark.asyncio
async def test_upload_attachment(
    get_initial_directory_for_upload_mock: Mock, add_attachment_mock: Mock, app
):
    # GIVEN
    get_initial_directory_for_upload_mock.return_value = ''
    add_attachment_mock.return_value = APIControllerResponse(
        result=Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        )
    )
    async with app.run_test():
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        widget.upload_attachment('file3.txt')
        # THEN
        add_attachment_mock.assert_called_once_with('WI-1', 'file3.txt')
        assert isinstance(widget.children[0], AttachmentsDataTable)


@patch.object(IssueAttachmentsWidget, '_fetch_attachments_on_delete')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'delete_attachment')
@pytest.mark.asyncio
async def test_delete_attachment(
    delete_attachment_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    fetch_attachments_on_delete_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    fetch_attachments_on_delete_mock.return_value = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues[0:])
    )
    delete_attachment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        await widget._delete_attachment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_attachment_mock.assert_called_once_with('1')
        get_issue_mock.assert_called_once_with('WI-1', fields=['attachment'])
        assert widget.attachments == WorkItemAttachments(
            work_item_key='WI-1',
            attachments=jira_issues[0].attachments,
        )


@patch.object(IssueAttachmentsWidget, '_update_attachments_after_delete')
@patch.object(IssueAttachmentsWidget, '_fetch_attachments_on_delete')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'delete_attachment')
@pytest.mark.asyncio
async def test_delete_attachment_fails_to_fetch_issue(
    delete_attachment_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    fetch_attachments_on_delete_mock: Mock,
    update_attachments_after_delete_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    fetch_attachments_on_delete_mock.return_value = True
    get_issue_mock.return_value = APIControllerResponse(success=False)
    delete_attachment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        await widget._delete_attachment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_attachment_mock.assert_called_once_with('1')
        get_issue_mock.assert_called_once_with('WI-1', fields=['attachment'])
        update_attachments_after_delete_mock.assert_called_once_with('1')


@patch.object(IssueAttachmentsWidget, '_update_attachments_after_delete')
@patch.object(IssueAttachmentsWidget, '_fetch_attachments_on_delete')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'delete_attachment')
@pytest.mark.asyncio
async def test_delete_attachment_without_fetching_issues(
    delete_attachment_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    fetch_attachments_on_delete_mock: Mock,
    update_attachments_after_delete_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    fetch_attachments_on_delete_mock.return_value = False
    delete_attachment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        await widget._delete_attachment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_attachment_mock.assert_called_once_with('1')
        get_issue_mock.assert_not_called()
        update_attachments_after_delete_mock.assert_called_once_with('1')


@patch.object(IssueAttachmentsWidget, '_fetch_attachments_on_delete')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'delete_attachment')
@pytest.mark.asyncio
async def test_delete_attachment_without_fetching_issues_updates_datatable(
    delete_attachment_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    fetch_attachments_on_delete_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    fetch_attachments_on_delete_mock.return_value = False
    delete_attachment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        await widget._delete_attachment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_attachment_mock.assert_called_once_with('1')
        get_issue_mock.assert_not_called()
        assert widget.attachments == WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )


@patch.object(IssueAttachmentsWidget, '_update_attachments_after_delete')
@patch.object(IssueAttachmentsWidget, '_fetch_attachments_on_delete')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'delete_attachment')
@pytest.mark.asyncio
async def test_delete_attachment_fetch_issue_is_none(
    delete_attachment_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    fetch_attachments_on_delete_mock: Mock,
    update_attachments_after_delete_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    fetch_attachments_on_delete_mock.return_value = True
    get_issue_mock.return_value = APIControllerResponse(result=None)
    delete_attachment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        await widget._delete_attachment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_attachment_mock.assert_called_once_with('1')
        get_issue_mock.assert_called_once_with('WI-1', fields=['attachment'])
        update_attachments_after_delete_mock.assert_called_once_with('1')


@patch.object(IssueAttachmentsWidget, '_update_attachments_after_delete')
@patch.object(IssueAttachmentsWidget, '_fetch_attachments_on_delete')
@patch.object(APIController, 'get_issue')
@patch.object(APIController, 'delete_attachment')
@pytest.mark.asyncio
async def test_delete_attachment_fetch_issue_returns_no_issue(
    delete_attachment_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    fetch_attachments_on_delete_mock: Mock,
    update_attachments_after_delete_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    fetch_attachments_on_delete_mock.return_value = True
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    delete_attachment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueAttachmentsWidget()
        await app.screen.mount(widget)
        widget.attachments = WorkItemAttachments(
            work_item_key='WI-1',
            attachments=[
                Attachment(
                    id='1',
                    filename='file1.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
                Attachment(
                    id='2',
                    filename='file2.txt',
                    size=10,
                    mime_type='text/plain',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # WHEN
        await widget._delete_attachment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_attachment_mock.assert_called_once_with('1')
        get_issue_mock.assert_called_once_with('WI-1', fields=['attachment'])
        update_attachments_after_delete_mock.assert_called_once_with('1')
