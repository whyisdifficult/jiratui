from typing import cast
from unittest.mock import patch, AsyncMock

import pytest

from jiratui.api_controller.controller import APIController


@patch.object(APIController, 'search_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_without_project(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_users_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.users_autocomplete.set_project_key()
        # WHEN
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('e')
        await pilot.press('s')
        # THEN
        search_users_mock.assert_called_once_with(email_or_name='tes')

@patch.object(APIController, 'search_users_assignable_to_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_with_project(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_users_assignable_to_projects_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.users_autocomplete.set_project_key('PR1')
        # WHEN
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('e')
        await pilot.press('s')
        # THEN
        search_users_assignable_to_projects_mock.assert_called_once_with(['PR1'], query='tes')

@patch.object(APIController, 'search_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_with_short_query(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_users_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.users_autocomplete.set_project_key()
        # WHEN
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('e')
        # THEN
        app.save_screenshot()
        search_users_mock.assert_not_called()
