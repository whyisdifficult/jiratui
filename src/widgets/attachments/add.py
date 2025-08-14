from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Input, Rule, Static

from src.widgets.base import CustomTitle


class AddAttachmentScreen(Screen[str]):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'Attach File'

    def __init__(self, work_item_key: str | None = None):
        super().__init__()
        self._work_item_key = work_item_key
        self.title = f'{self.TITLE} - Work Item {self._work_item_key}'

    @property
    def file_path_input(self) -> Input:
        return self.query_one('#file-path-input', expect_type=Input)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-attachment-button-save', expect_type=Button)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.file_path_input.value = str(event.path)
        if event.path:
            self.save_button.disabled = False

    @on(Input.Changed, '#file-path-input')
    def validate_input(self):
        if self.file_path_input.value and self.file_path_input.value.strip():
            self.save_button.disabled = False
        else:
            self.save_button.disabled = True

    @on(Button.Pressed, '#add-attachment-button-save')
    def handle_save(self) -> None:
        self.dismiss(self.file_path_input.value or '')

    @on(Button.Pressed, '#add-attachment-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss('')

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle(f'Attach File to Work Item {self._work_item_key}')
            yield Static(
                Text(
                    'Important: uploading large files can make the interface temporarily unresponsive',
                    style='italic orange',
                )
            )
            yield Rule()
            with Horizontal():
                yield DirectoryTree('/', id='attachment-directory-tree')
                with Vertical():
                    yield FileNameInputWidget()
                    with ItemGrid(classes='add-attachment-grid-buttons'):
                        yield Button(
                            'Save',
                            variant='success',
                            id='add-attachment-button-save',
                            disabled=True,
                        )
                        yield Button('Cancel', variant='error', id='add-attachment-button-quit')


class FileNameInputWidget(Input):
    def __init__(self):
        super().__init__(
            id='file-path-input',
            classes='required',
            type='text',
            placeholder='path to the file...',
            tooltip='Enter the file name to upload',
        )
        self.border_title = 'File'
        self.border_subtitle = '(*)'
