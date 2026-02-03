from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, TextArea


class EditDescriptionScreen(Screen[str]):
    """Modal screen for editing work item description."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'Edit Description'

    def __init__(self, work_item_key: str, current_description: str = ''):
        super().__init__()
        self.work_item_key = work_item_key
        self.current_description = current_description
        self.title = f'{self.TITLE} - Work Item {self.work_item_key}'

    @property
    def description_textarea(self) -> TextArea:
        return self.query_one(TextArea)

    @property
    def save_button(self) -> Button:
        return self.query_one('#edit-description-button-save', expect_type=Button)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.title
        with vertical:
            yield TextArea.code_editor(
                self.current_description, language='markdown', show_line_numbers=False
            )
            with ItemGrid(classes='edit-description-grid-buttons'):
                yield Button('Save', variant='success', id='edit-description-button-save')
                yield Button('Cancel', variant='error', id='edit-description-button-quit')

    @on(Button.Pressed, '#edit-description-button-save')
    def handle_save(self) -> None:
        self.dismiss(self.description_textarea.text or '')

    @on(Button.Pressed, '#edit-description-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss(None)
