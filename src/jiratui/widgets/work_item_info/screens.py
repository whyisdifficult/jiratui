from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ItemGrid, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, MarkdownViewer, Static, TextArea


class EditTextContentScreen(Screen[dict]):
    """A modal screen that displays a TextArea editor to allow users to edit Plain Text/Markdown content."""

    BINDINGS = [
        Binding('escape', 'app.pop_screen', 'Close'),
        Binding('ctrl+s', 'save_content', 'Save', show=True, key_display='^s'),
    ]

    def __init__(self, content: str, jira_field_key: str, title: str | None = None):
        super().__init__()
        self.__content: str = content
        self.__jira_field_key = jira_field_key
        self.title = title

    @property
    def textarea(self) -> TextArea:
        return self.query_one(TextArea)

    def compose(self) -> ComposeResult:
        with Vertical():
            widget = TextArea.code_editor(
                self.__content,
                language='markdown',
                show_line_numbers=False,
                compact=True,
                theme='css',
            )
            widget.border_title = self.title
            yield widget
            with ItemGrid(classes='edit-grid-buttons'):
                yield Button(
                    'Save',
                    variant='success',
                    id='edit-description-button-save',
                    classes='save-cancel-buttons',
                )
                yield Button(
                    'Cancel',
                    variant='error',
                    id='edit-description-button-quit',
                    classes='save-cancel-buttons',
                )
            yield Static()
        yield Footer(compact=True, show_command_palette=False)

    def on_mount(self):
        self.post_message(TextArea.Changed(self.query_one(TextArea)))

    def save_button(self) -> Button:
        return self.query_one('#edit-description-button-save', Button)

    @on(Button.Pressed, '#edit-description-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})

    @on(Button.Pressed, '#edit-description-button-save')
    def handle_save(self) -> None:
        self.dismiss(
            {'content': self.textarea.text.strip(), 'jira_field_key': self.__jira_field_key}
        )

    def action_save_content(self) -> None:
        self.handle_save()


class DisplayTextContentScreen(ModalScreen):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]

    def __init__(self, content: str, title: str | None = None):
        super().__init__()
        self.__content = content
        self.title = title

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self.__content)
