"""
Running tests for this module:

# to test the actions with the standard key bindings
`JIRA_TUI_KEYBIND_STYLE=standard pytest src/jiratui/actions/tests/test_actions.py`
# to test the actions with the legacy key bindings
`JIRA_TUI_KEYBIND_STYLE=legacy pytest src/jiratui/actions/tests/test_actions.py`
# or, run
`make test`
"""

from typing import cast
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest
from textual.widget import Widget
from textual.widgets import DataTable

from jiratui.actions.keys import get_application_key_bindings
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
from jiratui.utils.history import HistoryEntry, HistoryManager
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
from jiratui.widgets.commons.adf import ADFMarkdownTextAreaWidget
from jiratui.widgets.commons.users import JiraUserInput
from jiratui.widgets.commons.widgets import PlainTextTextAreaWidget
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen, TextAreaTabbedContent
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
from jiratui.widgets.screens.goto import GoToScreen
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


@pytest.fixture
def bindings() -> dict:
    return get_application_key_bindings()


@pytest.mark.parametrize(
    'key, widget',
    [
        (
            get_application_key_bindings().get('focus_project_filter', {}).get('keys', [])[0],
            ProjectSelectionInput,
        ),
        (
            get_application_key_bindings()
            .get('focus_search_work_item_type_filter', {})
            .get('keys', [])[0],
            IssueTypeSelectionInput,
        ),
        (
            get_application_key_bindings()
            .get('focus_search_work_item_status_filter', {})
            .get('keys', [])[0],
            IssueStatusSelectionInput,
        ),
        (
            get_application_key_bindings()
            .get('focus_search_assignee_filter', {})
            .get('keys', [])[0],
            JiraUserInput,
        ),
        (
            get_application_key_bindings()
            .get('focus_search_work_item_key_filter', {})
            .get('keys', [])[0],
            WorkItemInputWidget,
        ),
        (
            get_application_key_bindings()
            .get('focus_search_created_from_filter', {})
            .get('keys', [])[0],
            IssueSearchCreatedFromWidget,
        ),
        (
            get_application_key_bindings()
            .get('focus_search_created_until_filter', {})
            .get('keys', [])[0],
            IssueSearchCreatedUntilWidget,
        ),
        (
            get_application_key_bindings().get('focus_search_sort_filter', {}).get('keys', [])[0],
            OrderByWidget,
        ),
        (
            get_application_key_bindings().get('focus_search_sprint_filter', {}).get('keys', [])[0],
            ActiveSprintCheckbox,
        ),
        (
            get_application_key_bindings().get('focus_search_jql', {}).get('keys', [])[0],
            JQLSearchWidget,
        ),
        (
            get_application_key_bindings().get('focus_search_results', {}).get('keys', [])[0],
            IssuesSearchResultsTable,
        ),
        (
            get_application_key_bindings()
            .get('focus_work_item_information_tab', {})
            .get('keys', [])[0],
            WorkItemInfoContainer,
        ),
        (
            get_application_key_bindings()
            .get('focus_work_item_details_tab', {})
            .get('keys', [])[0],
            IssueDetailsWidget,
        ),
        (
            get_application_key_bindings()
            .get('focus_work_item_comments_tab', {})
            .get('keys', [])[0],
            IssueCommentsWidget,
        ),
        (
            get_application_key_bindings()
            .get('focus_work_item_related_tab', {})
            .get('keys', [])[0],
            RelatedIssuesWidget,
        ),
        (
            get_application_key_bindings()
            .get('focus_work_item_attachments_tab', {})
            .get('keys', [])[0],
            IssueAttachmentsWidget,
        ),
        (
            get_application_key_bindings().get('focus_work_item_links_tab', {}).get('keys', [])[0],
            IssueRemoteLinksWidget,
        ),
        (
            get_application_key_bindings()
            .get('focus_work_item_subtasks_tab', {})
            .get('keys', [])[0],
            IssueChildWorkItemsWidget,
        ),
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
        (get_application_key_bindings().get('help', {}).get('keys', [])[0], HelpScreen),
        (
            get_application_key_bindings().get('server_info', {}).get('keys', [])[0],
            ServerInfoScreen,
        ),
        (
            get_application_key_bindings().get('config_info', {}).get('keys', [])[0],
            ConfigFileScreen,
        ),
        (
            get_application_key_bindings().get('show_recent_history', {}).get('keys', [])[0],
            HistoryScreen,
        ),
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
    bindings: dict,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
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
    bindings: dict,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press(bindings.get('find_by_text', {}).get('keys', [])[0])
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
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('create_git_branch', {}).get('keys', [])[0])
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
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('open_go_to_screen', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, GoToScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_view_work_item_to_view_related_item(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('view_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, WorkItemQuickViewScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_acton_unlink_work_item_to_delete_related_item(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('unlink_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        search_work_items_mock.assert_awaited_once()
        assert isinstance(app.screen, ConfirmationScreen)


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_link_work_item_to_add_related_item(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('link_work_item', {}).get('keys', [])[0])
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
async def test_action_copy_issue_url_from_main_screen(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_copy_issue_url_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('copy_issue_url', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_copy_issue_url_mock.assert_called_once()


@patch.object(MainScreen, 'action_copy_issue_key')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_copy_issue_key_from_main_screen(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_copy_issue_key_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('copy_issue_key', {}).get('keys', [])[0])
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
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('delete_work_item', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_delete_work_item_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_open_in_browser')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_open_in_browser_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_open_in_browser_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('open_in_browser', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_open_in_browser_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_next_issues_page')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_next_issues_page_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_next_issues_page_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('next_issues_page', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_next_issues_page_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_previous_issues_page')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_previous_issues_page_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_previous_issues_page_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('previous_issues_page', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_previous_issues_page_mock.assert_called_once()


@patch.object(IssuesSearchResultsTable, 'action_filter')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_filter_results_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_filter_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('filter', {}).get('keys', [])[0])
        await pilot.press(bindings.get('filter', {}).get('keys', [])[-1])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_filter_mock.assert_called()


@patch.object(DataTable, 'action_select_cursor')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_select_cursor_to_select_item_from_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_select_cursor_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_select_cursor_mock.assert_called_once()


@pytest.mark.parametrize(
    'key',
    [
        get_application_key_bindings().get('cursor_up', {}).get('keys', [])[0],
        get_application_key_bindings().get('cursor_up', {}).get('keys', [])[-1],
    ],
)
@patch.object(DataTable, 'action_cursor_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_up_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_cursor_up_mock: Mock,
    jira_issues,
    key: str,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_cursor_up_mock.assert_called_once()


@pytest.mark.parametrize(
    'key',
    [
        get_application_key_bindings().get('cursor_down', {}).get('keys', [])[0],
        get_application_key_bindings().get('cursor_down', {}).get('keys', [])[-1],
    ],
)
@patch.object(DataTable, 'action_cursor_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_down_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_cursor_down_mock: Mock,
    jira_issues,
    key: str,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(key)
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_cursor_down_mock.assert_called_once()


@pytest.mark.parametrize(
    'key',
    [
        get_application_key_bindings().get('page_up', {}).get('keys', [])[0],
        get_application_key_bindings().get('page_up', {}).get('keys', [])[-1],
    ],
)
@patch.object(DataTable, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: Mock,
    jira_issues,
    key: str,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
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
async def test_action_page_down_in_search_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_page_down_mock.assert_called_once()


@patch.object(DataTable, 'action_scroll_top')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_top_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_scroll_top_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('scroll_top', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_scroll_top_mock.assert_called_once()


@patch.object(DataTable, 'action_scroll_bottom')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_bottom_in_search_results(
    search_projects_mock,
    fetch_issue_types_mock,
    fetch_statuses_mock,
    search_work_items_mock: AsyncMock,
    action_scroll_bottom_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('scroll_bottom', {}).get('keys', [])[0])
        # THEN
        search_work_items_mock.assert_awaited_once()
        action_scroll_bottom_mock.assert_called_once()


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
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
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
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
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
async def test_action_create_work_item_from_main_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    create_work_item_mock: AsyncMock,
    bindings: dict,
    app,
):
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('create_work_item', {}).get('keys', [])[0])
        # THEN
        create_work_item_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'action_save_content')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_save_content_from_add_work_item_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_save_content_mock: Mock,
    bindings: dict,
    app,
):
    # test action save_content from the screen that creates new work items
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        app.push_screen(AddWorkItemScreen())
        await pilot.press(bindings.get('save_content', {}).get('keys', [])[0])
        # THEN
        action_save_content_mock.assert_called_once()


@patch.object(TextAreaTabbedContent, 'action_open_text_editor')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_open_text_editor_from_add_work_item_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_open_text_editor_mock: Mock,
    bindings: dict,
    app,
):
    # test action save_content from the screen that creates new work items
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        app.push_screen(AddWorkItemScreen())
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('open_text_editor', {}).get('keys', [])[0])
        # THEN
        action_open_text_editor_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'adf_support_enabled', PropertyMock(return_value=True))
@patch.object(ADFMarkdownTextAreaWidget, 'action_open_text_editor')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_open_text_editor_with_adf_support_enabled_from_add_work_item_screen_focused_on_textarea(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_open_text_editor_mock: Mock,
    bindings: dict,
    app,
):
    # test action save_content from the screen that creates new work items
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        app.push_screen(AddWorkItemScreen())
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('open_text_editor', {}).get('keys', [])[0])
        # THEN
        action_open_text_editor_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'adf_support_enabled', PropertyMock(return_value=False))
@patch.object(PlainTextTextAreaWidget, 'action_open_text_editor')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_open_text_editor_without_adf_support_enabled_from_add_work_item_screen_focused_on_textarea(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_open_text_editor_mock: Mock,
    bindings: dict,
    app,
):
    # test action save_content from the screen that creates new work items
    # GIVEN
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        app.push_screen(AddWorkItemScreen())
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('open_text_editor', {}).get('keys', [])[0])
        # THEN
        action_open_text_editor_mock.assert_called_once()


@patch.object(IssueCommentsWidget, 'action_add_comment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_add_comment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_add_comment_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('add_comment', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_add_comment_mock.assert_called_once()


@patch.object(Widget, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_comments_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_page_up_mock.assert_called()


@patch.object(Widget, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_comments_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_page_down_mock.assert_called()


@patch.object(Widget, 'action_scroll_home')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_home_in_comments_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_home_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_home', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_home_mock.assert_called()


@patch.object(Widget, 'action_scroll_end')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_end_in_comments_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_end_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_end', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_end_mock.assert_called()


@patch.object(Widget, 'action_scroll_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_up_in_comments_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_up_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_up_mock.assert_called()


@patch.object(Widget, 'action_scroll_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_down_in_comments_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_down_mock.assert_called()


@patch.object(CommentCollapsible, 'action_delete_comment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_delete_comment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_delete_comment_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_comments_widget.comments = WorkItemComments(
            work_item_key=jira_issues[1].key, comments=jira_issues[1].comments
        )
        await pilot.press(bindings.get('focus_work_item_comments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('delete_comment', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_delete_comment_mock.assert_awaited_once()


@patch.object(IssueAttachmentsWidget, 'action_add_attachment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_add_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_add_attachment_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('add_attachment', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_add_attachment_mock.assert_called_once()


@patch.object(AttachmentsDataTable, 'action_delete_attachment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_delete_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_delete_attachment_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('delete_attachment', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_delete_attachment_mock.assert_awaited_once()


@patch.object(AttachmentsDataTable, 'action_open_attachment')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_open_attachment(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_open_attachment_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('open_attachment', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_open_attachment_mock.assert_awaited_once()


@patch.object(AttachmentsDataTable, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_attachments_table(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: Mock,
    jira_issues,
    bindings: dict,
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
        Attachment(
            id='2',
            filename='file2.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
        Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_page_up_mock.assert_called_once()


@patch.object(AttachmentsDataTable, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_attachments_table(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        Attachment(
            id='2',
            filename='file2.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
        Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_page_down_mock.assert_called_once()


@patch.object(AttachmentsDataTable, 'action_cursor_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_up_in_attachments_table(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_cursor_up_mock: Mock,
    jira_issues,
    bindings: dict,
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
        Attachment(
            id='2',
            filename='file2.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
        Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_up', {}).get('keys', [])[0])
        await pilot.press(bindings.get('cursor_up', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_cursor_up_mock.assert_called()


@patch.object(AttachmentsDataTable, 'action_cursor_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_down_in_attachments_table(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_cursor_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        Attachment(
            id='2',
            filename='file2.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
        Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_down', {}).get('keys', [])[0])
        await pilot.press(bindings.get('cursor_down', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_cursor_down_mock.assert_called()


@patch.object(AttachmentsDataTable, 'action_scroll_top')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_top_in_attachments_table(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_top_mock: Mock,
    jira_issues,
    bindings: dict,
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
        Attachment(
            id='2',
            filename='file2.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
        Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_top', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_top_mock.assert_called_once()


@patch.object(AttachmentsDataTable, 'action_scroll_bottom')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_bottom_in_attachments_table(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_bottom_mock: Mock,
    jira_issues,
    bindings: dict,
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
        Attachment(
            id='2',
            filename='file2.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
        Attachment(
            id='3',
            filename='file3.txt',
            size=10,
            mime_type='text/plain',
            author=JiraUser(account_id='1', active=True, display_name='Bart'),
        ),
    ]
    app.config.pre_defined_jql_expressions = None
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_attachments_widget.attachments = WorkItemAttachments(
            work_item_key=jira_issues[1].key, attachments=jira_issues[1].attachments
        )
        await pilot.press(bindings.get('focus_work_item_attachments_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_bottom', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_bottom_mock.assert_called_once()


@patch.object(RelatedIssuesWidget, 'action_link_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_link_work_item_from_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_link_work_item_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('link_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_link_work_item_mock.assert_awaited_once()


@patch.object(RelatedIssueCollapsible, 'action_view_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_view_work_item_from_related_issues_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_work_item_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('view_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_view_work_item_mock.assert_awaited_once()


@patch.object(RelatedIssueCollapsible, 'action_unlink_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_unlink_work_item_from_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_unlink_work_item_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('unlink_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_unlink_work_item_mock.assert_awaited_once()


@patch.object(Widget, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_page_up_mock.assert_called_once()


@patch.object(Widget, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_page_down_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_home')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_home_in_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_home_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_home', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_home_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_end')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_end_in_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_end_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_end', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_end_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_up_in_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_up_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_up_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_down_in_related_issues_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_down_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.related_issues_widget.issues = WorkItemRelatedItems(
            work_item_key=jira_issues[1].key, related_items=jira_issues[1].related_issues
        )
        await pilot.press(bindings.get('focus_work_item_related_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_down_mock.assert_called_once()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(IssueRemoteLinksWidget, 'action_add_remote_link')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_add_remote_link_from_links_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_add_remote_link_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('add_remote_link', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_add_remote_link_mock.assert_awaited_once()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(Widget, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_from_remote_links_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_page_up_mock.assert_called()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(Widget, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_from_remote_links_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_page_down_mock.assert_called()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(Widget, 'action_scroll_home')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_home_from_remote_links_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_home_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_home', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_home_mock.assert_called()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(Widget, 'action_scroll_end')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_end_from_remote_links_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_end_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_end', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_end_mock.assert_called()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(Widget, 'action_scroll_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_up_from_remote_links_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_up_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_up_mock.assert_called()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(Widget, 'action_scroll_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_down_from_remote_links_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_down_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[-1])
        await app.workers.wait_for_complete()
        # THEN
        action_scroll_down_mock.assert_called()


@patch.object(APIController, 'get_issue_remote_links')
@patch.object(IssueRemoteLinkCollapsible, 'action_delete_remote_link')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_delete_remote_link_from_links_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_delete_remote_link_mock: AsyncMock,
    get_issue_remote_links_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_remote_links_widget.issue_key = jira_issues[1].key
        await pilot.press(bindings.get('focus_work_item_links_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('delete_remote_link', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_delete_remote_link_mock.assert_awaited_once()


@patch.object(IssueDetailsWidget, 'action_view_worklog')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_view_worklog_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_worklog_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('view_worklog', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_view_worklog_mock.assert_called_once()


@patch.object(WorkItemWorkLogScreen, 'action_log_work')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_log_work_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_log_work_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('view_worklog', {}).get('keys', [])[0])
        await pilot.press(bindings.get('log_work', {}).get('keys', [])[0])
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
async def test_action_delete_worklog_entry(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    action_delete_worklog_mock: AsyncMock,
    jira_issues,
    jira_worklogs,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('view_worklog', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press(bindings.get('delete_worklog', {}).get('keys', [])[0])
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
async def test_action_open_in_browser_worklog_entry(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    action_open_in_browser_mock: AsyncMock,
    jira_issues,
    jira_worklogs,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('view_worklog', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press(bindings.get('open_in_browser', {}).get('keys', [])[0])
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
async def test_action_edit_worklog_entry(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    action_edit_worklog_entry_mock: AsyncMock,
    jira_issues,
    jira_worklogs,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('view_worklog', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press(bindings.get('edit_worklog_entry', {}).get('keys', [])[0])
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        action_edit_worklog_entry_mock.assert_awaited_once()


@patch.object(IssueDetailsWidget, 'action_flag_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_flag_work_item_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_flag_work_item_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('flag_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_flag_work_item_mock.assert_called_once()


@patch.object(IssueDetailsWidget, 'action_save_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_save_work_item_from_details_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_save_content_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_details_widget.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_details_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('save_content', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_save_content_mock.assert_called_once()


@patch.object(InfoTabbedContent, 'action_view_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_view_content_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_content_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_information_tab', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('view_content', {}).get('keys', [])[0])
        # THEN
        action_view_content_mock.assert_called_once()


@patch.object(InfoTabbedContent, 'action_edit_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_edit_content_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_edit_content_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_information_tab', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('edit_content', {}).get('keys', [])[0])
        # THEN
        action_edit_content_mock.assert_called_once()


@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_edit_content_open_edit_screen_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_information_tab', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('edit_content', {}).get('keys', [])[0])
        # THEN
        assert isinstance(app.screen, EditTextContentScreen)


@patch.object(EditTextContentScreen, 'action_save_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_save_content_in_edit_screen_from_info_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_save_content_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_information_tab', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('edit_content', {}).get('keys', [])[0])
        await pilot.press(bindings.get('save_content', {}).get('keys', [])[0])
        # THEN
        action_save_content_mock.assert_called_once()


@patch.object(InfoTabbedContent, 'action_copy_content')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_copy_content_from_info_tab(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_copy_content_mock: AsyncMock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_info_container.issue = jira_issues[1]
        await pilot.press(bindings.get('focus_work_item_information_tab', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press(bindings.get('copy_content', {}).get('keys', [])[0])
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
    bindings: dict,
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    async with app.run_test() as pilot:
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        # THEN
        action_search_mock.assert_awaited_once()


@patch.object(HistoryScreen, 'action_empty_recent_history')
@pytest.mark.asyncio
async def test_action_empty_recent_history(empty_recent_history_mock: Mock, bindings: dict, app):
    # testing action empty_recent_history
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press(bindings.get('empty_recent_history', {}).get('keys', [])[0])
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
    bindings: dict,
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
async def test_action_create_work_item_subtask_from_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_create_work_item_subtask_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('create_work_item_subtask', {}).get('keys', [])[0])
        # THEN
        action_create_work_item_subtask_mock.assert_called_once()


@patch.object(ChildWorkItemCollapsible, 'action_view_work_item')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_view_work_item_from_selected_subtasks_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_view_work_item_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_child_work_items_widget.issues = WorkItemSubtasks(
            work_item_key=jira_issues[1].key,
            project_key=jira_issues[1].project.key,
            issues=[jira_issues[0]],
        )
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('view_work_item', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_view_work_item_mock.assert_called_once()


@patch.object(ChildWorkItemCollapsible, 'action_open_go_to_screen')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_open_go_to_screen_with_selected_subtask_from_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_open_go_to_screen_mock: Mock,
    jira_issues,
    bindings: dict,
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        app.screen.issue_child_work_items_widget.issues = WorkItemSubtasks(
            work_item_key=jira_issues[1].key,
            project_key=jira_issues[1].project.key,
            issues=[jira_issues[0]],
        )
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press('tab')
        await pilot.press(bindings.get('open_go_to_screen', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        # THEN
        action_open_go_to_screen_mock.assert_called_once()


@patch.object(Widget, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_up_mock: Mock,
    jira_issues,
    bindings: dict,
    app,
):
    # tests the action page_up to open the screen to add a new work item from the Subtasks tab; a
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        # THEN
        action_page_up_mock.assert_called_once()


@patch.object(Widget, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_page_down_mock: Mock,
    jira_issues,
    bindings: dict,
    app,
):
    # tests the action page_up to open the screen to add a new work item from the Subtasks tab; a
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        # THEN
        action_page_down_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_home')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_home_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_home_mock: Mock,
    jira_issues,
    bindings: dict,
    app,
):
    # tests the action page_up to open the screen to add a new work item from the Subtasks tab; a
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_home', {}).get('keys', [])[0])
        # THEN
        action_scroll_home_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_end')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_end_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_end_mock: Mock,
    jira_issues,
    bindings: dict,
    app,
):
    # tests the action page_up to open the screen to add a new work item from the Subtasks tab; a
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_end', {}).get('keys', [])[0])
        # THEN
        action_scroll_end_mock.assert_called_once()


@patch.object(Widget, 'action_scroll_up')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_up_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_up_mock: Mock,
    jira_issues,
    bindings: dict,
    app,
):
    # tests the action page_up to open the screen to add a new work item from the Subtasks tab; a
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_up', {}).get('keys', [])[-1])
        # THEN
        action_scroll_up_mock.assert_called()


@patch.object(Widget, 'action_scroll_down')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_down_in_subtasks_tab(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    action_scroll_down_mock: Mock,
    jira_issues,
    bindings: dict,
    app,
):
    # tests the action page_up to open the screen to add a new work item from the Subtasks tab; a
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
        await pilot.press(bindings.get('search', {}).get('keys', [])[0])
        await app.workers.wait_for_complete()
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        await pilot.press(bindings.get('focus_work_item_subtasks_tab', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[0])
        await pilot.press(bindings.get('scroll_down', {}).get('keys', [])[-1])
        # THEN
        action_scroll_down_mock.assert_called()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_cursor_up')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_up_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_cursor_up_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_up', {}).get('keys', [])[0])
        # THEN
        action_cursor_up_mock.assert_called_once()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_cursor_down')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_down_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_cursor_down_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_down', {}).get('keys', [])[0])
        # THEN
        action_cursor_down_mock.assert_called_once()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_page_up_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        # THEN
        action_page_up_mock.assert_called_once()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_page_down_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        # THEN
        action_page_down_mock.assert_called_once()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_scroll_top')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_top_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_scroll_top_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_top', {}).get('keys', [])[0])
        # THEN
        action_scroll_top_mock.assert_called_once()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_scroll_bottom')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_bottom_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_scroll_bottom_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_bottom', {}).get('keys', [])[0])
        # THEN
        action_scroll_bottom_mock.assert_called_once()


@patch.object(ConfigFileScreen, '_get_data')
@patch.object(DataTable, 'action_select_cursor')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_select_cursor_in_config_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_select_cursor_mock: Mock,
    get_data_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_data_mock.return_value = {
        'field_1': '21',
        'field_2': '2',
        'field_3': '3',
    }
    app.config.pre_defined_jql_expressions = None
    app.config.ssl = None
    async with app.run_test() as pilot:
        app.push_screen(ConfigFileScreen())
        await pilot.press('tab')
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        # THEN
        action_select_cursor_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_cursor_up')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_up_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_cursor_up_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_up', {}).get('keys', [])[0])
        # THEN
        action_cursor_up_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_cursor_down')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_down_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_cursor_down_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_down', {}).get('keys', [])[0])
        # THEN
        action_cursor_down_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_page_up_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        # THEN
        action_page_up_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_page_down_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        # THEN
        action_page_down_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_scroll_top')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_top_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_scroll_top_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_top', {}).get('keys', [])[0])
        # THEN
        action_scroll_top_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_scroll_bottom')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_bottom_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_scroll_bottom_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_bottom', {}).get('keys', [])[0])
        # THEN
        action_scroll_bottom_mock.assert_called_once()


@patch.object(APIController, 'get_issue')
@patch.object(DataTable, 'action_select_cursor')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_select_cursor_in_goto_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_select_cursor_mock: Mock,
    get_issue_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    async with app.run_test() as pilot:
        app.push_screen(GoToScreen(jira_issues[0].key, APIController()))
        await pilot.press('tab')
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        # THEN
        action_select_cursor_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_cursor_up')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_up_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_cursor_up_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_up', {}).get('keys', [])[0])
        # THEN
        action_cursor_up_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_cursor_down')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_cursor_down_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_cursor_down_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('cursor_down', {}).get('keys', [])[0])
        # THEN
        action_cursor_down_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_page_up')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_up_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_page_up_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('page_up', {}).get('keys', [])[0])
        # THEN
        action_page_up_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_page_down')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_page_down_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_page_down_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('page_down', {}).get('keys', [])[0])
        # THEN
        action_page_down_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_scroll_top')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_top_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_scroll_top_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_top', {}).get('keys', [])[0])
        # THEN
        action_scroll_top_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_scroll_bottom')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_scroll_bottom_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_scroll_bottom_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('scroll_bottom', {}).get('keys', [])[0])
        # THEN
        action_scroll_bottom_mock.assert_called_once()


@patch.object(HistoryManager, 'get_history')
@patch.object(DataTable, 'action_select_cursor')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_action_select_cursor_in_history_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    action_select_cursor_mock: Mock,
    get_history_mock: Mock,
    bindings: dict,
    jira_issues,
    app,
):
    # GIVEN
    get_history_mock.return_value = [
        HistoryEntry(key='WI-1', item_type='Task', status='Done', summary='Work to do 1'),
        HistoryEntry(key='WI-2', item_type='Task', status='Done', summary='Work to do 2'),
        HistoryEntry(key='WI-3', item_type='Task', status='Done', summary='Work to do 3'),
    ]
    async with app.run_test() as pilot:
        app.push_screen(HistoryScreen(HistoryManager()))
        await pilot.press('tab')
        await pilot.press(bindings.get('select_cursor', {}).get('keys', [])[0])
        # THEN
        action_select_cursor_mock.assert_called_once()
