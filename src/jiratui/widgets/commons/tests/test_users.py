from unittest.mock import AsyncMock, PropertyMock, patch

import pytest

from jiratui.api_controller.controller import APIController
from jiratui.widgets.filters import ProjectSelectionInput


@patch.object(ProjectSelectionInput, 'selection', PropertyMock(return_value=None))
@patch.object(APIController, 'search_users_assignable_to_issue')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_with_custom_search_function(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('e')
        await pilot.press('s')
        # THEN
        search_users_assignable_to_issue_mock.assert_called_once_with(
            project_id_or_key=None, query='tes'
        )


@patch.object(ProjectSelectionInput, 'selection', PropertyMock(return_value='PR1'))
@patch.object(APIController, 'search_users_assignable_to_issue')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_by_project_with_custom_search_function(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('e')
        await pilot.press('s')
        # THEN
        search_users_assignable_to_issue_mock.assert_called_once_with(
            project_id_or_key='PR1', query='tes'
        )
