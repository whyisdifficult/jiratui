from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmationScreen(ModalScreen[bool]):
    """Screen with a dialog to confirm an action."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message or 'Are you sure you want to perform this action?'

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.message, id='confirmation-question'),
            Button('Accept', variant='primary', id='confirmation-button-accept'),
            Button('Cancel', variant='error', id='confirmation-button-cancel'),
            id='confirmation-dialog',
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'confirmation-button-cancel':
            self.dismiss(False)
        else:
            self.dismiss(True)
