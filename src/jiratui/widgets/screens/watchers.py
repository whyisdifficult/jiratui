from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label, Static

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import Watchers
from jiratui.utils.ui_actions import Actionable, UIAction


@dataclass
class WorkItemWatchersUpdateRequest:
    """"""

    work_item_key: str
    watch: bool
    """If true then the user wants to "watch" the work item; otherwise the user does not want to "watch" the work
    item."""
    update: bool
    """If true then the watching status of the user must be updated based on the value of `watch`."""


class WorkItemWatchersScreen(Actionable, ModalScreen[WorkItemWatchersUpdateRequest]):
    """A modal screen that allows users to view the users watching an item and update the user's watching status."""

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.WATCH_WORK_ITEM,
        SupportedActions.UNWATCH_WORK_ITEM,
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

    BINDINGS = [  # type:ignore[assignment]
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ] + [Binding('escape', 'app.pop_screen', 'Close')]

    def __init__(self, work_item_key: str):
        super().__init__()
        self.__work_item_key = work_item_key
        self.__watching_enabled = True
        self.__unwatching_enabled = False

    @property
    def vertical_container(self) -> Vertical:
        return self.query_one(Vertical)

    @property
    def message(self) -> Static:
        return self.query_one('#message', Static)

    @property
    def watching_status_field(self) -> Label:
        return self.query_one('#watching_status', Label)

    @property
    def datatable(self) -> DataTable:
        return self.query_one(DataTable)

    def compose(self) -> ComposeResult:
        with Vertical():
            label = Label('', id='watching_status')
            label.styles.display = 'none'
            yield label
            yield Static(id='message')
            data_table: DataTable = DataTable(cursor_type='row')
            data_table.display = False
            yield data_table
        yield Footer(compact=True, show_command_palette=False)

    def on_mount(self) -> None:
        self.vertical_container.border_title = f'Watching - {self.__work_item_key}'
        self.run_worker(self._populate_table)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""

        if action == SupportedActions.WATCH_WORK_ITEM.value and not self.__watching_enabled:
            return False
        if action == SupportedActions.UNWATCH_WORK_ITEM.value and not self.__unwatching_enabled:
            return False
        return True

    async def _populate_table(self) -> None:
        response: APIControllerResponse = await self.app.api.get_work_item_watchers(  # type:ignore[attr-defined]
            issue_id_or_key=self.__work_item_key
        )
        if response.success and response.result:
            watchers: Watchers = response.result
            self.__watching_enabled = not watchers.is_watching
            self.__unwatching_enabled = watchers.is_watching
            if watchers.is_watching:
                self.watching_status_field.content = 'Watching'
                self.watching_status_field.styles.display = 'block'
            self.datatable.clear()
            if watchers.watchers:
                self.datatable.add_columns('Name')
                for watcher in watchers.watchers:
                    self.datatable.add_row(watcher.display_name)
                self.datatable.border_subtitle = f'{watchers.count} watchers'
                self.datatable.border_title = 'Watchers'
                self.datatable.display = True
                self.message.display = False
            else:
                self.message.content = 'The work item does not have watchers yet.'
                self.message.display = True
        self.refresh_bindings()

    def action_watch_work_item(self) -> None:
        self.dismiss(WorkItemWatchersUpdateRequest(self.__work_item_key, True, update=True))

    def action_unwatch_work_item(self) -> None:
        self.dismiss(WorkItemWatchersUpdateRequest(self.__work_item_key, False, update=True))
