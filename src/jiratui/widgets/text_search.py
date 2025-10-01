from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input


class TextSearchScreen(ModalScreen[str]):
    """A modal screen that shows an inout field to allow the user to provide a text for searching work items using
    full-text search."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]

    def compose(self) -> ComposeResult:
        input_term_field = Input(placeholder='Type in to find items')
        input_term_field.border_title = 'Full-Text Search'
        yield input_term_field

    @on(Input.Submitted)
    def request_search(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
