from unittest.mock import MagicMock, patch

import pytest

from jiratui.widgets.screens.work_item_quick_view import WorkItemReadOnlyDetailsScreen
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
        assert isinstance(app.screen, WorkItemReadOnlyDetailsScreen)
