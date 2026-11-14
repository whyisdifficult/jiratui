from dataclasses import dataclass
from enum import Enum

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.utils.ui_actions import Actionable, UIAction


class ContextMenuAction(Enum):
    """The possible actions a user can select from the context menu."""

    CLONE_WORK_ITEM = 'clone_work_item'
    ARCHIVE_WORK_ITEM = 'archive_work_item'
    VOTES = 'votes'
    WATCHERS = 'watchers'


@dataclass
class ContextMenuOption:
    action_id: ContextMenuAction
    """The name of the action. The action can be handled in the caller by implementing a method named
    `menu_action_{action_id.value}`.
    Example:
    action_id = ContextMenuAction.CLONE_WORK_ITEM
    def menu_action_clone_work_item(work_item_key):
        ...
    """
    label: str


@dataclass
class ContextMenuSelection:
    """The result returned by the context menu screen when the user selects an action."""

    work_item_key: str
    action_id: ContextMenuAction
    """The name of the action. The action can be handled in the caller by implementing a method named
    `menu_action_{action_id.value}`.
    Example:
    action_id = ContextMenuAction.CLONE_WORK_ITEM
    def menu_action_clone_work_item(work_item_key):
        ...
    """


class ContextMenuOptionList(Actionable, OptionList):
    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.CURSOR_UP,
        SupportedActions.CURSOR_DOWN,
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
    ]


class ContextMenu(ModalScreen[ContextMenuSelection]):
    """A modal screen to display a contextual menu to execute actions on a work items."""

    BINDINGS = [Binding('escape', 'app.pop_screen', 'Close')]

    DEFAULT_MENU_OPTIONS = [
        ContextMenuOption(
            action_id=ContextMenuAction.CLONE_WORK_ITEM,
            label='Clone Item...',
        ),
        ContextMenuOption(
            action_id=ContextMenuAction.ARCHIVE_WORK_ITEM,
            label='Archive Item',
        ),
        ContextMenuOption(
            action_id=ContextMenuAction.VOTES,
            label='Vote...',
        ),
        ContextMenuOption(
            action_id=ContextMenuAction.WATCHERS,
            label='Watch...',
        ),
    ]

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key
        """The key of the work item to which the actions in the menu will be applied"""
        self.__menu_options: list[tuple[str, str]] = [
            (option.label, option.action_id.value) for option in self.DEFAULT_MENU_OPTIONS
        ]

    @property
    def options_list(self) -> ContextMenuOptionList:
        return self.query_one(ContextMenuOptionList)

    def compose(self) -> ComposeResult:
        yield ContextMenuOptionList()

    def on_mount(self) -> None:
        self.options_list.clear_options()
        for menu_option in self.__menu_options:
            self.options_list.add_option(Option(menu_option[0], id=menu_option[1]))
        self.add_class('open')
        self.options_list.highlighted = 0
        self.focus()

    @on(ContextMenuOptionList.OptionSelected)
    def _handle_option_selection(self, message: ContextMenuOptionList.OptionSelected) -> None:  # type:ignore[name-defined]
        message.stop()
        if message.option_id:
            self.dismiss(
                ContextMenuSelection(self._work_item_key, ContextMenuAction(message.option_id))
            )
