import os
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

import pytest
from textual.widgets import DataTable

# IMPORTANT!
# set BEFORE any other imports that might depend on this. This allows us to test different key binding styles
os.environ['JIRA_TUI_KEYBIND_STYLE'] = 'standard'

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import (
    Attachment,
    IssueComment,
    IssueRemoteLink,
    IssueStatus,
    IssueType,
    JiraIssueSearchResponse,
    JiraUser,
    PaginatedJiraWorklog,
    RelatedJiraIssue,
)
from jiratui.utils.history import HistoryManager
from jiratui.widgets.attachments.attachments import (
    AttachmentsDataTable,
    IssueAttachmentsWidget,
    WorkItemAttachments,
)
from jiratui.widgets.comments.comments import (
    CommentCollapsible,
    IssueCommentsWidget,
    WorkItemComments,
)
from jiratui.widgets.commons.users import JiraUserInput
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen
from jiratui.widgets.filters import (
    ActiveSprintCheckbox,
    IssueSearchCreatedFromWidget,
    IssueSearchCreatedUntilWidget,
    IssueStatusSelectionInput,
    IssueTypeSelectionInput,
    JQLSearchWidget,
    OrderByWidget,
    ProjectSelectionInput,
    WorkItemInputWidget,
)
from jiratui.widgets.related_work_items.add import AddWorkItemRelationshipScreen
from jiratui.widgets.related_work_items.related_issues import (
    RelatedIssueCollapsible,
    RelatedIssuesWidget,
    WorkItemRelatedItems,
)
from jiratui.widgets.remote_links.links import IssueRemoteLinkCollapsible, IssueRemoteLinksWidget
from jiratui.widgets.screen import MainScreen, WorkItemSearchResult
from jiratui.widgets.screens.config import ConfigFileScreen
from jiratui.widgets.screens.confirmation import ConfirmationScreen
from jiratui.widgets.screens.git import GitScreen
from jiratui.widgets.screens.goto import GotToScreen
from jiratui.widgets.screens.help import HelpScreen
from jiratui.widgets.screens.history import HistoryScreen
from jiratui.widgets.screens.jql import JQLEditorScreen
from jiratui.widgets.screens.server import ServerInfoScreen
from jiratui.widgets.screens.work_item_quick_view import WorkItemQuickViewScreen
from jiratui.widgets.search import IssuesSearchResultsTable
from jiratui.widgets.work_item_details.details import IssueDetailsWidget
from jiratui.widgets.work_item_info.info import WorkItemInfoContainer
from jiratui.widgets.work_item_info.screens import EditTextContentScreen
from jiratui.widgets.work_item_info.tabs import InfoTabbedContent
from jiratui.widgets.work_item_subtasks.subtasks import (
    ChildWorkItemCollapsible,
    IssueChildWorkItemsWidget,
    WorkItemSubtasks,
)
from jiratui.widgets.work_item_worklog.screens import WorkItemWorkLogScreen, WorkLogCollapsible


@pytest.mark.parametrize(
    'key, widget',
    [
        ('alt+p', ProjectSelectionInput),
        ('alt+t', IssueTypeSelectionInput),
        ('alt+s', IssueStatusSelectionInput),
        ('alt+a', JiraUserInput),
        ('alt+k', WorkItemInputWidget),
        ('alt+f', IssueSearchCreatedFromWidget),
        ('alt+u', IssueSearchCreatedUntilWidget),
        ('alt+o', OrderByWidget),
        ('alt+v', ActiveSprintCheckbox),
        ('alt+j', JQLSearchWidget),
        ('1', IssuesSearchResultsTable),
        ('2', WorkItemInfoContainer),
        ('3', IssueDetailsWidget),
        ('4', IssueCommentsWidget),
        ('5', RelatedIssuesWidget),
        ('6', IssueAttachmentsWidget),
        ('7', IssueRemoteLinksWidget),
        ('8', IssueChildWorkItemsWidget),
    ],
)
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_quick_access_keys_with_standard_keybindings_style(
    search_projects_mock, fetch_issue_types_mock, fetch_statuses_mock, key: str, widget, app
):
    async with app.run_test() as pilot:
        await pilot.press(key)
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert isinstance(main_screen.focused, widget)


@pytest.mark.parametrize(
    'key, expected_screen',
    [
        ('f1', HelpScreen),
        ('f2', ServerInfoScreen),
        ('f3', ConfigFileScreen),
        ('f4', HistoryScreen),
    ],
)
@patch.object(ConfigFileScreen, '_get_data')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_f_keys(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    get_config_data_mock: Mock,
    key: str,
    expected_screen,
    app,
):
    # GIVEN
    get_config_data_mock.return_value = {}
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(key)
        assert isinstance(app.screen, expected_screen)


@patch.object(MainScreen, 'action_search')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_perform_search_from_main_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_search_mock: AsyncMock,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('/')
        # THEN
        action_search_mock.assert_awaited_once()


@patch.object(MainScreen, 'action_find_by_text')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_perform_full_text_search_from_main_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_find_by_text_mock: AsyncMock,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+f')
        # THEN
        action_find_by_text_mock.assert_awaited_once()


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_open_git_screen(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('f6')
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, GitScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_open_goto_screen(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('f5')
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, GotToScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_goto_screen_key_to_view_related_item(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('v')
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, WorkItemQuickViewScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_goto_screen_key_to_delete_related_item(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('x')
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, ConfirmationScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_goto_screen_key_to_add_related_item(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('a')
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, AddWorkItemRelationshipScreen)


@patch.object(MainScreen, 'action_copy_issue_url')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_copy_item_url_from_main_screen(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_copy_issue_url_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('ctrl+c')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_copy_issue_url_mock.assert_called_once()


@patch.object(MainScreen, 'action_copy_issue_key')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_copy_item_key_from_main_screen(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_copy_issue_key_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('y')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_copy_issue_key_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_delete_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_delete_item_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_delete_work_item_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('x')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_delete_work_item_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_open_in_browser')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_open_item_in_browser_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_open_in_browser_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('o')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_open_in_browser_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_next_issues_page')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_go_to_next_page_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_next_issues_page_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press(']')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_next_issues_page_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_previous_issues_page')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_go_to_previous_page_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_previous_issues_page_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('[')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_previous_issues_page_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_filter')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_filter_results_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_filter_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('f')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_filter_mock.assert_called_once()


@patch.object(DataTable, 'action_select_cursor')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_select_item_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_select_cursor_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('enter')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_select_cursor_mock.assert_called_once()


@pytest.mark.parametrize('key', ['k', 'up'])
@patch.object(DataTable, 'action_cursor_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_move_row_up_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_cursor_up_mock: Mock,
    jira_issues,
    key: str,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_cursor_up_mock.assert_called_once()


@pytest.mark.parametrize('key', ['j', 'down'])
@patch.object(DataTable, 'action_cursor_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_move_row_down_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_cursor_down_mock: Mock,
    jira_issues,
    key: str,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_cursor_down_mock.assert_called_once()


@pytest.mark.parametrize('key', ['pageup', 'ctrl+b'])
@patch.object(DataTable, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_move_page_up_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: Mock,
    jira_issues,
    key: str,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_page_up_mock.assert_called_once()


@patch.object(DataTable, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_move_page_down_in_search_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('pagedown')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_page_down_mock.assert_called_once()


@patch.object(DataTable, 'action_scroll_top')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_scroll_top_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_scroll_top_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('ctrl+home')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_scroll_top_mock.assert_called_once()


@patch.object(DataTable, 'action_scroll_bottom')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_scroll_bottom_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_scroll_bottom_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('ctrl+end')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_scroll_bottom_mock.assert_called_once()


@patch.object(DataTable, 'action_scroll_home')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_scroll_home_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_scroll_home_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('home')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_scroll_home_mock.assert_called_once()


@patch.object(DataTable, 'action_scroll_end')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_scroll_end_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_scroll_end_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('end')
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_scroll_end_mock.assert_called_once()


@pytest.mark.xfail(reason='We need to implement this logic')
@pytest.mark.parametrize('key', ['l', 'right'])
@patch.object(DataTable, 'action_cursor_right')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_move_cursor_right_in_search_results(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_cursor_right_mock: Mock,
    jira_issues,
    key: str,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_cursor_right_mock.assert_called_once()


@pytest.mark.xfail(reason='We need to implement this logic')
@pytest.mark.parametrize('key', ['h', 'left'])
@patch.object(DataTable, 'action_cursor_left')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_move_cursor_left_in_search_results(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_cursor_left_mock: Mock,
    jira_issues,
    key: str,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    app.open_url = Mock()
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_cursor_left_mock.assert_called_once()


@patch.object(MainScreen, 'action_create_work_item')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_open_create_item_screen_from_main_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    create_work_item_mock: AsyncMock,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('ctrl+n')
        # THEN
        create_work_item_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'action_save_content')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_save_content_from_add_work_item_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_save_content_mock: Mock,
    app,
):
    # test action save_content from the screen that creates new work items
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        app.push_screen(AddWorkItemScreen())
        await pilot.press('ctrl+s')
        # THEN
        action_save_content_mock.assert_called_once()


@patch.object(IssueCommentsWidget, 'action_add_comment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_add_comment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_add_comment_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].comments = [
        IssueComment(
            id='1',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
            body='I will study',
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press('4')
        await pilot.press('tab')
        await pilot.press('a')
        await app.workers.wait_for_complete()
        # THEN
        action_add_comment_mock.assert_called_once()


@patch.object(CommentCollapsible, 'action_delete_comment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_delete_comment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_delete_comment_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].comments = [
        IssueComment(
            id='1',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
            body='I will study',
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press('4')
        await pilot.press('tab')
        await pilot.press('x')
        await app.workers.wait_for_complete()
        # THEN
        action_delete_comment_mock.assert_awaited_once()


@patch.object(IssueAttachmentsWidget, 'action_add_attachment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_add_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_add_attachment_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].attachments = [
        Attachment(
            id='1',
            filename='file1.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('a')
        await app.workers.wait_for_complete()
        # THEN
        action_add_attachment_mock.assert_called_once()


@patch.object(AttachmentsDataTable, 'action_delete_attachment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_delete_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_delete_attachment_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].attachments = [
        Attachment(
            id='1',
            filename='file1.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('x')
        await app.workers.wait_for_complete()
        # THEN
        action_delete_attachment_mock.assert_awaited_once()


@patch.object(AttachmentsDataTable, 'action_open_attachment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_open_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_open_attachment_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].attachments = [
        Attachment(
            id='1',
            filename='file1.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press('6')
        await pilot.press('tab')
        await pilot.press('o')
        await app.workers.wait_for_complete()
        # THEN
        action_open_attachment_mock.assert_awaited_once()


@patch.object(RelatedIssuesWidget, 'action_link_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_link_work_items_from_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_link_work_item_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('a')
        await app.workers.wait_for_complete()
        # THEN
        action_link_work_item_mock.assert_awaited_once()


@patch.object(RelatedIssueCollapsible, 'action_view_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_view_work_item_from_related_issues_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_work_item_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('v')
        await app.workers.wait_for_complete()
        # THEN
        action_view_work_item_mock.assert_awaited_once()


@patch.object(RelatedIssueCollapsible, 'action_unlink_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_unlink_work_item_from_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_unlink_work_item_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    jira_issues[1].related_issues = [
        RelatedJiraIssue(
            id='3',
            key='WI-3',
            summary='Issue 3',
            status=IssueStatus(id='1', name='Open'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press('5')
        await pilot.press('tab')
        await pilot.press('x')
        await app.workers.wait_for_complete()
        # THEN
        action_unlink_work_item_mock.assert_awaited_once()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(IssueRemoteLinksWidget, 'action_add_remote_link')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_add_web_link_from_links_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_add_remote_link_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
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
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press('7')
        await pilot.press('tab')
        await pilot.press('a')
        await app.workers.wait_for_complete()
        # THEN
        action_add_remote_link_mock.assert_awaited_once()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(IssueRemoteLinkCollapsible, 'action_delete_remote_link')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_delete_web_link_from_links_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_delete_remote_link_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
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
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press('7')
        await pilot.press('tab')
        await pilot.press('x')
        await app.workers.wait_for_complete()
        # THEN
        action_delete_remote_link_mock.assert_awaited_once()


@patch.object(IssueDetailsWidget, 'action_view_worklog')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_open_worklog_screen_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_worklog_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('w')
        await app.workers.wait_for_complete()
        # THEN
        action_view_worklog_mock.assert_called_once()


@patch.object(WorkItemWorkLogScreen, 'action_log_work')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_log_work_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_log_work_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('w')
        await pilot.press('l')
        await app.workers.wait_for_complete()
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        action_log_work_mock.assert_called_once()


@patch.object(WorkLogCollapsible, 'action_delete_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_delete_worklog_entry(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    action_delete_worklog_mock: AsyncMock,
    jira_issues,
    jira_worklogs,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('w')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('x')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        action_delete_worklog_mock.assert_awaited_once()


@patch.object(WorkLogCollapsible, 'action_open_in_browser')
@patch.object(APIController, 'get_work_item_worklog')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_open_in_browser_worklog_entry(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    action_open_in_browser_mock: AsyncMock,
    jira_issues,
    jira_worklogs,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('w')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('o')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        action_open_in_browser_mock.assert_awaited_once()


@patch.object(WorkLogCollapsible, 'action_edit_worklog_entry')
@patch.object(APIController, 'get_work_item_worklog')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_edit_worklog_entry(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    action_edit_worklog_entry_mock: AsyncMock,
    jira_issues,
    jira_worklogs,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('w')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('e')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        action_edit_worklog_entry_mock.assert_awaited_once()


@patch.object(IssueDetailsWidget, 'action_flag_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_flag_work_item_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_flag_work_item_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('*')
        await app.workers.wait_for_complete()
        # THEN
        action_flag_work_item_mock.assert_called_once()


@patch.object(IssueDetailsWidget, 'action_save_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_save_work_item_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_save_content_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press('3')
        await pilot.press('ctrl+s')
        await app.workers.wait_for_complete()
        # THEN
        action_save_content_mock.assert_called_once()


@patch.object(InfoTabbedContent, 'action_view_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_view_text_content_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_content_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    jira_issues[1].description = 'hello'
    jira_issues[1].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
            }
        }
    }
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press('2')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('v')
        # THEN
        action_view_content_mock.assert_called_once()


@patch.object(InfoTabbedContent, 'action_edit_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_edit_text_content_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_edit_content_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    jira_issues[1].description = 'hello'
    jira_issues[1].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
            }
        }
    }
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press('2')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('e')
        # THEN
        action_edit_content_mock.assert_called_once()


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_edit_text_content_open_edit_screen_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    app.config.enable_updating_rich_text = True
    app.config.text_editor = None
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    jira_issues[1].description = 'hello'
    jira_issues[1].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
            }
        }
    }
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press('2')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('e')
        # THEN
        assert isinstance(app.screen, EditTextContentScreen)


@patch.object(EditTextContentScreen, 'action_save_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_save_text_content_in_edit_screen_from_info_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_save_content_mock: Mock,
    jira_issues,
    app,
):
    # test the action save_content on the screen that edits text content
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    app.config.enable_updating_rich_text = True
    app.config.text_editor = None
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    jira_issues[1].description = 'hello'
    jira_issues[1].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
            }
        }
    }
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press('2')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('e')
        await pilot.press('ctrl+s')
        # THEN
        action_save_content_mock.assert_called_once()


@patch.object(InfoTabbedContent, 'action_copy_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_copy_text_content_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_copy_content_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    jira_issues[1].description = 'hello'
    jira_issues[1].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
            }
        }
    }
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press('2')
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('c')
        # THEN
        action_copy_content_mock.assert_called_once()


@patch.object(MainScreen, 'action_search')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_search_work_items_fro_main_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_search_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    async with app.run_test() as pilot:
        await pilot.press('/')
        # THEN
        action_search_mock.assert_awaited_once()


@patch.object(HistoryScreen, 'action_empty_recent_history')
@pytest.mark.asyncio
async def test_key_to_empty_recent_history(empty_recent_history_mock: Mock, app):
    # testing action empty_recent_history
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('x')
        # THEN
        empty_recent_history_mock.assert_called_once()


@pytest.mark.xfail(reason='Debug why does not work')
@patch.object(JQLSearchWidget, 'action_edit_jql')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_to_edit_jql_opening_modal_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_edit_jql_mock: AsyncMock,
    app,
):
    # test the action action_edit_jql
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('alt+j')
        assert isinstance(app.focused, JQLSearchWidget)
        await pilot.press('ctrl+e')
        await app.workers.wait_for_complete()
        # THEN
        action_edit_jql_mock.assert_awaited_once()
        assert isinstance(app.screen, JQLEditorScreen)


@patch.object(IssueChildWorkItemsWidget, 'action_create_work_item_subtask')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_for_action_create_work_item_subtask_from_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_create_work_item_subtask_mock: Mock,
    jira_issues,
    app,
):
    # tests the action create_work_item_subtask to open the screen to add a new work item from the Subtasks tab; a
    # work item must be selected in the results tab
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        await pilot.press('enter')
        await pilot.press('8')
        await pilot.press('a')
        # THEN
        action_create_work_item_subtask_mock.assert_called_once()


@patch.object(ChildWorkItemCollapsible, 'action_view_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_open_quick_view_screen_from_selected_subtasks_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_work_item_mock: Mock,
    jira_issues,
    app,
):
    # test the action that opens the quick view screen when the user selects a subtasks in the subtasks tab
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_child_work_items_widget.issues = WorkItemSubtasks(
            work_item_key=jira_issues[1].key,
            project_key=jira_issues[1].project.key,
            issues=[jira_issues[0]],
        )
        await pilot.press('8')
        await pilot.press('tab')
        await pilot.press('v')
        await app.workers.wait_for_complete()
        # THEN
        action_view_work_item_mock.assert_called_once()


@patch.object(ChildWorkItemCollapsible, 'action_open_go_to_screen')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_key_open_related_screen_for_selected_subtask_from_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_open_go_to_screen_mock: Mock,
    jira_issues,
    app,
):
    # test the action that opens the screen to view related tasks for a selected subtask
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.git_repositories = None
    app.config.jira_base_url = 'foo.bar'
    app.config.enable_goto = True
    search_work_items_mock.return_value = WorkItemSearchResult(
        response=JiraIssueSearchResponse(issues=jira_issues),
        total=1,
        start=1,
        end=1,
    )
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press('/')
        await app.workers.wait_for_complete()
        app.screen.issue_child_work_items_widget.issues = WorkItemSubtasks(
            work_item_key=jira_issues[1].key,
            project_key=jira_issues[1].project.key,
            issues=[jira_issues[0]],
        )
        await pilot.press('8')
        await pilot.press('tab')
        await pilot.press('f5')
        await app.workers.wait_for_complete()
        # THEN
        action_open_go_to_screen_mock.assert_called_once()
