from typing import cast
from unittest.mock import AsyncMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.screens import MainScreen, WorkItemSearchResult
from jiratui.widgets.work_item_details.details import IssueDetailsWidget
from jiratui.widgets.work_item_details.flag_work_item import FlagWorkItemScreen


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_issue_has_no_metadata(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    selected_issue.edit_meta = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, MainScreen)


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_missing_metadata_for_flagged_field(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    selected_issue.edit_meta = {
        'fields': {
            'customfield_10021': {
                'required': False,
                'schema': {
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                    'customId': 10021,
                },
                'name': 'AnotherFieldName',
                'key': 'customfield_10021',
                'operations': ['add', 'set', 'remove'],
                'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
            },
        }
    }
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, MainScreen)


@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_flagging_enabled_issue_is_flagged(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = True
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is True  # type:ignore[name-defined] # noqa: F821
        assert 'Remove' in app.screen.root_container.border_title


@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_flagging_enabled_issue_is_not_flagged(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = []
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is False  # type:ignore[name-defined] # noqa: F821
        assert 'Add' in app.screen.root_container.border_title


@patch.object(IssueDetailsWidget, '_toggle_work_item_flag')
@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_dismiss_without_updating_flag_status(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    toggle_work_item_flag_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = []
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is False  # type:ignore[name-defined] # noqa: F821
        await pilot.press('escape')
        toggle_work_item_flag_mock.assert_not_called()


@patch.object(IssueDetailsWidget, '_toggle_work_item_flag')
@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_dismiss_without_updating_flag_status_clicking_cancel_button(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    toggle_work_item_flag_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = []
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is False  # type:ignore[name-defined] # noqa: F821
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        toggle_work_item_flag_mock.assert_not_called()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch('jiratui.widgets.screens.APIController.update_issue_flagged_status')
@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_updating_flag_status_clicking_save_button(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    update_issue_flagged_status_mock: AsyncMock,
    refresh_work_item_details_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = []
    update_issue_flagged_status_mock.return_value = APIControllerResponse()
    refresh_work_item_details_mock.return_value = None
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is False  # type:ignore[name-defined] # noqa: F821
        await pilot.press('-')
        await pilot.press('tab')
        await pilot.press('enter')
        update_issue_flagged_status_mock.assert_called_once_with(
            issue_id_or_key='key-2',
            note='-',
            add_flag=True,
        )
        refresh_work_item_details_mock.assert_called_once()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch('jiratui.widgets.screens.APIController.update_issue_flagged_status')
@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_updating_flag_status_clicking_save_button_without_note(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    update_issue_flagged_status_mock: AsyncMock,
    refresh_work_item_details_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = []
    update_issue_flagged_status_mock.return_value = APIControllerResponse()
    refresh_work_item_details_mock.return_value = None
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is False  # type:ignore[name-defined] # noqa: F821
        await pilot.press('tab')
        await pilot.press('enter')
        update_issue_flagged_status_mock.assert_called_once_with(
            issue_id_or_key='key-2',
            note=None,
            add_flag=True,
        )
        refresh_work_item_details_mock.assert_called_once()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch('jiratui.widgets.screens.APIController.update_issue_flagged_status')
@patch.object(JiraIssue, 'get_custom_field_value')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_flag_screen_updating_flag_status_clicking_save_button_update_fails(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_custom_field_value_mock: Mock,
    update_issue_flagged_status_mock: AsyncMock,
    refresh_work_item_details_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    selected_issue = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[selected_issue])
    )
    get_custom_field_value_mock.return_value = []
    update_issue_flagged_status_mock.return_value = APIControllerResponse(success=False)
    refresh_work_item_details_mock.return_value = None
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        assert isinstance(app.screen, MainScreen)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+f')
        assert isinstance(app.screen, FlagWorkItemScreen)
        assert app.screen._work_item_is_flagged is False  # type:ignore[name-defined] # noqa: F821
        await pilot.press('-')
        await pilot.press('tab')
        await pilot.press('enter')
        update_issue_flagged_status_mock.assert_called_once_with(
            issue_id_or_key='key-2',
            note='-',
            add_flag=True,
        )
        refresh_work_item_details_mock.assert_not_called()
