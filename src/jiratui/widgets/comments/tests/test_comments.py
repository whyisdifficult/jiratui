from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import IssueComment, JiraUser
from jiratui.widgets.comments.add import AddCommentScreen
from jiratui.widgets.comments.comments import (
    CommentCollapsible,
    IssueCommentsWidget,
    WorkItemComments,
)
from jiratui.widgets.screens import MainScreen


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


@pytest.mark.asyncio
async def test_add_comment_cancel_without_comment(app):
    async with app.run_test() as pilot:
        # WHEN
        screen = AddCommentScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('escape')
        await pilot.press('enter')
        # THEN
        assert screen.dismiss.call_args[0][0] == ''


@pytest.mark.asyncio
async def test_add_comment_save_with_comment(app):
    async with app.run_test() as pilot:
        screen = AddCommentScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('tab')
        await pilot.press('a')
        await pilot.press(' ')
        await pilot.press('escape')
        await pilot.press('enter')
        assert screen.dismiss.call_args[0][0].strip() == 'a'


@pytest.mark.asyncio
async def test_add_comment_save_button_enabled_with_non_empty_comment(app):
    async with app.run_test() as pilot:
        screen = AddCommentScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('tab')
        await pilot.press('a')
        assert screen.save_button.disabled is False


@pytest.mark.asyncio
async def test_add_comment_cancel_with_comment(app):
    async with app.run_test() as pilot:
        screen = AddCommentScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('tab')
        await pilot.press('a')
        await pilot.press('escape')
        await pilot.press('tab')
        await pilot.press('enter')
        assert screen.dismiss.call_args[0][0].strip() == ''


@pytest.mark.asyncio
async def test_no_comments_available(app):
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.comments = None
        # THEN
        assert widget._work_item_key is None
        assert CommentCollapsible not in widget.children


@pytest.mark.asyncio
async def test_sets_comments(mock_configuration, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.comments = WorkItemComments(
            work_item_key='WI-1',
            comments=[
                IssueComment(
                    id='1',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                    body='I will study',
                ),
                IssueComment(
                    id='2',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                ),
            ],
        )
        # THEN
        assert widget._work_item_key == 'WI-1'
        assert len(widget.children) == 2
        assert isinstance(widget.children[0], CommentCollapsible)
        assert widget.children[0]._comment_id == '1'
        assert widget.children[0]._work_item_key == 'WI-1'
        assert widget.children[1]._comment_id == '2'
        assert widget.children[1]._work_item_key == 'WI-1'


@pytest.mark.asyncio
async def test_sets_comments_with_empty_list(mock_configuration, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.comments = WorkItemComments(work_item_key='WI-1', comments=None)
        # THEN
        assert widget._work_item_key == 'WI-1'
        assert len(widget.children) == 0


@pytest.mark.asyncio
async def test_open_screen_to_add_comment_without_existing_comments(app):
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(work_item_key='WI-1')
        # WHEN
        widget.action_add_comment()
        # THEN
        assert isinstance(app.screen, AddCommentScreen)


@pytest.mark.asyncio
async def test_open_screen_to_add_comment_without_existing_comments_and_without_work_item(app):
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments()
        # WHEN
        widget.action_add_comment()
        # THEN
        assert isinstance(app.screen, MainScreen)


@pytest.mark.asyncio
async def test_open_screen_to_add_comment_with_existing_comments(mock_configuration, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(
            work_item_key='WI-1',
            comments=[
                IssueComment(
                    id='1',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                    body='I will study',
                )
            ],
        )
        # WHEN
        widget.action_add_comment()
        # THEN
        assert isinstance(app.screen, AddCommentScreen)


@patch.object(IssueCommentsWidget, '_add_comment_to_issue')
@pytest.mark.asyncio
async def test_save_empty_comment(add_comment_to_issue_mock: Mock, app):
    async with app.run_test():
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(work_item_key='WI-1')
        # WHEN
        widget._save_comment('')
        # THEN
        add_comment_to_issue_mock.assert_not_called()


@patch.object(APIController, 'get_comments')
@patch.object(APIController, 'add_comment')
@pytest.mark.asyncio
async def test_save_comment(
    add_comment_mock: AsyncMock,
    get_comments_mock: AsyncMock,
    mock_configuration,
    app,
):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    get_comments_mock.return_value = APIControllerResponse(
        result=[
            IssueComment(
                id='1',
                author=JiraUser(account_id='1', active=True, display_name='Bart'),
                body='I will study',
            )
        ]
    )
    add_comment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(work_item_key='WI-1')
        # WHEN
        widget._save_comment('test ')
        await pilot.pause()
        # THEN
        add_comment_mock.assert_called_once_with('WI-1', 'test')
        get_comments_mock.assert_called_once_with('WI-1')
        assert isinstance(widget.children[0], CommentCollapsible)
        assert widget.children[0]._comment_id == '1'


@patch.object(APIController, 'get_comments')
@patch.object(APIController, 'add_comment')
@pytest.mark.asyncio
async def test_save_comment_no_comments_found(
    add_comment_mock: AsyncMock,
    get_comments_mock: AsyncMock,
    mock_configuration,
    app,
):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    get_comments_mock.return_value = APIControllerResponse(result=None)
    add_comment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(work_item_key='WI-1')
        # WHEN
        widget._save_comment('test ')
        await pilot.pause()
        # THEN
        add_comment_mock.assert_called_once_with('WI-1', 'test')
        get_comments_mock.assert_called_once_with('WI-1')
        assert len(widget.children) == 0


@patch('jiratui.utils.urls.CONFIGURATION')
@patch.object(IssueCommentsWidget, '_fetch_comments_on_delete')
@patch.object(APIController, 'get_comments')
@patch.object(APIController, 'delete_comment')
@pytest.mark.asyncio
async def test_delete_comment(
    delete_comment_mock: AsyncMock,
    get_comments_mock: AsyncMock,
    fetch_comments_on_delete_mock: Mock,
    urls_config_mock: Mock,
    app,
):
    # GIVEN
    urls_config_mock.jira_base_url = 'http://foo.bar'
    fetch_comments_on_delete_mock.fetch_comments_on_delete = True
    get_comments_mock.return_value = APIControllerResponse(result=None)
    delete_comment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(
            work_item_key='WI-1',
            comments=[
                IssueComment(
                    id='1',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                    body='I will study',
                ),
            ],
        )
        # WHEN
        await widget._delete_comment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_comment_mock.assert_called_once_with('WI-1', '1')
        get_comments_mock.assert_called_once_with('WI-1')
        assert len(widget.children) == 0


@patch('jiratui.utils.urls.CONFIGURATION')
@patch.object(IssueCommentsWidget, '_fetch_comments_on_delete')
@patch.object(APIController, 'get_comments')
@patch.object(APIController, 'delete_comment')
@pytest.mark.asyncio
async def test_delete_comment_comments_left(
    delete_comment_mock: AsyncMock,
    get_comments_mock: AsyncMock,
    fetch_comments_on_delete_mock: Mock,
    urls_config_mock: Mock,
    config_for_testing,
    app,
):
    # GIVEN
    fetch_comments_on_delete_mock.fetch_comments_on_delete = True
    urls_config_mock.configure_mock(jira_base_url='foo.bar')
    get_comments_mock.return_value = APIControllerResponse(
        result=[
            IssueComment(
                id='2',
                author=JiraUser(account_id='1', active=True, display_name='Bart'),
                body='I will study',
            )
        ]
    )
    delete_comment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(
            work_item_key='WI-1',
            comments=[
                IssueComment(
                    id='1',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                    body='I will study',
                )
            ],
        )
        # WHEN
        await widget._delete_comment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_comment_mock.assert_called_once_with('WI-1', '1')
        get_comments_mock.assert_called_once_with('WI-1')
        assert len(widget.children) == 1


@patch.object(IssueCommentsWidget, '_fetch_comments_on_delete')
@patch('jiratui.utils.urls.CONFIGURATION')
@patch.object(APIController, 'get_comments')
@patch.object(APIController, 'delete_comment')
@pytest.mark.asyncio
async def test_delete_comment_comments_left_without_getting_comments(
    delete_comment_mock: AsyncMock,
    get_comments_mock: AsyncMock,
    urls_config_mock: Mock,
    fetch_comments_on_delete_mock: Mock,
    app,
):
    # GIVEN
    fetch_comments_on_delete_mock.return_value = False
    urls_config_mock.configure_mock(jira_base_url='foo.bar')
    delete_comment_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueCommentsWidget()
        await app.screen.mount(widget)
        widget.comments = WorkItemComments(
            work_item_key='WI-1',
            comments=[
                IssueComment(
                    id='1',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                    body='I will study',
                ),
                IssueComment(
                    id='2',
                    author=JiraUser(account_id='1', active=True, display_name='Bart'),
                    body='I will study',
                ),
            ],
        )
        # WHEN
        await widget._delete_comment('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_comment_mock.assert_called_once_with('WI-1', '1')
        get_comments_mock.assert_not_called()
        assert len(widget.children) == 1
