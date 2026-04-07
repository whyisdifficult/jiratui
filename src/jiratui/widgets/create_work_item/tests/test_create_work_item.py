from unittest.mock import AsyncMock, PropertyMock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import IssueType, Project
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value=None))
@patch.object(APIController, 'get_user')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    get_user_mock: AsyncMock,
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_not_called()
        get_user_mock.assert_not_called()


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value=None))
@patch.object(APIController, 'get_issue_create_metadata')
@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'search_users')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen_search_assignee_and_reporter(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    search_users_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    get_issue_create_metadata_mock: AsyncMock,
    projects: list[Project],
    issue_types: list[IssueType],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    # GIVEN
    search_projects_mock.return_value = APIControllerResponse(result=projects)
    get_issue_types_for_project_mock.return_value = APIControllerResponse(result=issue_types)
    get_issue_create_metadata_mock.return_value = APIControllerResponse(result=[])
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('s')
        await pilot.press('t')
        await pilot.press('tab')
        await pilot.press('q')
        await pilot.press('w')
        await pilot.press('r')
        await pilot.press('tab')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_called_once_with('P1')
        search_users_mock.assert_called_once_with(email_or_name='tst')
        search_users_assignable_to_issue_mock.assert_called_once_with(
            project_id_or_key='P1', query='qwr'
        )
        get_issue_create_metadata_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value=None))
@patch.object(APIController, 'get_issue_create_metadata')
@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'search_users')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen_search_reporter_only(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    search_users_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    get_issue_create_metadata_mock: AsyncMock,
    projects: list[Project],
    issue_types: list[IssueType],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    # GIVEN
    search_projects_mock.return_value = APIControllerResponse(result=projects)
    get_issue_types_for_project_mock.return_value = APIControllerResponse(result=issue_types)
    get_issue_create_metadata_mock.return_value = APIControllerResponse(result=[])
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('s')
        await pilot.press('t')
        await pilot.press('tab')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_called_once_with('P1')
        search_users_mock.assert_called_once_with(email_or_name='tst')
        search_users_assignable_to_issue_mock.assert_not_called()
        get_issue_create_metadata_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value='12345'))
@patch.object(APIController, 'get_user')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen_with_reporter_account_id(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    get_user_mock: AsyncMock,
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_user_mock.return_value = APIControllerResponse(result=None)
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_not_called()
        get_user_mock.assert_called_once_with('12345')
