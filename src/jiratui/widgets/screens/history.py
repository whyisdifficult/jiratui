from dataclasses import dataclass

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Rule, Static

from jiratui.utils.history import HistoryManager
from jiratui.utils.urls import build_external_url_for_issue


class HistoryWorkItemsTable(DataTable):
    """A [DataTable](textual.widgets.DataTable) that displays the entries in the recent history.

    This table is responsible for:
    - posting the message [LoadWorkItem](#jiratui.widgets.screens.history.HistoryWorkItemsTable.LoadWorkItem)
    when the user selects a data row that contains a work item key.
    - copying into the clipboard the key of a selected item.
    - copying into the clipboard the url of a selected item.
    - opening in the browser a selected item.

    **See Also**
    - [Use Case](#use-case-recent-history)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__current_work_item_key: str | None = None

    @dataclass
    class LoadWorkItem(Message):
        work_item_key: str

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Posts the message [LoadWorkItem](#jjiratui.widgets.screens.history.HistoryWorkItemsTable.LoadWorkItem)
        to ask the caller to search the work item displayed in the row.

        Args:
            event: the event that triggered this.
        """

        if event.row_key and event.row_key.value:
            if key := event.row_key.value.split(':')[-1]:
                self.post_message(self.LoadWorkItem(key))

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


class HistoryScreen(ModalScreen[str]):
    """A modal screen that displays the recent history of work items viewed, created or updated.

    The screen is responsible for:

    - retrieving the entries in the history using the `HistoryManager`.
    - deleting the history when the user requests it.
    - handling the message [LoadWorkItem](#jiratui.widgets.screens.history.HistoryWorkItemsTable.LoadWorkItem) and
    requesting the main screen to search the work item that was selected by the user from the table.

    **See Also**
    - [Use Case: Manage Recent History](#use-case-recent-history)
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
        Binding(
            key='d',
            action='empty_recent_history',
            description='Empty History',
            show=True,
            key_display='d',
            tooltip='Empty History',
        ),
    ]
    TITLE = 'Recent History'

    def __init__(self, manager: HistoryManager):
        super().__init__()
        self.__history_manager = manager

    def compose(self) -> ComposeResult:
        vertical = VerticalScroll()
        vertical.border_title = self.TITLE
        with vertical:
            yield Static(
                f'List of recently viewed, created or updated work items. Shows the last {self.__history_manager.LIMIT} items.',
                classes='message-tip',
            )
            yield Rule()
            yield HistoryWorkItemsTable(cursor_type='row', classes='recent-history-table')
        yield Footer(show_command_palette=False, compact=True)

    async def on_mount(self) -> None:
        table = self.query_one(HistoryWorkItemsTable)
        table.add_columns(*['Key', 'Type', 'Status', 'Summary'])
        self._fill_in_table(table)

    @on(HistoryWorkItemsTable.LoadWorkItem)
    def _dismiss_with_work_item_key(self, message: HistoryWorkItemsTable.LoadWorkItem) -> None:
        self.dismiss(message.work_item_key)
        message.stop()  # no need to propagate the message

    def action_empty_recent_history(self) -> None:
        self.__history_manager.empty()
        table = self.query_one(HistoryWorkItemsTable)
        table.clear()
        self._fill_in_table(table)

    def _fill_in_table(self, table: HistoryWorkItemsTable) -> None:
        for entry in self.__history_manager.get_history():
            entry_summary = (
                f'{entry.summary[:65]}...' if len(entry.summary) > 65 else entry.summary or '-'
            )
            table.add_row(
                *[entry.key, entry.item_type or '-', entry.status or '-', entry_summary],
                key=f'key:{entry.key}',
            )
