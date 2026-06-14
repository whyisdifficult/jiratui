from dataclasses import dataclass

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Link, Rule, Static

from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue
from jiratui.utils.styling import get_style_for_work_item_status
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.messages import SearchWorkItem
from jiratui.widgets.screens.goto import GotToScreen
from jiratui.widgets.screens.work_item_quick_view import WorkItemQuickViewScreen


@dataclass
class WorkItemSubtasks:
    work_item_key: str
    project_key: str | None = None
    issues: list[JiraIssue] | None = None


class ChildWorkItemCollapsible(Collapsible):
    """A collapsible to show the work items that are children of another work item.

    This widget is responsible for:

    - opening the modal screen [WorkItemQuickViewScreen](#jiratui.widgets.screens.work_item_quick_view.WorkItemQuickViewScreen)
    to display the details of the work item selected.
    - posting the message [SearchWorkItem](#jiratui.widgets.messages.SearchWorkItem)
    when the screen [WorkItemQuickViewScreen](#jiratui.widgets.screens.work_item_quick_view.WorkItemQuickViewScreen) is
    dismissed with a work item key.

    **See Also**:
    - [Architecture](#architecture-work-item-subtasks-classes)
    """

    BINDINGS = [
        Binding(
            key='v',
            action='view_work_item',
            description='Quick View',
            show=True,
            key_display='v',
        ),
        Binding(
            key='f6',
            action='open_go_to_screen',
            description='Related',
            show=True,
            key_display='f6',
            tooltip='View related work items',
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
        await self.app.push_screen(
            WorkItemQuickViewScreen(self.work_item_key),
            callback=self._load_work_item_after_viewing,
        )

    async def action_open_go_to_screen(self) -> None:
        """Opens a modal screen to show the work items related to the work item selected by the user.

        The screen will be opened only if `config.enable_goto == True` and there is a work item selected.

        Returns:
            None
        """

        if CONFIGURATION.get().enable_goto and self.work_item_key:
            self.app.push_screen(
                GotToScreen(self.work_item_key, self.app.api),  # type:ignore[attr-defined]
                callback=self._close_goto_screen,
            )
        elif not self.work_item_key:
            self.notify('Select/Highlight an item to view its related items')
        else:
            self.notify('This feature is disabled. Check config.enable_goto', severity='warning')

    def _close_goto_screen(self, work_item_key: str) -> None:
        # sends a message to request the handler, the Main Screen, to search for the work item with the given key
        if work_item_key:
            self.post_message(SearchWorkItem(work_item_key))

    def _load_work_item_after_viewing(self, work_item_key: str | None = None) -> None:
        if work_item_key:
            self.post_message(SearchWorkItem(work_item_key))


class IssueChildWorkItemsWidget(VerticalScroll):
    """A container for displaying the subtasks of a work item.

    This class defines a key binding to open a modal screen to allow users to create a new work item as a subtask of
    the work item currently selected. Adding the subtask is handled by the main screen.

    **See Also**:
    - [Architecture](#architecture-work-item-subtasks-classes)
    """

    HELP = 'See Subtasks section in the help'
    issues: Reactive[WorkItemSubtasks | None] = reactive(None, always_update=True)

    BINDINGS = [
        # override the binding to be able to inject the current work item as a prent of the subtask
        Binding(
            key='ctrl+n',
            action='create_work_item_subtask',
            description='New Subtask',
            show=True,
            key_display='^n',
        ),
    ]

    class CreateSubtask(Message):
        """Posted when the user wants to add a subtask to the work item.

        It holds the key of the work item's project and the key of the subtask's parent work item.
        """

        def __init__(self, project_key: str, parent_work_item_key: str) -> None:
            self.project_key = project_key
            self.parent_work_item_key = parent_work_item_key
            super().__init__()

    def __init__(self):
        super().__init__(id='issue_subtasks')
        self._work_item_key: str | None = None
        self._work_item_project_key: str | None = None

    @property
    def help_anchor(self) -> str:
        return '#subtasks'

    async def action_create_work_item_subtask(self) -> None:
        if self._work_item_key:
            self.post_message(
                self.CreateSubtask(
                    project_key=self._work_item_project_key,
                    parent_work_item_key=self._work_item_key,
                )
            )
        else:
            self.notify(
                'Select a work item before attempting to create a subtask.', title='Create Subtask'
            )

    def watch_issues(self, work_item_subtasks: WorkItemSubtasks | None = None) -> None:
        """Updates the list of work items that are subtasks of the currently-selected item.

        Args:
            work_item_subtasks: the subtasks associated to a work item. This contains the work item's key and the work
            item's project's key as well.

        Returns:
            None
        """

        self.remove_children()

        if work_item_subtasks is None:
            return

        self._work_item_key = work_item_subtasks.work_item_key
        self._work_item_project_key = work_item_subtasks.project_key

        rows: list[ChildWorkItemCollapsible] = []
        for issue in work_item_subtasks.issues or []:
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
