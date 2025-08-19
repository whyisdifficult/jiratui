from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Link, Static

from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen
from jiratui.widgets.work_item_details.read_only_details import WorkItemReadOnlyDetailsScreen


class ChildWorkItemCollapsible(Collapsible):
    BINDINGS = [
        Binding(
            key='v',
            action='view_work_item',
            description='View Work Item',
            show=True,
            key_display='v',
        ),
    ]

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)
        super().__init__(*args, **kwargs)

    @property
    def work_item_key(self) -> str | None:
        return self._work_item_key

    async def action_view_work_item(self) -> None:
        await self.app.push_screen(WorkItemReadOnlyDetailsScreen(self.work_item_key))


class IssueChildWorkItemsWidget(VerticalScroll):
    HELP = """\
# Subtasks

This will display a list of work items that are a sub task of the selected work item. A work item `A` is a subtask of
another work item `B` if the parent of `A` is `B`.
    """

    issues: Reactive[list[JiraIssue] | None] = reactive(None, always_update=True)

    BINDINGS = [
        # override the binding to be able to inject the current work item as a prent of the subtask
        Binding(
            key='ctrl+n',
            action='create_work_item_subtask',
            description='New Work Item',
            show=True,
            key_display='^n',
        ),
    ]

    def __init__(self):
        super().__init__(id='issue_subtasks')
        self._issue_key: str | None = None

    @property
    def issue_key(self) -> str | None:
        return self._issue_key

    @issue_key.setter
    def issue_key(self, value: str | None) -> None:
        self._issue_key = value

    async def action_create_work_item_subtask(self) -> None:
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        await self.app.push_screen(
            AddWorkItemScreen(
                project_key=screen.project_selector.selection,
                reporter_account_id=CONFIGURATION.get().jira_account_id,
                parent_work_item_key=self.issue_key,
            ),
            callback=screen.create_work_item,
        )

    def watch_issues(self, items: list[JiraIssue]) -> None:
        self.remove_children()
        if not items:
            return
        rows: list[ChildWorkItemCollapsible] = []
        for issue in items:
            children: list[Widget] = [
                Static(Text(f'Status: {issue.status.name}')),
                Static(Text(f'Type: {issue.issue_type.name}')),
                Static(Text(f'Assignee: {issue.display_assignee()}')),
            ]
            if browsable_url := build_external_url_for_issue(issue.key):
                children.append(
                    Link(
                        browsable_url, url=browsable_url, tooltip='open link in the default browser'
                    )
                )
            rows.append(
                ChildWorkItemCollapsible(
                    *children,
                    title=Text(f'{issue.key} | {issue.cleaned_summary()}'),
                    work_item_key=issue.key,
                )
            )
        self.mount_all(rows)
