from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmationScreen(ModalScreen[bool]):
    """Screen with a dialog to confirm an action."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Screen')]

    def __init__(self, message: str):
        super().__init__()
        self.message = message or 'Are you sure you want to perform this action?'

    def compose(self) -> ComposeResult:
        with Vertical() as vertical:
            vertical.border_title = 'Confirm Action'
            yield Label(self.message, id='confirmation-question')
            with ItemGrid(classes='confirmation-screen-grid-buttons'):
                yield Button('Accept', variant='success', id='confirmation-button-accept')
                yield Button('Cancel', variant='error', id='confirmation-button-cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'confirmation-button-cancel':
            self.dismiss(False)
        else:
            self.dismiss(True)
