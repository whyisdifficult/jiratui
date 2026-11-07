from dataclasses import dataclass
from enum import Enum

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class WorkItemContextMenuOptionAction(Enum):
    """The possible actions a user can select from the context menu."""

    CLONE_WORK_ITEM = 'clone_work_item'
    ARCHIVE_WORK_ITEM = 'archive_work_item'

    @classmethod
    def options(cls):
        return [(item.value.replace('_', ' ').title(), item.value) for item in cls]


@dataclass
class WorkItemContextMenuSelection:
    """The result returned by the context menu screen when the user selects an action."""

    work_item_key: str
    action_id: WorkItemContextMenuOptionAction


class WorkItemContextMenu(ModalScreen[WorkItemContextMenuSelection]):
    """A modal screen to display a contextual menu to execute actions on a work item."""

    BINDINGS = [Binding('escape', 'app.pop_screen', 'Close')]

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key
        """The key of the work item to which the actions in the menu will be applied"""
        self.__menu_options: list[tuple[str, str]] = WorkItemContextMenuOptionAction.options()

    @property
    def options_list(self) -> OptionList:
        return self.query_one(OptionList)

    def compose(self) -> ComposeResult:
        yield OptionList()

    def on_mount(self) -> None:
        self.options_list.clear_options()
        for menu_option in self.__menu_options:
            self.options_list.add_option(Option(menu_option[0], id=menu_option[1]))
        self.add_class('open')
        self.options_list.highlighted = 0
        self.focus()

    @on(OptionList.OptionSelected)
    def handle_option_selection(self, message: OptionList.OptionSelected) -> None:
        message.stop()
        if message.option_id:
            self.dismiss(
                WorkItemContextMenuSelection(
                    self._work_item_key, WorkItemContextMenuOptionAction(message.option_id)
                )
            )
