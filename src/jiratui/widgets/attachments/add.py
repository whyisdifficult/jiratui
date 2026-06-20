from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, DirectoryTree, Input, Rule, Static

from jiratui.config import CONFIGURATION


class AddAttachmentScreen(Screen[str]):
    """The screen to select files to attach and attach them to a work item.

    The screen is responsible for:
    - showing a directory tree to let the user select the file to upload.
    - handling the `Checkbox.Changed` event and refreshing the directory tree when the user selects to use the
    last-used directory.

    The screen uses the application's session object [ContextualSession](#jiratui.utils.session.ContextualSession) to
    extract/store the recently-used directory.

    **See Also**:
    - [Attach File Screen Design](#components-attach-file-screen)
    - [Use Case: Attach File](#use-case-attach-file)
    - [Architecture](#architecture-work-item-attachments-classes)
    """

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'Attach File'
    DEFAULT_ATTACHMENTS_SOURCE_DIRECTORY = '/'
    """The default source directory for searching files to attach. This can be overridden by the config variable
    `attachments_source_directory`."""

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

    @property
    def directory_tree(self) -> DirectoryTree:
        return self.query_one('#attachment-directory-tree', expect_type=DirectoryTree)

    @property
    def right_hand_side_vertical_widget(self) -> Vertical:
        return self.query_one('#right-hand-side-panel', expect_type=Vertical)

    def _get_initial_directory_for_upload(self, use_latest_path: bool = False) -> str:
        if use_latest_path and (
            recently_used_attachment_path := self.app.session.get('recently_used_attachment_path')  # type:ignore[attr-defined]
        ):
            return recently_used_attachment_path
        if attachments_source_directory := CONFIGURATION.get().attachments_source_directory:
            if cleaned := attachments_source_directory.strip():
                return cleaned
        return self.DEFAULT_ATTACHMENTS_SOURCE_DIRECTORY

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.title
        with vertical:
            yield Static(
                Text(
                    'Important: uploading large files can make the interface temporarily unresponsive',
                    style='italic orange',
                )
            )
            yield Rule()
            yield Checkbox('Use last directory', classes='input-checkbox')
            with Horizontal():
                yield DirectoryTree(
                    self._get_initial_directory_for_upload(), id='attachment-directory-tree'
                )
                with Vertical(id='right-hand-side-panel'):
                    yield FileNameInputWidget()
                    with ItemGrid(classes='add-attachment-grid-buttons'):
                        yield Button(
                            'Save',
                            variant='success',
                            id='add-attachment-button-save',
                            disabled=True,
                        )
                        yield Button('Cancel', variant='error', id='add-attachment-button-quit')

    @on(Checkbox.Changed)
    async def _change_directory(self, event: Checkbox.Changed) -> None:
        # change the filesystem view to the last-used directory (if any is set)
        # for the lack of a better way (see https://github.com/Textualize/textual/issues/2056) we remove the directory
        # tree widget and re-create it with the new root directory
        if self.app.session.get('recently_used_attachment_path'):  # type:ignore[attr-defined]
            directory = self._get_initial_directory_for_upload(use_latest_path=event.value)
            await self.directory_tree.remove()
            await self.mount(
                DirectoryTree(directory, id='attachment-directory-tree'),
                before=self.right_hand_side_vertical_widget,
            )

    def on_mount(self) -> None:
        if cb := self.query_one_optional(Checkbox):
            cb.value = True if self.app.session.get('recently_used_attachment_path') else False


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
