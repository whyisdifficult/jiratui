from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Link, Rule, Static

from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue
from jiratui.utils.styling import get_style_for_work_item_status
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen
from jiratui.widgets.work_item_details.read_only_details import WorkItemReadOnlyDetailsScreen


class ChildWorkItemCollapsible(Collapsible):
    """A collapsible to show the work items that are children of another work item."""

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
        self.border_title = self._work_item_key

    @property
    def work_item_key(self) -> str | None:
        return self._work_item_key

    async def action_view_work_item(self) -> None:
        await self.app.push_screen(WorkItemReadOnlyDetailsScreen(self.work_item_key))


class IssueChildWorkItemsWidget(VerticalScroll):
    HELP = 'See Subtasks section in the help'
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
    def help_anchor(self) -> str:
        return '#subtasks'

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
        """Updates the list of work items that are subtasks of the currently-selected item.

        Args:
            items: the list of items that are subtasks of the current work item.

        Returns:
            None
        """

        self.remove_children()
        if not items:
            return
        rows: list[ChildWorkItemCollapsible] = []
        for issue in items:
            children: list[Widget] = [
                Static(Text(f'Type: {issue.issue_type.name}')),
                Static(Text(f'Assignee: {issue.display_assignee()}')),
            ]
            if browsable_url := build_external_url_for_issue(issue.key):
                children.append(
                    Link(
                        browsable_url, url=browsable_url, tooltip='open link in the default browser'
                    )
                )
            children.append(
                Rule(classes='rule-horizontal-compact-70'),
            )
            children.append(Static(Text(issue.cleaned_summary())))

            collapsible = ChildWorkItemCollapsible(
                *children,
                title=Text(issue.cleaned_summary(max_length=70)),
                work_item_key=issue.key,
            )
            collapsible.border_subtitle = issue.status_name
            if collapsible_color := get_style_for_work_item_status(issue.status_name):
                collapsible.styles.border = ('round', collapsible_color)

            rows.append(collapsible)
        self.mount_all(rows)
