from dataclasses import dataclass
from io import BytesIO
import json
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import DataTable, LoadingIndicator, Markdown, Static, TextArea

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import Attachment
from jiratui.utils.mime import (
    SupportedAttachmentVisualizationMimeTypes,
    can_view_attachment,
    is_image,
)
from jiratui.utils.urls import build_external_url_for_attachment
from jiratui.widgets.attachments.add import AddAttachmentScreen
from jiratui.widgets.confirmation_screen import ConfirmationScreen


@dataclass
class WorkItemAttachments:
    """The data for the reactive attribute that holds the attachments of a work item."""

    work_item_key: str | None = None
    attachments: list[Attachment] | None = None


class AttachmentsDataTable(DataTable):
    """A data table to list the files attached to a work item."""

    BINDINGS = [
        Binding(
            key='d',
            action='delete_attachment',
            description='Delete',
            key_display='d',
            tooltip='Deletes the attachment',
        ),
        Binding(
            key='ctrl+o',
            action='open_attachment',
            description='Browse',
            show=True,
            key_display='^o',
            tooltip='Open file in the browser',
        ),
    ]
    NOTIFICATIONS_DEFAULT_TITLE = 'Work Item Attachments'

    class Deleted(Message):
        """Posted when the user deletes an attachment.

        It holds the key of the work item whose attachment we deleted and the ID of the deleted attachment.
        """

        def __init__(self, work_item_key: str, attachment_id: str) -> None:
            self.work_item_key = work_item_key
            self.attachment_id = attachment_id
            super().__init__()

    def __init__(self, work_item_key: str):
        super().__init__(cursor_type='row')
        self._selected_attachment_id: str | None = None
        self._selected_attachment_file_name: str | None = None
        self._work_item_key: str | None = work_item_key

    @on(DataTable.RowHighlighted)
    def highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handles the event when a user highlights a row.

        We want to store the id of the attachment, the file name of the attachment and the file type. This
        data will be used for displaying images and opening links in the browser.

        Args:
            event: the event triggered when the user highlights a row.

        Returns:
            None
        """
        self._selected_attachment_id = str(event.row_key.value)
        if (row := event.data_table.get_row(event.row_key.value)) and len(row) > 0:
            self._selected_attachment_file_name = row[0]

    @on(DataTable.RowSelected)
    def selected(self, event: DataTable.RowSelected) -> None:
        """Handles the event when a user selects a row.

        We want to store the id of the attachment, the file name of the attachment and the file type. This
        data will be used for displaying images and opening links in the browser.

        Args:
            event: the event triggered when the user selects a row.

        Returns:
            None
        """
        if event.row_key.value:
            self._selected_attachment_id = str(event.row_key.value)
            if (row := event.data_table.get_row(event.row_key.value)) and len(row) > 0:
                self._selected_attachment_file_name = row[0]
                selected_attachment_file_type = row[-1]
                if selected_attachment_file_type:
                    if not can_view_attachment(selected_attachment_file_type.lower()):
                        self.notify(
                            f'The type of file {selected_attachment_file_type} is not supported'
                        )
                    else:
                        self.app.push_screen(
                            ViewAttachmentScreen(
                                self._selected_attachment_id,
                                selected_attachment_file_type,
                                self._selected_attachment_file_name,
                            )
                        )

    async def action_open_attachment(self) -> None:
        """Opens the currently selected attached file in the default browser."""
        if self._selected_attachment_id and self._selected_attachment_file_name:
            self.notify('Opening attachment in the browser...')
            if url := build_external_url_for_attachment(
                self._selected_attachment_id, self._selected_attachment_file_name
            ):
                self.app.open_url(url)

    async def action_delete_attachment(self) -> None:
        """Opens up a modal screen to prompt the user before attempting to delete an attachment."""
        if not self._selected_attachment_id:
            self.notify(
                'Select a row before attempting to delete the file.',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            await self.app.push_screen(
                ConfirmationScreen('Are you sure you want to delete the file?'),
                callback=self.handle_delete_choice,
            )

    async def handle_delete_choice(self, result: bool) -> None:
        """Attempts to delete an attachment if the user agrees.

        Args:
            result: the choice of the user that decides to delete or not an attachment.

        Returns:
            None
        """

        if result:
            self.post_message(self.Deleted(self._work_item_key, self._selected_attachment_id))


class IssueAttachmentsWidget(VerticalScroll):
    """A container for displaying the files attached to a work item.

    This widget is responsible for the following:

    - opening the modal screen that allows users to attach files.
    - processing the result from the modal screen and attaching a file to the work item via the API.
    - deleting attachments from the work item via the API when the message
    `jiratui.widgets.attachments.attachments.AttachmentsDataTable.Deleted` is posted.
    - updating the list of attachments when an attachment is deleted.

    The config variable `config.fetch_attachments_on_delete` controls whether the widget retrieves the attachments from
    the work item after an attachment is deleted.
    """

    HELP = 'See Attachments section in the help'
    BINDINGS = [
        Binding(
            key='ctrl+u',
            action='add_attachment',
            description='Attach',
            key_display='^u',
            tooltip='Attache new file',
        )
    ]

    attachments: Reactive[WorkItemAttachments | None] = reactive(None)
    NOTIFICATIONS_DEFAULT_TITLE = 'Work Item Attachments'

    def __init__(self):
        super().__init__(id='attachments')
        self._issue_key: str | None = None

    @property
    def help_anchor(self) -> str:
        return '#attachments'

    @property
    def issue_key(self) -> str | None:
        return self._issue_key

    @issue_key.setter
    def issue_key(self, value: str | None) -> None:
        self._issue_key = value

    def on_attachments_data_table_deleted(self, message: AttachmentsDataTable.Deleted) -> None:
        """Schedules a task to delete an attachment."""

        self.run_worker(self._delete_attachment(message.work_item_key, message.attachment_id))
        message.stop()  # no need to propagate the message

    @staticmethod
    def _fetch_attachments_on_delete() -> bool:
        return CONFIGURATION.get().fetch_attachments_on_delete

    def _update_attachments_after_delete(self, attachment_id: str) -> None:
        """Updates hte list of attachments displayed in the data table after an attachment is deleted.

        Args:
            attachment_id: the ID of the attachment that was deleted.

        Returns:
            None
        """

        if self.attachments and self.attachments.attachments:
            self.attachments = WorkItemAttachments(
                work_item_key=self.issue_key,
                attachments=[
                    attachment
                    for attachment in self.attachments.attachments
                    if attachment.id != attachment_id
                ],
            )

    async def _delete_attachment(self, work_item_key: str, attachment_id: str) -> None:
        """Attempts to delete an attachment."""

        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await screen.api.delete_attachment(attachment_id)
        if not response.success:
            self.notify(
                f'Failed to delete the file: {response.error}',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            if self._fetch_attachments_on_delete():
                response = await screen.api.get_issue(work_item_key, fields=['attachment'])
                if response.success:
                    if response.result is None or not response.result.issues:
                        # fallback to removing the attachment manually based on the id
                        self._update_attachments_after_delete(attachment_id)
                        self.notify(
                            f'Failed to find the work item with key: {work_item_key}',
                            severity='error',
                            title=self.NOTIFICATIONS_DEFAULT_TITLE,
                        )
                    else:
                        self.attachments = WorkItemAttachments(
                            work_item_key=work_item_key,
                            attachments=response.result.issues[0].attachments,
                        )
                else:
                    # fallback to removing the attachment manually based on the id
                    self._update_attachments_after_delete(attachment_id)
                    self.notify(
                        f'Failed to find the work item with key: {work_item_key}',
                        severity='error',
                        title=self.NOTIFICATIONS_DEFAULT_TITLE,
                    )
            else:
                # fallback to removing the attachment manually based on the id
                self._update_attachments_after_delete(attachment_id)

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
        """Uploads a file as an attachment to the work item.

        Args:
            content: the name of the file to attach.

        Returns:
            None
        """

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
                # update the list of attachments being displayed in the table
                # avoid fetching the list from the API to avoid making a request; simple append the new attachment
                current_attachments = self.attachments.attachments if self.attachments else []
                new_attachments = [response.result] if response.result else []
                self.attachments = WorkItemAttachments(
                    work_item_key=self.issue_key,
                    attachments=current_attachments + new_attachments,
                )

    def watch_attachments(self, data: WorkItemAttachments | None) -> None:
        """Updates the table that displays the attached files with new attachments."""

        self.remove_children()
        self.issue_key = data.work_item_key if data else None
        if data and data.attachments:
            table = AttachmentsDataTable(self.issue_key)
            table.add_columns(*['File Name', 'Size (KB)', 'Added', 'Author', 'Type'])
            item: Attachment
            for item in data.attachments:
                table.add_row(
                    *[
                        item.filename,
                        item.get_size() or '-',
                        item.created_date,
                        item.display_author,
                        item.get_mime_type(),
                    ],
                    key=item.id,
                )
            self.mount(table)


class ViewAttachmentScreen(ModalScreen):
    """A modal screen to display files attached to a work item."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Image')]
    TITLE = 'Image'
    HELP = None

    def __init__(self, attachment_id: str, attachment_file_type: str, attachment_file_name: str):
        super().__init__()
        self._attachment_id = attachment_id
        self._attachment_file_type = attachment_file_type
        self._attachment_file_name = attachment_file_name

    @property
    def center_widget(self) -> Center:
        return self.query_one(Center)

    @property
    def vertical_widget(self) -> VerticalScroll:
        return self.query_one(VerticalScroll)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            with Center():
                yield LoadingIndicator()

    async def _download_attachment(self, attachment_id: str) -> None:
        app = cast('JiraApp', self.screen.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await app.api.get_attachment_content(attachment_id)
        container = self.center_widget
        await container.remove_children(LoadingIndicator)
        if response.success and response.result:
            self.vertical_widget.border_title = self._attachment_file_name or ''
            try:
                widget = FileAttachmentWidget.build_widget(
                    self._attachment_file_type, response.result
                )
            except Exception:
                await container.mount(Static('Unable to display the file'))
            else:
                if widget:
                    await container.mount(widget)
                else:
                    await container.mount(Static('Unsupported file type'))
        else:
            await container.mount(Static('Unable to download the attached file'))
            self.notify(
                f'Unable to download the attached file: {response.error}',
                severity='error',
                title='Download Attachment',
            )

    async def on_mount(self):
        self.run_worker(self._download_attachment(self._attachment_id))


class FileAttachmentWidget:
    """A factory to build Widgets to view different types of files attached to a work item."""

    @staticmethod
    def build_widget(file_type: str, content: bytes) -> Widget | None:
        """Builds a `textual.widget.Widget` for visualizing a specific type of file/content.

        Args:
            file_type: the file's MIME type.
            content: the bytes representation of the file's content to display.

        Returns:
            A `textual.widget.Widget` to display the contents or `None` if the file's content is not supported.
        """
        try:
            mime = SupportedAttachmentVisualizationMimeTypes(file_type)
        except ValueError:
            return None
        if mime == SupportedAttachmentVisualizationMimeTypes.APPLICATION_JSON:
            return TextArea.code_editor(
                json.dumps(json.loads(content), indent=3),
                language='json',
                read_only=True,
                show_line_numbers=False,
            )
        if mime == SupportedAttachmentVisualizationMimeTypes.APPLICATION_XML:
            return TextArea.code_editor(
                str(content.decode()), language='xml', read_only=True, show_line_numbers=False
            )
        if (
            mime == SupportedAttachmentVisualizationMimeTypes.TEXT_CSV
            or mime == SupportedAttachmentVisualizationMimeTypes.TEXT_PLAIN
        ):
            return TextArea.code_editor(
                str(content.decode()), read_only=True, show_line_numbers=False
            )
        if mime == SupportedAttachmentVisualizationMimeTypes.TEXT_MARKDOWN:
            return Markdown(str(content.decode()))

        if is_image(file_type) and _image_support_is_enabled():
            from PIL import UnidentifiedImageError
            from textual_image.widget import Image

            try:
                return Image(BytesIO(content))
            except UnidentifiedImageError:
                return None
        return None


def _image_support_is_enabled() -> bool:
    return CONFIGURATION.get().enable_images_support
