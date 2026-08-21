from dataclasses import dataclass

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Link, Rule, Static

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue
from jiratui.utils.styling import get_style_for_work_item_status
from jiratui.utils.ui_actions import Actionable, UIAction
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.messages import SearchWorkItem
from jiratui.widgets.screens.confirmation import ConfirmationScreen
from jiratui.widgets.screens.goto import GoToScreen
from jiratui.widgets.screens.work_item_quick_view import WorkItemQuickViewScreen


@dataclass
class WorkItemSubtasks:
    work_item_key: str
    project_key: str | None = None
    issues: list[JiraIssue] | None = None


class ChildWorkItemCollapsible(Actionable, Collapsible, inherit_bindings=False):  # type:ignore[call-arg]
    """A collapsible to show the work items that are children of another work item.

    This widget is responsible for:

    - opening the modal screen [WorkItemQuickViewScreen](#jiratui.widgets.screens.work_item_quick_view.WorkItemQuickViewScreen)
    to display the details of the work item selected.
    - posting the message [SearchWorkItem](#jiratui.widgets.messages.SearchWorkItem)
    when the screen [WorkItemQuickViewScreen](#jiratui.widgets.screens.work_item_quick_view.WorkItemQuickViewScreen) is
    dismissed with a work item key.

    **See Also**:
    - [Architecture](#architecture-work-item-subtasks-classes)
    - [Use Case: Open Go-To Screen](#use-case-subtasks-goto-screen)
    """

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.VIEW_WORK_ITEM,
        SupportedActions.OPEN_GO_TO_SCREEN,
        SupportedActions.DELETE_WORK_ITEM,
    ]:
        data = key_bindings.get(supported_action_id.value, {})
        ACTIONS.append(
            UIAction(
                action=supported_action_id.value,
                keys=data.get('keys', []),
                show=data.get('show', False),
                description=data.get('description'),
                tooltip=data.get('tooltip', ''),
            )
        )

    BINDINGS = [
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ]

    @dataclass
    class WorkItemDeleted(Message):
        work_item_key: str

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
                GoToScreen(self.work_item_key, self.app.api),  # type:ignore[attr-defined]
                callback=self._close_goto_screen,
            )
        elif not self.work_item_key:
            self.notify('Select/Highlight an item to view its related items')
        else:
            self.notify('This feature is disabled. Check config.enable_goto', severity='warning')

    async def action_delete_work_item(self) -> None:
        if self.work_item_key:
            await self.app.push_screen(
                ConfirmationScreen(
                    message='Are you sure you want to delete this item?',
                    title=f'Delete Work Item {self.work_item_key}',
                    warning_message=f'Warning: if the work item {self.work_item_key} has subtasks, deleting it will also delete all its subtasks!',
                ),
                callback=self._delete_work_item,
            )

    def _delete_work_item(self, delete: bool) -> None:
        if delete:
            self.post_message(self.WorkItemDeleted(self.work_item_key))

    def _close_goto_screen(self, work_item_key: str) -> None:
        # sends a message to request the handler, the Main Screen, to search for the work item with the given key
        if work_item_key:
            self.post_message(SearchWorkItem(work_item_key))

    def _load_work_item_after_viewing(self, work_item_key: str | None = None) -> None:
        if work_item_key:
            self.post_message(SearchWorkItem(work_item_key))


class IssueChildWorkItemsWidget(Actionable, VerticalScroll, inherit_bindings=False):  # type:ignore[call-arg]
    """A container for displaying the subtasks of a work item.

    This class defines a key binding to open a modal screen to allow users to create a new work item as a subtask of
    the work item currently selected. Adding the subtask is handled by the main screen.

    **See Also**:
    - [Architecture](#architecture-work-item-subtasks-classes)
    """

    issues: Reactive[WorkItemSubtasks | None] = reactive(None, always_update=True)

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.CREATE_WORK_ITEM_SUBTASK,
        SupportedActions.PAGE_UP,
        SupportedActions.PAGE_DOWN,
        SupportedActions.SCROLL_HOME,
        SupportedActions.SCROLL_END,
        SupportedActions.SCROLL_UP,
        SupportedActions.SCROLL_DOWN,
    ]:
        data = key_bindings.get(supported_action_id.value, {})
        ACTIONS.append(
            UIAction(
                action=supported_action_id.value,
                keys=data.get('keys', []),
                show=data.get('show', False),
                description=data.get('description'),
                tooltip=data.get('tooltip', ''),
            )
        )

    BINDINGS = [
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ]

    HELP = 'See Subtasks section in the help'

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
                'Select a work item before attempting to create a subtask.',
                title='No item selected',
                severity='warning',
            )

    @on(ChildWorkItemCollapsible.WorkItemDeleted)
    async def delete_work_item(self, event: ChildWorkItemCollapsible.WorkItemDeleted) -> None:
        if event.work_item_key:
            response: APIControllerResponse = await self.app.api.delete_work_item(  # type:ignore[attr-defined]
                event.work_item_key
            )
            if response.success:
                # do not fetch subtasks to make it faster
                self.notify(f'Deleted {event.work_item_key}', title='Delete Work Item')
                self.issues = WorkItemSubtasks(
                    work_item_key=self.issues.work_item_key,
                    project_key=self.issues.project_key,
                    issues=[
                        item for item in self.issues.issues or [] if item.key != event.work_item_key
                    ],
                )
            else:
                self.notify(
                    f'Failed to delete the item {event.work_item_key}',
                    title='Delete Work Item',
                    severity='error',
                )
                if response.error:
                    self.notify(response.error, title='Delete Work Item', severity='error')

    def watch_issues(self, work_item_subtasks: WorkItemSubtasks | None = None) -> None:
        """Updates the list of work items that are subtasks of the currently-selected item.

        Args:
            work_item_subtasks: the subtasks associated to a work item. This contains the work item's key and the work
            item's project's key as well.

        Returns:
            None
        """

        # reset the widget's data
        self.remove_children(ChildWorkItemCollapsible)
        self._work_item_key = None
        self._work_item_project_key = None

        if work_item_subtasks is None:
            return

        self._work_item_key = work_item_subtasks.work_item_key
        self._work_item_project_key = work_item_subtasks.project_key
        rows: list[ChildWorkItemCollapsible] = self._build_collapsible_subtasks_widgets(
            work_item_subtasks.issues
        )
        self.mount_all(rows)

    @staticmethod
    def _build_collapsible_subtasks_widgets(
        items: list[JiraIssue] | None = None,
    ) -> list[ChildWorkItemCollapsible]:
        rows: list[ChildWorkItemCollapsible] = []
        for issue in items or []:
            children: list[Widget] = [
                Static(Text(f'Type: {issue.issue_type.name}')),
                Static(Text(f'Assignee: {issue.display_assignee()}')),
                Rule(classes='rule-horizontal-compact-70'),
                Static(Text(issue.cleaned_summary())),
            ]
            if browsable_url := build_external_url_for_issue(issue.key):
                children.append(
                    Link(
                        browsable_url, url=browsable_url, tooltip='open link in the default browser'
                    )
                )

            collapsible = ChildWorkItemCollapsible(
                *children,
                title=Text(issue.cleaned_summary(max_length=70)),
                work_item_key=issue.key,
            )
            collapsible.border_subtitle = issue.status_name
            if collapsible_color := get_style_for_work_item_status(issue.status_name):
                collapsible.styles.border = ('round', collapsible_color)

            rows.append(collapsible)
        return rows
