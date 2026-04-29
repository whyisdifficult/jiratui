from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import IssueRemoteLink
from jiratui.widgets.remote_links.add import AddRemoteLinkScreen
from jiratui.widgets.remote_links.links import IssueRemoteLinkCollapsible, IssueRemoteLinksWidget
from jiratui.widgets.screens import MainScreen


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


@pytest.mark.asyncio
async def test_add_link_cancel_without_data(app):
    async with app.run_test() as pilot:
        # WHEN
        screen = AddRemoteLinkScreen()
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert screen.dismiss.call_args[0][0] == {}


@pytest.mark.asyncio
async def test_add_link_save_with_data(app):
    async with app.run_test() as pilot:
        screen = AddRemoteLinkScreen()
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('a')
        await pilot.press('.')
        await pilot.press('c')
        await pilot.press('o')
        await pilot.press('m')
        await pilot.press('tab')
        await pilot.press('a')
        await pilot.press('tab')
        await pilot.press('enter')
        assert screen.dismiss.call_args[0][0] == {
            'link_url': 'https://a.com',
            'link_title': 'a',
        }


@pytest.mark.asyncio
async def test_add_link_cancel_with_data(app):
    async with app.run_test() as pilot:
        screen = AddRemoteLinkScreen()
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('a')
        await pilot.press('.')
        await pilot.press('c')
        await pilot.press('o')
        await pilot.press('m')
        await pilot.press('tab')
        await pilot.press('a')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        assert screen.dismiss.call_args[0][0] == {}


@patch.object(IssueRemoteLinksWidget, 'fetch_remote_links')
@pytest.mark.asyncio
async def test_without_links_set(fetch_remote_links_mock: AsyncMock, app):
    async with app.run_test():
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.issue_key = None
        # THEN
        assert IssueRemoteLinkCollapsible not in widget.children
        fetch_remote_links_mock.assert_not_called()


@patch.object(APIController, 'get_issue_remote_links')
@pytest.mark.asyncio
async def test_with_links_set(get_issue_remote_links_mock: AsyncMock, app):
    # GIVEN
    get_issue_remote_links_mock.return_value = APIControllerResponse(
        result=[
            IssueRemoteLink(
                id='1',
                global_id='1',
                relationship='relates to',
                title='Link 1',
                summary='Link',
                url='http://foo.bar',
                application_name='Application 1',
                status_title='Ok',
                status_resolved=None,
            )
        ]
    )
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.issue_key = 'WI-1'
        await pilot.pause()
        # THEN
        assert widget.issue_key == 'WI-1'
        assert len(widget.children) == 1
        assert isinstance(widget.children[0], IssueRemoteLinkCollapsible)
        assert widget.children[0]._link_id == '1'
        assert widget.children[0]._work_item_key == 'WI-1'


@patch.object(APIController, 'get_issue_remote_links')
@pytest.mark.asyncio
async def test_with_empty_links(get_issue_remote_links_mock: AsyncMock, app):
    # GIVEN
    get_issue_remote_links_mock.return_value = APIControllerResponse(result=[])
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.issue_key = 'WI-1'
        await pilot.pause()
        # THEN
        assert widget.issue_key == 'WI-1'
        assert len(widget.children) == 0


@patch.object(APIController, 'get_issue_remote_links')
@pytest.mark.asyncio
async def test_with_error_fetching_links(get_issue_remote_links_mock: AsyncMock, app):
    # GIVEN
    get_issue_remote_links_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.issue_key = 'WI-1'
        await pilot.pause()
        # THEN
        assert widget.issue_key == 'WI-1'
        assert len(widget.children) == 0


@pytest.mark.asyncio
async def test_open_screen_to_add_link(app):
    async with app.run_test():
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        widget.issue_key = 'WI-1'
        # WHEN
        await widget.action_add_remote_link()
        # THEN
        assert isinstance(app.screen, AddRemoteLinkScreen)


@pytest.mark.asyncio
async def test_open_screen_to_add_link_without_work_item_key(app):
    async with app.run_test():
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        widget.issue_key = None
        # WHEN
        await widget.action_add_remote_link()
        # THEN
        assert isinstance(app.screen, MainScreen)


@patch.object(IssueRemoteLinksWidget, 'create_link')
@pytest.mark.asyncio
async def test_add_link_without_data(create_link_mock: AsyncMock, app):
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        widget.issue_key = 'WI-1'
        # WHEN
        widget.add_link({})
        await pilot.pause()
        # THEN
        create_link_mock.assert_not_called()


@patch.object(IssueRemoteLinksWidget, 'create_link')
@pytest.mark.asyncio
async def test_add_link_with_data(create_link_mock: AsyncMock, app):
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        widget.issue_key = 'WI-1'
        # WHEN
        widget.add_link({'link_url': 'foo.bar', 'link_title': 'Test'})
        await pilot.pause()
        # THEN
        create_link_mock.assert_called_once_with({'link_url': 'foo.bar', 'link_title': 'Test'})


@patch.object(IssueRemoteLinksWidget, 'fetch_remote_links')
@patch.object(APIController, 'create_issue_remote_link')
@pytest.mark.asyncio
async def test_add_link(
    create_issue_remote_link_mock: AsyncMock, fetch_remote_links_mock: Mock, app
):
    # GIVEN
    create_issue_remote_link_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        widget.issue_key = 'WI-1'
        # WHEN
        widget.add_link({'link_url': 'foo.bar', 'link_title': 'Test'})
        await pilot.pause()
        # THEN
        create_issue_remote_link_mock.assert_called_once_with('WI-1', 'foo.bar', 'Test')
        fetch_remote_links_mock.assert_has_calls([call('WI-1'), call('WI-1')])


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(APIController, 'delete_issue_remote_link')
@pytest.mark.asyncio
async def test_delete_link(
    delete_issue_remote_link_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    app,
):
    # GIVEN
    get_issue_remote_links_mock.return_value = APIControllerResponse(result=None)
    delete_issue_remote_link_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        widget = IssueRemoteLinksWidget()
        await app.screen.mount(widget)
        widget.issue_key = 'WI-1'
        # WHEN
        await widget._delete_link('WI-1', '1')
        await pilot.pause()
        # THEN
        delete_issue_remote_link_mock.assert_called_once_with('WI-1', '1')
        assert len(widget.children) == 0
