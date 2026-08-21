from dataclasses import dataclass
from inspect import isawaitable
from typing import Any, Awaitable, Callable

from textual.actions import SkipAction
from textual.events import Key


@dataclass
class UIAction:
    """An action that can be triggered by keyboard shortcuts by the user."""

    action: str | Callable[[], Any]
    keys: list[str]
    description: str | None = None
    """An optional description of the action. Useful for when the keybind is displayed in the footer."""
    show: bool = False
    """If True then the keybind will be displayed in the footer."""
    tooltip: str = ''
    """An optional tooltip to display in the footer."""


class Actionable:
    ACTIONS: list[UIAction]

    async def on_key(self, event: Key) -> None:
        try:
            iter(self.ACTIONS)
        except AttributeError:
            return

        func: Callable[[], Any] | None
        for action in self.ACTIONS:
            if check_key(event, action.keys):
                if not isinstance(action.action, str):
                    func = action.action
                else:
                    func = getattr(self, f'action_{action.action}')
                    if not callable(func):
                        continue

                try:
                    result: Any | Awaitable = func()
                except SkipAction:
                    pass
                else:
                    if isawaitable(result):
                        await result

                event.prevent_default().stop()
        return


def check_key(event: Key, key_list: list[str] | str) -> bool:
    if isinstance(key_list, str):
        key_list = [key_list]
    return bool(
        event.key in key_list
        or any(key in key_list for key in event.aliases)
        or (
            event.is_printable
            and event.character in key_list
            # specifically check for space
            and event.character != ' '
        )
    )
