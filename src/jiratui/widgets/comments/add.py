from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, TextArea


class AddCommentScreen(Screen[str]):
    """A modal screen that allows users to add a comment to a work item.

    The screen does not add the comment to the work item. Instead, it returns the comment's text to the caller via the
    `dismiss()` call and the caller will proceed to add the comment via the API.
    """

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]

    def __init__(self, work_item_key: str | None = None):
        super().__init__()
        self.__work_item_key = work_item_key
        self.title = f'Add comment to the work item {self.__work_item_key}'

    @property
    def comment_textarea(self) -> TextArea:
        return self.query_one(TextArea)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-comment-button-save', expect_type=Button)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.title
        with vertical:
            yield Static(
                Text(
                    'Tip: tab works as indentation control. Use Escape or shift+tab to focus/unfocus elements in the screen.'
                ),
                classes='tip',
            )
            textarea = TextArea.code_editor(
                '', language='markdown', show_line_numbers=False, compact=True
            )
            textarea.border_title = 'Comment'
            textarea.border_subtitle = 'Markdown Enabled'
            yield textarea
            with ItemGrid(classes='add-comment-grid-buttons'):
                yield Button('Save', variant='success', id='add-comment-button-save', disabled=True)
                yield Button('Cancel', variant='error', id='add-comment-button-quit')

    @on(TextArea.Changed, 'TextArea')
    def validate_comment(self):
        value = self.comment_textarea.text
        self.save_button.disabled = False if (value and value.strip()) else True

    @on(Button.Pressed, '#add-comment-button-save')
    def handle_save(self) -> None:
        self.dismiss(self.comment_textarea.text.strip() or '')

    @on(Button.Pressed, '#add-comment-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss('')
