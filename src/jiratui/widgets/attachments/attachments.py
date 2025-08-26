from typing import cast

from textual import on
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import DataTable

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import Attachment
from jiratui.widgets.attachments.add import AddAttachmentScreen
from jiratui.widgets.confirmation_screen import ConfirmationScreen


class IssueAttachmentsWidget(VerticalScroll):
    HELP = """\
# Attachments

This will display a list of files attached to the selected work item.

To upload a file press `^u` and provide the details in the pop-up that opens. To delete an attachment focus on the
attached file you want to delete and then press `d`.

**Important**: Uploading large files may cause the UI to be unresponsive temporarily. This will depend on the size of
the file.

**Warning**: The application imposes a maximum file size of 10MB.
    """

    BINDINGS = [
        Binding(
            key='ctrl+u',
            action='add_attachment',
            description='Attach File',
            key_display='^u',
        )
    ]

    attachments: Reactive[list[Attachment] | None] = reactive(None)
    NOTIFICATIONS_DEFAULT_TITLE = 'Work Item Attachments'

    def __init__(self):
        super().__init__(id='attachments')
        self._issue_key: str | None = None

    @property
    def issue_key(self) -> str | None:
        return self._issue_key

    @issue_key.setter
    def issue_key(self, value: str | None) -> None:
        self._issue_key = value

    def action_add_attachment(self) -> None:
        """Opens a screen to attach a file to the issue."""

        if self.issue_key:
            self.app.push_screen(AddAttachmentScreen(self.issue_key), self.upload_attachment)
        else:
            self.notify(
                'You need to select a work item before attempting to attach a file.',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
                severity='error',
            )

    def upload_attachment(self, content: str) -> None:
        if content and (file_name := content.strip()):
            self.notify('Uploading attachment...', title=self.NOTIFICATIONS_DEFAULT_TITLE)
            screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
            response: APIControllerResponse = screen.api.add_attachment(self.issue_key, file_name)
            if not response.success:
                self.notify(
                    f'Failed to attach the file: {response.error}',
                    title=self.NOTIFICATIONS_DEFAULT_TITLE,
                    severity='error',
                )
            else:
                self.notify(
                    'File attached successfully',
                    title=self.NOTIFICATIONS_DEFAULT_TITLE,
                )
                current_attachments = self.attachments
                self.attachments = current_attachments + [response.result]

    def watch_attachments(self, attachments: list[Attachment] | None) -> None:
        self.remove_children()
        if not attachments:
            return

        table = AttachmentsDataTable(self.issue_key)
        table.add_columns(*['File Name', 'Size (KB)', 'Added', 'Author'])

        item: Attachment
        for item in attachments:
            table.add_row(
                *[item.filename, item.kb or '-', item.created_date, item.display_author],
                key=item.id,
            )
        self.mount(table)


class AttachmentsDataTable(DataTable):
    BINDINGS = [
        Binding(
            key='d',
            action='delete_attachment',
            description='Delete File',
            key_display='d',
        )
    ]
    NOTIFICATIONS_DEFAULT_TITLE = 'Work Item Attachments'

    def __init__(self, work_item_key: str):
        super().__init__(cursor_type='row')
        self._selected_attachment_id: str | None = None
        self._work_item_key: str | None = work_item_key

    @on(DataTable.RowHighlighted)
    def highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._selected_attachment_id = str(event.row_key.value)

    @on(DataTable.RowSelected)
    def selected(self, event: DataTable.RowSelected) -> None:
        self._selected_attachment_id = str(event.row_key.value)

    async def action_delete_attachment(self) -> None:
        if not self._selected_attachment_id:
            self.notify(
                'Select a row, e.g. by clicking on it, before attempting to delete the file.',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            await self.app.push_screen(
                ConfirmationScreen('Are you sure you want to delete the file?'),
                callback=self.handle_delete_choice,
            )

    def _update_attachments_after_delete(self) -> None:
        updated_attachments: list[Attachment] = []
        for attachment in self.parent.attachments:  # type:ignore[attr-defined]
            if attachment.id == self._selected_attachment_id:
                continue
            updated_attachments.append(attachment)
        self.parent.attachments = updated_attachments  # type:ignore[attr-defined]

    async def handle_delete_choice(self, result: bool) -> None:
        if result is True:
            screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
            response: APIControllerResponse = await screen.api.delete_attachment(
                self._selected_attachment_id
            )
            if not response.success:
                self.notify(
                    f'Failed to delete the file: {response.error}',
                    severity='error',
                    title=self.NOTIFICATIONS_DEFAULT_TITLE,
                )
            else:
                self.notify('File deleted successfully', title=self.NOTIFICATIONS_DEFAULT_TITLE)
                if CONFIGURATION.get().fetch_attachments_on_delete:
                    response = await screen.api.get_issue(
                        self._work_item_key, fields=['attachment']
                    )
                    if not response.success or not (result := response.result):
                        # fallback to removing the attachment manually based on the id
                        self._update_attachments_after_delete()
                    else:
                        self.parent.attachments = result.issues[0].attachments  # type:ignore[attr-defined]
                else:
                    # fallback to removing the attachment manually based on the id
                    self._update_attachments_after_delete()
