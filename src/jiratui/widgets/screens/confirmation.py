from rich.text import Text
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ConfirmationScreen(ModalScreen[bool]):
    """Screen with a dialog to confirm an action."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Screen')]

    def __init__(
        self,
        message: str | None = None,
        title: str | None = None,
        warning_message: str | None = None,
    ):
        super().__init__()
        self.message = message or 'Are you sure you want to perform this action?'
        self.title = title
        self.warning_message = warning_message

    def compose(self) -> ComposeResult:
        with Vertical() as vertical:
            vertical.border_title = self.title or 'Confirm Action'
            yield Label(self.message, classes='confirmation-question-label')
            if self.warning_message:
                yield Static(
                    Text(self.warning_message, style='italic orange'),
                    classes='confirmation-warning-message',
                )
            else:
                yield Static(classes='confirmation-warning-message')
            with ItemGrid(classes='confirmation-screen-grid-buttons'):
                yield Button(
                    'Accept', variant='success', flat=True, classes='confirmation-button-accept'
                )
                yield Button(
                    'Cancel',
                    variant='error',
                    id='confirmation-button-cancel',
                    flat=True,
                    classes='confirmation-button-cancel',
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'confirmation-button-cancel':
            self.dismiss(False)
        else:
            self.dismiss(True)
