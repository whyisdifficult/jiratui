from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.screen import MainScreen
from jiratui.widgets.screens.goto import GotToScreen
from jiratui.widgets.screens.work_item_quick_view import WorkItemQuickViewScreen
from jiratui.widgets.work_item_subtasks.subtasks import (
    ChildWorkItemCollapsible,
    IssueChildWorkItemsWidget,
    WorkItemSubtasks,
)


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


@pytest.mark.asyncio
async def test_sets_subtasks(mock_configuration, jira_issues, app):
    async with app.run_test():
        # GIVEN
        mock_configuration.jira_base_url = 'http://foo.bar'
        widget = IssueChildWorkItemsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.issues = WorkItemSubtasks(
            work_item_key='WI-1',
            project_key='P1',
            issues=jira_issues,
        )
        # THEN
        assert widget._work_item_key == 'WI-1'
        assert widget._work_item_project_key == 'P1'
        assert len(widget.children) == 2
        assert isinstance(widget.children[0], ChildWorkItemCollapsible)
        assert widget.children[0]._work_item_key == 'key-1'
        assert widget.children[1]._work_item_key == 'key-2'


@pytest.mark.asyncio
async def test_sets_subtasks_none(jira_issues, app):
    async with app.run_test():
        # GIVEN
        widget = IssueChildWorkItemsWidget()
        await app.screen.mount(widget)
        # WHEN
        widget.issues = None
        # THEN
        assert widget._work_item_key is None
        assert widget._work_item_project_key is None
        assert len(widget.children) == 0


@pytest.mark.asyncio
async def test_view_subtask(app):
    async with app.run_test() as pilot:
        # GIVEN
        widget = ChildWorkItemCollapsible(work_item_key='key-1')
        await app.screen.mount(widget)
        # WHEN
        await widget.action_view_work_item()
        await pilot.pause()
        # THEN
        assert isinstance(app.screen, WorkItemQuickViewScreen)


@pytest.mark.asyncio
async def test_related_issues_widget_opens_quick_view_screen(mock_configuration, jira_issues, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        widget = IssueChildWorkItemsWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issues = WorkItemSubtasks(
            work_item_key='WI-1',
            project_key='P1',
            issues=jira_issues,
        )
        await pilot.press('8')
        await pilot.press('tab')
        await pilot.press('v')
        # THEN
        assert isinstance(app.screen, WorkItemQuickViewScreen)
        assert app.screen._work_item_key == 'key-1'


@pytest.mark.asyncio
async def test_open_goto_screen_with_goto_enabled(
    mock_configuration, jira_issues: list[JiraIssue], app
):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    app.config.enable_goto = True
    async with app.run_test() as pilot:
        # WHEN
        widget = IssueChildWorkItemsWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issues = WorkItemSubtasks(
            work_item_key='WI-1',
            project_key='P1',
            issues=jira_issues,
        )
        await pilot.press('8')
        await pilot.press('tab')
        await pilot.press('f6')
        # THEN
        assert isinstance(app.screen, GotToScreen)


@pytest.mark.asyncio
async def test_open_goto_screen_with_goto_disabled(
    mock_configuration, jira_issues: list[JiraIssue], app
):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    app.config.enable_goto = False
    async with app.run_test() as pilot:
        # WHEN
        widget = IssueChildWorkItemsWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issues = WorkItemSubtasks(
            work_item_key='WI-1',
            project_key='P1',
            issues=jira_issues,
        )
        await pilot.press('8')
        await pilot.press('tab')
        await pilot.press('f6')
        # THEN
        assert isinstance(app.screen, MainScreen)


@patch.object(APIController, 'get_issue')
@patch.object(ChildWorkItemCollapsible, '_close_goto_screen')
@pytest.mark.asyncio
async def test_dismiss_goto_screen_with_key(
    close_goto_screen_mock: Mock,
    get_issue_mock: AsyncMock,
    mock_configuration,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    app.config.enable_goto = True
    async with app.run_test() as pilot:
        # WHEN
        widget = IssueChildWorkItemsWidget()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issues = WorkItemSubtasks(
            work_item_key=jira_issues[0].key,
            project_key='P1',
            issues=[jira_issues[1]],
        )
        await pilot.press('8')
        await pilot.press('tab')
        await pilot.press('f6')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, MainScreen)
        close_goto_screen_mock.assert_called_once_with('key-1')
