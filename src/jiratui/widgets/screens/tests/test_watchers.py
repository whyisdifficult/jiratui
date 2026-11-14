from unittest.mock import AsyncMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraUser, Watchers
from jiratui.widgets.screens.watchers import WorkItemWatchersScreen


@patch.object(APIController, 'get_work_item_watchers')
@pytest.mark.asyncio
async def test_open_watchers_screen_user_is_watching(
    get_work_item_watchers_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_watchers_mock.return_value = APIControllerResponse(
        success=True,
        result=Watchers(
            is_watching=True,
            count=1,
            watchers=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test():
        screen = WorkItemWatchersScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Watching - WI-1'
        assert screen.watching_status_field.content == 'Watching'
        assert screen.watching_status_field.styles.display == 'block'
        assert screen.watching_enabled is False
        assert screen.unwatching_enabled is True
        assert screen.datatable.border_subtitle == '1 watchers'
        assert screen.datatable.border_title == 'Watchers'
        get_work_item_watchers_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_watchers')
@pytest.mark.asyncio
async def test_open_watchers_screen_user_has_not_watched_with_watchers(
    get_work_item_watchers_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_watchers_mock.return_value = APIControllerResponse(
        success=True,
        result=Watchers(
            is_watching=False,
            count=1,
            watchers=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test():
        screen = WorkItemWatchersScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Watching - WI-1'
        assert screen.watching_status_field.content == ''
        assert screen.watching_status_field.styles.display == 'none'
        assert screen.datatable.border_title == 'Watchers'
        assert screen.datatable.border_subtitle == '1 watchers'
        assert len(screen.datatable.rows) == 1
        get_work_item_watchers_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_watchers')
@pytest.mark.asyncio
async def test_open_watchers_screen_user_has_not_watched_without_watchers(
    get_work_item_watchers_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_watchers_mock.return_value = APIControllerResponse(
        success=True,
        result=Watchers(
            is_watching=False,
            count=0,
            watchers=[],
        ),
    )
    async with app.run_test():
        screen = WorkItemWatchersScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Watching - WI-1'
        assert screen.watching_status_field.content == ''
        assert screen.watching_status_field.styles.display == 'none'
        assert not screen.datatable.display
        assert not screen.datatable.border_title
        assert not screen.datatable.border_subtitle
        assert len(screen.datatable.rows) == 0
        assert screen.message.content == 'The work item does not have watchers yet'
        assert screen.watching_enabled is True
        assert screen.unwatching_enabled is False
        get_work_item_watchers_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_watchers')
@pytest.mark.asyncio
async def test_open_watchers_screen_fetching_watchers_data_fails(
    get_work_item_watchers_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_watchers_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        screen = WorkItemWatchersScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Watching - WI-1'
        assert screen.watching_status_field.content == ''
        assert screen.watching_status_field.styles.display == 'none'
        assert not screen.datatable.display
        assert not screen.datatable.border_title
        assert not screen.datatable.border_subtitle
        assert len(screen.datatable.rows) == 0
        assert screen.message.content == 'Failed to retrieve watch data'
        assert screen.message.display is True
        assert screen.watching_enabled is True
        assert screen.unwatching_enabled is False
        get_work_item_watchers_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_watchers')
@pytest.mark.asyncio
async def test_open_watchers_screen_user_wants_to_watch_issue(
    get_work_item_watchers_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_watchers_mock.return_value = APIControllerResponse(
        success=True,
        result=Watchers(
            is_watching=False,
            count=1,
            watchers=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test() as pilot:
        screen = WorkItemWatchersScreen('WI-1')
        await app.push_screen(screen)
        screen.dismiss = Mock()
        # WHEN
        await pilot.press('a')
        # THEN
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
        assert screen.dismiss.call_args[0][0].watch is True
        assert screen.dismiss.call_args[0][0].update is True


@patch.object(APIController, 'get_work_item_watchers')
@pytest.mark.asyncio
async def test_open_watchers_screen_user_wants_to_unwatch_issue(
    get_work_item_watchers_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_watchers_mock.return_value = APIControllerResponse(
        success=True,
        result=Watchers(
            is_watching=True,
            count=1,
            watchers=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test() as pilot:
        screen = WorkItemWatchersScreen('WI-1')
        await app.push_screen(screen)
        screen.dismiss = Mock()
        # WHEN
        await pilot.press('x')
        # THEN
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
        assert screen.dismiss.call_args[0][0].watch is False
        assert screen.dismiss.call_args[0][0].update is True
