from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, TextArea

from jiratui.widgets.base import CustomTitle


class AddCommentScreen(Screen[str]):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'New Comment'

    def __init__(self, work_item_key: str | None = None):
        super().__init__()
        self.work_item_key = work_item_key
        self.title = f'{self.TITLE} - Work Item {self.work_item_key}'

    @property
    def comment_textarea(self) -> TextArea:
        return self.query_one(TextArea)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-comment-button-save', expect_type=Button)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle(self.title)
            yield TextArea.code_editor('', language='markdown', show_line_numbers=False)
            with ItemGrid(classes='add-comment-grid-buttons'):
                yield Button('Save', variant='success', id='add-comment-button-save', disabled=True)
                yield Button('Cancel', variant='error', id='add-comment-button-quit')

    @on(TextArea.Changed, 'TextArea')
    def validate_comment(self):
        value = self.comment_textarea.text
        self.save_button.disabled = False if (value and value.strip()) else True

    @on(Button.Pressed, '#add-comment-button-save')
    def handle_save(self) -> None:
        self.dismiss(self.comment_textarea.text or '')

    @on(Button.Pressed, '#add-comment-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss('')
