from typing import Type, cast
from unittest.mock import AsyncMock, patch

import pytest
from textual.widgets import Markdown, Static, TextArea

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.attachments.attachments import (
    AttachmentsDataTable,
    FileAttachmentWidget,
    ViewAttachmentScreen,
)
from jiratui.widgets.screens import MainScreen, WorkItemSearchResult


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_focus_attachments_datatable(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('6')
        await pilot.press('tab')
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert main_screen.issue_attachments_widget.issue_key == 'key-2'
        attachment_dt = main_screen.issue_attachments_widget.query_one(AttachmentsDataTable)
        assert attachment_dt.has_focus


@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_focus_attachments_datatable_highlight_file(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('6')
        await pilot.press('tab')
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert main_screen.issue_attachments_widget.issue_key == 'key-2'
        attachment_dt = main_screen.issue_attachments_widget.query_one(AttachmentsDataTable)
        assert attachment_dt.has_focus
        assert attachment_dt._selected_attachment_file_type == 'text/csv'
        assert attachment_dt._selected_attachment_file_name == 'file-one.csv'


@patch('jiratui.widgets.screens.APIController.get_attachment_content')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_attachment_download_fails(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_attachment_content_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_attachment_content_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('v')
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert main_screen.issue_attachments_widget.issue_key == 'key-2'
        attachment_dt = main_screen.issue_attachments_widget.query_one(AttachmentsDataTable)
        assert attachment_dt.has_focus
        assert attachment_dt._selected_attachment_file_type == 'text/csv'
        assert attachment_dt._selected_attachment_file_name == 'file-one.csv'
        assert isinstance(app.screen, ViewAttachmentScreen)
        get_attachment_content_mock.assert_called_once_with('1')
        assert isinstance(app.screen.center_widget.children[0], Static)
        assert (
            app.screen.center_widget.children[0].content == 'Unable to download the attached file'
        )


@patch('jiratui.widgets.screens.APIController.get_attachment_content')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_show_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_attachment_content_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_attachment_content_mock.return_value = APIControllerResponse(result='csv content'.encode())
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('v')
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert main_screen.issue_attachments_widget.issue_key == 'key-2'
        attachment_dt = main_screen.issue_attachments_widget.query_one(AttachmentsDataTable)
        assert attachment_dt.has_focus
        assert attachment_dt._selected_attachment_file_type == 'text/csv'
        assert attachment_dt._selected_attachment_file_name == 'file-one.csv'
        assert isinstance(app.screen, ViewAttachmentScreen)
        get_attachment_content_mock.assert_called_once_with('1')
        assert isinstance(app.screen.center_widget.children[0], TextArea)
        assert app.screen.center_widget.children[0].text == 'csv content'
        assert app.screen.center_widget.children[0].language is None
        assert app.screen.center_widget.children[0].read_only is True


@patch('jiratui.widgets.screens.APIController.get_attachment_content')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_show_attachment_with_language(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_attachment_content_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_attachment_content_mock.return_value = APIControllerResponse(
        result='<xml> content'.encode()
    )
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('down')
        await pilot.press('down')
        await pilot.press('v')
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert main_screen.issue_attachments_widget.issue_key == 'key-2'
        attachment_dt = main_screen.issue_attachments_widget.query_one(AttachmentsDataTable)
        assert attachment_dt.has_focus
        assert attachment_dt._selected_attachment_file_type == 'application/xml'
        assert attachment_dt._selected_attachment_file_name == 'file-three.xml'
        assert isinstance(app.screen, ViewAttachmentScreen)
        get_attachment_content_mock.assert_called_once_with('3')
        assert isinstance(app.screen.center_widget.children[0], TextArea)
        assert app.screen.center_widget.children[0].text == '<xml> content'
        assert app.screen.center_widget.children[0].language == 'xml'


@patch('jiratui.widgets.screens.APIController.get_attachment_content')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_show_attachment_with_unsupported_type(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_attachment_content_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_attachment_content_mock.return_value = APIControllerResponse(result='csv content'.encode())
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('down')
        await pilot.press('down')
        await pilot.press('down')
        await pilot.press('down')
        await pilot.press('v')
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert main_screen.issue_attachments_widget.issue_key == 'key-2'
        attachment_dt = main_screen.issue_attachments_widget.query_one(AttachmentsDataTable)
        assert attachment_dt.has_focus
        assert attachment_dt._selected_attachment_file_type == 'text/abc'
        assert attachment_dt._selected_attachment_file_name == 'file-five.abc'
        assert isinstance(app.screen, MainScreen)


@pytest.mark.parametrize(
    'file_type, content, expected_widget',
    [
        ('text/plain', b'hello world', TextArea),
        ('text/csv', b'hello world', TextArea),
        ('text/markdown', b'hello world', Markdown),
        ('application/json', b'{}', TextArea),
        ('application/xml', b'hello world', TextArea),
    ],
)
def test_build_file_attachment_widget(file_type: str, content: bytes, expected_widget: Type):
    widget = FileAttachmentWidget.build_widget(file_type, content)
    assert isinstance(widget, expected_widget)


def test_build_file_attachment_widget_for_unsupported_file_type():
    widget = FileAttachmentWidget.build_widget('image/svg', b'')
    assert widget is None
