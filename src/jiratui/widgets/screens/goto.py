from dataclasses import dataclass

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Rule, Static
from textual.worker import Worker

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse, RelatedJiraIssue
from jiratui.utils.urls import build_external_url_for_issue


class GoToItemsTable(DataTable):
    """A Textual's [DataTable](#textual.widgets.DataTable) to shows work items.

    The table is responsible for:

    - Copying into the clipboard the URL of a selected work item.
    - Copying into the clipboard the Key of a selected work item.
    - Opening in the browser a work item selected by the user.

    **See Also**:
    - [Use Cases](#use-case-goto-screen)
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
        Binding(
            key='ctrl+o',
            action='open_issue_in_browser',
            description='Browse',
            show=True,
            key_display='^o',
            tooltip='Open in browser',
        ),
        Binding(
            key='ctrl+k',
            action='copy_issue_key',
            description='Copy Key',
            show=True,
            key_display='^k',
            tooltip='Copy key',
        ),
        Binding(
            key='ctrl+j',
            action='copy_issue_url',
            description='Copy URL',
            show=True,
            key_display='^j',
            tooltip='Copy URL',
        ),
    ]

    @dataclass
    class WorkItemSelected(Message):
        """The message posted by this table when the user selects a work item, i.e. presses "enter" in a row."""

        work_item_key: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__current_work_item_key: str | None = None

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Posts the message [WorkItemSelected](#jiratui.widgets.screens.goto.GoToItemsTable.WorkItemSelected)
        to ask the caller to search the work item displayed in the row.

        Args:
            event: the event that triggered this.
        """

        if event.row_key and event.row_key.value:
            if key := event.row_key.value.split(':')[-1]:
                self.post_message(self.WorkItemSelected(key))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Stores the key of the currently-highlighted item."""
        if event.row_key:
            self.__current_work_item_key = event.row_key.value.split(':')[-1]

    def action_open_issue_in_browser(self) -> None:
        """Opens the currently-selected item in the default browser."""
        if self.__current_work_item_key:
            self.notify('Opening Work Item in the browser...')
            self.app.open_url(build_external_url_for_issue(self.__current_work_item_key))

    def action_copy_issue_key(self) -> None:
        """Copy to the clipboard the key of the item."""
        if self.__current_work_item_key:
            self.app.copy_to_clipboard(self.__current_work_item_key)
            self.notify('Work item Key copied!')

    def action_copy_issue_url(self) -> None:
        """Copy to the clipboard the URL of the item."""
        if self.__current_work_item_key:
            if url := build_external_url_for_issue(self.__current_work_item_key):
                self.app.copy_to_clipboard(url)
                self.notify('Work item URL copied!')


class GotToScreen(ModalScreen[str]):
    """A modal screen that display work items related to another work item.

    The screen is responsible for:

    - Fetching the details of the given work item.
    - Fetching the details of the given work item's parent (if any).
    - Fetching the details of the items related to the given work item.
    - Fetching the details of the subtasks of the given work item.
    - Populating data tables with basic details of all related items.
    - Handling the message [GoToItemsTable.WorkItemSelected](#jiratui.widgets.screens.goto.GoToItemsTable.WorkItemSelected)
    to request the main screen to search a work item based on its key.

    **See Also**:
    - [Use Case](#use-case-goto-screen)
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
    ]
    TITLE = 'Related Work Items'

    def __init__(self, work_item_key: str, controller: APIController):
        super().__init__()
        self.__work_item_key = work_item_key
        self.__controller = controller

    @property
    def table_subtasks(self) -> GoToItemsTable:
        return self.query_one('#subtasks', expect_type=GoToItemsTable)

    @property
    def table_related(self) -> GoToItemsTable:
        return self.query_one('#related', expect_type=GoToItemsTable)

    @property
    def table_parent(self) -> GoToItemsTable:
        return self.query_one('#parent', expect_type=GoToItemsTable)

    @property
    def table_basic_details(self) -> GoToItemsTable:
        return self.query_one(GoToItemsTable)

    def compose(self) -> ComposeResult:
        vertical = VerticalScroll()
        vertical.border_title = self.TITLE
        with vertical:
            yield Static(
                'Select and press enter in a row to search the work item.', classes='message-tip'
            )
            yield Rule()
            details_table = GoToItemsTable(
                cursor_type='row', show_header=False, classes='go-to-items-table'
            )
            details_table.border_title = self.__work_item_key
            yield details_table
            subtasks_table = GoToItemsTable(
                id='subtasks', cursor_type='row', classes='go-to-items-table'
            )
            subtasks_table.add_columns(*['Key', 'Type', 'Status', 'Summary'])
            subtasks_table.display = False
            subtasks_table.border_title = 'Subtasks'
            yield subtasks_table
            related_tasks_table = GoToItemsTable(
                id='related', cursor_type='row', classes='go-to-items-table'
            )
            related_tasks_table.add_columns(*['Key', 'Type', 'Status', 'Relation', 'Summary'])
            related_tasks_table.display = False
            related_tasks_table.border_title = 'Related Work Items'
            yield related_tasks_table
            parent_table = GoToItemsTable(
                id='parent', cursor_type='row', classes='go-to-items-table'
            )
            parent_table.add_columns(*['Key', 'Type', 'Status', 'Summary'])
            parent_table.display = False
            parent_table.border_title = 'Parent'
            yield parent_table
        yield Footer(show_command_palette=False, compact=True)

    async def on_mount(self) -> None:
        # fetch the details of the work item
        get_issue_response: APIControllerResponse = await self.__controller.get_issue(
            issue_id_or_key=self.__work_item_key,
        )
        if (
            not get_issue_response.success
            or not get_issue_response.result
            or not get_issue_response.result.issues
        ):
            self.notify(
                'Unable to find the selected work item', title='Find Work Item', severity='error'
            )
        else:
            result: JiraIssueSearchResponse = get_issue_response.result
            work_item: JiraIssue = result.issues[0]

            table = self.table_basic_details
            table.clear()
            table.add_columns(*['Property', 'Value'])
            table.add_row(
                *[Text('Key', justify='right'), Text(work_item.key, justify='left')],
                key=f'key:{work_item.key}',
            )
            table.add_row(
                *[
                    Text('Parent', justify='right'),
                    Text(work_item.parent_key or '-', justify='left'),
                ],
                key=f'key:{work_item.parent_key}' if work_item.parent_key else None,
            )

            # fetch the details of the subtasks
            self.run_worker(self._get_subtasks(), name='get_subtasks')

            # fetch the details of the parent; if any
            if work_item.parent_key:
                self.run_worker(self._get_parent(work_item.parent_key), name='get_parent')

            # get the related tasks
            related_issues: list[RelatedJiraIssue] = work_item.related_issues or []
            if related_issues:
                self._fill_in_related_work_items_table(related_issues)

    def _fill_in_subtasks_table(self, tasks: list[JiraIssue]) -> None:
        table = self.table_subtasks
        table.clear()
        if tasks:
            processed: set[str] = set()
            for task in tasks:
                if task.key in processed:
                    continue
                processed.add(task.key)
                task_summary = (
                    f'{task.summary[:65]}...' if len(task.summary) > 65 else task.summary or '-'
                )
                table.add_row(
                    *[task.key, task.issue_type.name or '-', task.status.name or '-', task_summary],
                    key=f'key:{task.key}',
                )
            table.display = True

    def _fill_in_related_work_items_table(self, tasks: list[RelatedJiraIssue]) -> None:
        table = self.table_related
        table.clear()
        if tasks:
            for task in tasks:
                task_summary = (
                    f'{task.summary[:65]}...' if len(task.summary) > 65 else task.summary or '-'
                )
                table.add_row(
                    *[
                        task.key,
                        task.issue_type.name or '-',
                        task.status.name or '-',
                        task.link_type or '',
                        task_summary,
                    ],
                    key=f'key:{task.key}',
                )
            table.display = True

    def _fill_in_parent_table(self, parent: JiraIssue | None) -> None:
        table = self.table_parent
        table.clear()
        if parent:
            parent_summary = (
                f'{parent.summary[:65]}...' if len(parent.summary) > 65 else parent.summary or '-'
            )
            table.add_row(
                *[
                    parent.key,
                    parent.issue_type.name or '-',
                    parent.status.name or '-',
                    parent_summary,
                ],
                key=f'key:{parent.key}',
            )
            table.display = True

    @on(GoToItemsTable.WorkItemSelected)
    def _dismiss_with_work_item_key(self, message: GoToItemsTable.WorkItemSelected) -> None:
        message.stop()  # no need to propagate the message
        self.dismiss(message.work_item_key)

    async def _get_subtasks(self) -> list[JiraIssue]:
        search_issues_response: APIControllerResponse = await self.__controller.search_issues(
            jql_query=f'parent={self.__work_item_key}',
            fields=['id', 'key', 'status', 'summary', 'issuetype', 'assignee'],
        )
        if search_issues_response.success and search_issues_response.result:
            return search_issues_response.result.issues or []
        return []

    async def _get_parent(self, key: str) -> JiraIssue | None:
        parent_search_response: APIControllerResponse = await self.__controller.get_issue(
            issue_id_or_key=key,
        )
        if parent_search_response.success and parent_search_response.result:
            parent_search_result: JiraIssueSearchResponse = parent_search_response.result
            if parent_search_result.issues:
                return parent_search_result.issues[0]
        return None

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == 'get_subtasks':
            self._fill_in_subtasks_table(event.worker.result or [])
        if event.worker.name == 'get_parent':
            self._fill_in_parent_table(event.worker.result)
