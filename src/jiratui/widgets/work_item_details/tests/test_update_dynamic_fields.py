from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.common.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    SelectionWidget,
    TextInputWidget,
    URLWidget,
)
from jiratui.widgets.screens import MainScreen, WorkItemSearchResult


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_multi_checkbox_custom_field_open_modal_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[0],
            MultiSelectWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[0].id
            == 'customfield_10021'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        # MultiSelectWidget is a SelectionList - it's directly focusable, no Input child
        assert isinstance(app.screen.focused, MultiSelectWidget)
        assert app.screen.focused.id == 'customfield_10021'
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update() == [{'id': '1'}]


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_multi_checkbox_custom_field_dismiss_modal_screen_without_changes(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[0],
            MultiSelectWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[0].id
            == 'customfield_10021'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        # MultiSelectWidget is a SelectionList - it's directly focusable, no Input child
        assert isinstance(app.screen.focused, MultiSelectWidget)
        assert app.screen.focused.id == 'customfield_10021'
        # Check that Option 1 is selected
        assert '1' in app.screen.focused.selected
        # get_value_for_update returns list of dicts with 'id' key only
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update() == [{'id': '1'}]
        # SelectionList doesn't open a modal - it's inline, so stay on MainScreen
        assert isinstance(app.screen, MainScreen)
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update() == [{'id': '1'}]


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_multi_checkbox_custom_field_modal_screen_press_update_without_changes(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[0],
            MultiSelectWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[0].id
            == 'customfield_10021'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        # MultiSelectWidget is a SelectionList - it's directly focusable, no Input child
        assert isinstance(app.screen.focused, MultiSelectWidget)
        assert app.screen.focused.id == 'customfield_10021'
        # Check initial value before making changes
        initial = app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update()
        assert initial == [{'id': '1'}]
        # MultiSelectWidget is inline (SelectionList), use space to toggle selections
        await pilot.press('down')
        await pilot.press('space')
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update() == [{'id': '1'}, {'id': '2'}]
        # Reset selection by pressing space again
        await pilot.press('space')
        await pilot.press('up')
        # Verify the selection was reset back to just Option 1
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update() == [{'id': '1'}]
        # Now toggle Option 2 to select both
        await pilot.press('down')
        await pilot.press('space')
        assert isinstance(app.screen, MainScreen)
        # Both Option 1 and Option 2 should now be selected
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container.children[
            0
        ].get_value_for_update() == [
            {'id': '1'},
            {'id': '2'},
        ]


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_url_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[1],
            URLWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[1].id
            == 'customfield_2'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, URLWidget)
        assert app.screen.focused.id == 'customfield_2'
        assert app.screen.focused.value == 'https://foo.bar'


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_url_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_2'] = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[1],
            URLWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[1].id
            == 'customfield_2'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, URLWidget)
        assert app.screen.focused.id == 'customfield_2'
        assert app.screen.focused.value == ''


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_float_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[2],
            NumericInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[2].id
            == 'customfield_3'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, NumericInputWidget)
        assert app.screen.focused.id == 'customfield_3'
        assert app.screen.focused.value == '12.34'


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_float_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_3'] = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[2],
            NumericInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[2].id
            == 'customfield_3'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, NumericInputWidget)
        assert app.screen.focused.id == 'customfield_3'
        assert app.screen.focused.value == ''


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_text_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[3],
            TextInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[3].id
            == 'customfield_4'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, TextInputWidget)
        assert app.screen.focused.id == 'customfield_4'
        assert app.screen.focused.value == 'hello world!'


@pytest.mark.parametrize('custom_field_value', [None, ''])
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_text_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    custom_field_value: str | None,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_4'] = custom_field_value
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[3],
            TextInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[3].id
            == 'customfield_4'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, TextInputWidget)
        assert app.screen.focused.id == 'customfield_4'
        assert app.screen.focused.value == ''


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_datetime_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[4],
            DateTimeInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[4].id
            == 'customfield_5'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, DateTimeInputWidget)
        assert app.screen.focused.id == 'customfield_5'
        assert app.screen.focused.value == '2025-12-30 11:22:33'


@pytest.mark.parametrize('custom_field_value', [None, ''])
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_datetime_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    custom_field_value: str | None,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_5'] = custom_field_value
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[4],
            DateTimeInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[4].id
            == 'customfield_5'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, DateTimeInputWidget)
        assert app.screen.focused.id == 'customfield_5'
        assert app.screen.focused.value == ''


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_date_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[5],
            DateInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[5].id
            == 'customfield_6'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, DateInputWidget)
        assert app.screen.focused.id == 'customfield_6'
        assert app.screen.focused.value == '2025-12-31'


@pytest.mark.parametrize('custom_field_value', [None, ''])
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_date_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    custom_field_value: str | None,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_6'] = custom_field_value
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[5],
            DateInputWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[5].id
            == 'customfield_6'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, DateInputWidget)
        assert app.screen.focused.id == 'customfield_6'
        assert app.screen.focused.value == ''


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_selection_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[6],
            SelectionWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[6].id
            == 'customfield_7'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, SelectionWidget)
        assert app.screen.focused.id == 'customfield_7'
        assert app.screen.focused.selection == '2'


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_selection_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_7'] = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[6],
            SelectionWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[6].id
            == 'customfield_7'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, SelectionWidget)
        assert app.screen.focused.id == 'customfield_7'
        assert app.screen.focused.selection is None


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_labels_with_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[7],
            LabelsWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[7].id
            == 'customfield_8'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, LabelsWidget)
        assert app.screen.focused.id == 'customfield_8'
        assert app.screen.focused.value == 'label1,label2'


@pytest.mark.parametrize('custom_field_value', [None, []])
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_custom_field_labels_without_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    custom_field_value: list | None,
    jira_issues_with_custom_fields: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_custom_fields[0].custom_fields['customfield_8'] = custom_field_value
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_custom_fields[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_custom_fields, next_page_token=None, is_last=None
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
        assert app.screen.issue_details_widget.dynamic_fields_widgets_container is not None
        assert isinstance(
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[7],
            LabelsWidget,
        )
        assert (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.children[7].id
            == 'customfield_8'
        )
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(app.screen.focused, LabelsWidget)
        assert app.screen.focused.id == 'customfield_8'
        assert app.screen.focused.value == ''


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_components_field_open_modal_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_components_field: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_components_field[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_components_field, next_page_token=None, is_last=None
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
        components_field = (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.query_one(
                '#components', MultiSelectWidget
            )
        )
        assert components_field is not None
        assert components_field.id == 'components'
        # Focus on the components field directly
        app.screen.set_focus(components_field)
        await pilot.pause()
        assert components_field.get_value_for_update() == [{'id': '2'}]
        await pilot.press('enter')


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_components_field_open_modal_screen_without_initial_value(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_components_field: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    jira_issues_with_components_field[0].components = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_components_field[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_components_field, next_page_token=None, is_last=None
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
        components_field = (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.query_one(
                '#components', MultiSelectWidget
            )
        )
        assert components_field is not None
        assert components_field.id == 'components'
        assert components_field.get_value_for_update() == []


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_components_field_dismiss_modal_screen_without_changes(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_components_field: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_components_field[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_components_field, next_page_token=None, is_last=None
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
        components_field = (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.query_one(
                '#components', MultiSelectWidget
            )
        )
        assert components_field is not None
        assert components_field.id == 'components'
        # Focus on the components field directly
        app.screen.set_focus(components_field)
        await pilot.pause()
        assert components_field.get_value_for_update() == [{'id': '2'}]
        await pilot.press('enter')
        await pilot.press('escape')
        assert isinstance(app.screen, MainScreen)
        # After pressing enter, Option 1 gets auto-selected
        assert components_field.get_value_for_update() == [{'id': '2'}, {'id': '1'}]


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_components_field_modal_screen_press_update_without_changes(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_components_field: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_components_field[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_components_field, next_page_token=None, is_last=None
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
        components_field = (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.query_one(
                '#components', MultiSelectWidget
            )
        )
        assert components_field is not None
        assert components_field.id == 'components'
        # Focus on the components field directly
        app.screen.set_focus(components_field)
        await pilot.pause()
        assert components_field.get_value_for_update() == [{'id': '2'}]
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('enter')
        assert isinstance(app.screen, MainScreen)
        # After pressing enter, Option 1 gets auto-selected
        assert components_field.get_value_for_update() == [{'id': '2'}, {'id': '1'}]


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_components_field_modal_screen_press_update_with_changes(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues_with_components_field: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.enable_updating_additional_fields = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues_with_components_field[0]])
    )
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues_with_components_field, next_page_token=None, is_last=None
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
        components_field = (
            app.screen.issue_details_widget.dynamic_fields_widgets_container.query_one(
                '#components', MultiSelectWidget
            )
        )
        assert components_field is not None
        assert components_field.id == 'components'
        # Focus on the components field directly
        app.screen.set_focus(components_field)
        await pilot.pause()
        assert components_field.get_value_for_update() == [{'id': '2'}]
        await pilot.press('enter')
        await pilot.press('space')
        await pilot.press('tab')
        await pilot.press('enter')
        assert isinstance(app.screen, MainScreen)
        # After pressing space on Option 1, it gets deselected, leaving only Option 2
        assert components_field.get_value_for_update() == [{'id': '2'}]
