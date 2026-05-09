import os
import shlex
import subprocess
import tempfile
from typing import Any, cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, ItemGrid, Vertical, VerticalGroup, VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Collapsible,
    LoadingIndicator,
    MarkdownViewer,
    Rule,
    Static,
    TextArea,
)

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue, JiraWorkItemFields
from jiratui.widgets.commons import CustomFieldType
from jiratui.widgets.commons.adf import ADFTextAreaWidget
from jiratui.widgets.commons.factory_utils import (
    FieldMetadata,
    build_read_only_rich_text_widget,
)
from jiratui.widgets.commons.widgets import TextAreaWidget


class TextareaCollapsible(Collapsible):
    BINDINGS = [
        Binding(
            key='e',
            action='edit_content',
            description='Edit',
            key_display='e',
        ),
        Binding(
            key='v',
            action='view_content',
            description='View',
            key_display='v',
        ),
    ]

    class DisplayContent(Message):
        def __init__(self, content: str, title: str | None = None):
            super().__init__()
            self.content = content
            self.title = title

    class EditContent(Message):
        def __init__(
            self, jira_field_key: str, content: str | None = None, title: str | None = None
        ):
            super().__init__()
            self.content = content or ''
            self.jira_field_key = jira_field_key
            self.title = title

    def __init__(
        self,
        jira_field_key: str,
        field_name: str,
        widget: ADFTextAreaWidget | TextAreaWidget | Static,
        required: bool = False,
        **kwargs,
    ):
        self.__configuration = CONFIGURATION.get()
        self._jira_field_key: str = jira_field_key

        self.__widget: ADFTextAreaWidget | TextAreaWidget | Static = widget

        # the string representation of the content stored in the widget within this collapsible.
        # this will contain '' when the content is empty but the Collapsible contains a Static widget
        if isinstance(self.__widget, Static):
            self.__content: str = ''
        else:
            self.__content = self.__widget.text_content or ''

        # initialize the Collapsible widget
        super().__init__(self.__widget, **kwargs)
        self.border_title = field_name
        self.title = ''  # let's not set a text next to the arrows for toggling content
        self.add_class('textarea-collapsible')
        if required:
            self.border_subtitle = '(*)'
            self.add_class('required')

    @property
    def widget(self) -> ADFTextAreaWidget | TextAreaWidget | Static:
        return self.__widget

    @property
    def text_content(self) -> str:
        return self.__content

    @property
    def _updating_rich_text_is_enabled(self) -> bool:
        # for easy mocking in tests
        return self.__configuration.enable_updating_rich_text

    def action_view_content(self):
        if self.__content:
            self.post_message(self.DisplayContent(self.__content, self.border_title))
        else:
            self.notify('The field has no content to display. Press "e" to edit it.')

    def action_edit_content(self):
        if self._updating_rich_text_is_enabled:
            self.post_message(
                self.EditContent(self._jira_field_key, self.__content, self.border_title)
            )


class DisplayTextContentScreen(ModalScreen):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]

    def __init__(self, content: str, title: str | None = None):
        super().__init__()
        self.__content = content
        self.title = title

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self.__content)


class EditTextContentScreen(Screen[dict]):
    """A modal screen that displays a TextArea editor to allow users to edit Plain Text/Markdown content."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]

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
                self.__content, language='markdown', show_line_numbers=False, compact=True
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


class WorkItemInfoContainer(Vertical):
    """The container for all the widgets that store/show information (description and other text-based fields) of a
    work item."""

    HELP = 'See Work Item Info section in the help'
    issue: Reactive[JiraIssue | None] = reactive(None, always_update=True)
    """The issue whose information we want to display."""
    clear_information: Reactive[bool] = reactive(False, always_update=True)
    """Reactive variable to clear the summary, description and extra fields."""

    class WorkItemUpdated(Message):
        def __init__(self, work_item_key: str):
            super().__init__()
            self.work_item_key = work_item_key

    def __init__(self):
        super().__init__(id='work_item_info_container')
        self._has_extra_custom_fields = False
        self.can_focus = True
        self.__configuration = CONFIGURATION.get()

    @on(TextareaCollapsible.DisplayContent)
    def _display_content(self, event: TextareaCollapsible.DisplayContent) -> None:
        self.app.push_screen(DisplayTextContentScreen(event.content, event.title))
        event.stop()

    @property
    def _updating_rich_text_is_enabled(self) -> bool:
        return self.__configuration.enable_updating_rich_text

    @property
    def _enable_updating_additional_fields(self) -> bool:
        return self.__configuration.enable_updating_additional_fields

    @property
    def _update_additional_fields_ignore_ids(self) -> list[str]:
        return self.__configuration.update_additional_fields_ignore_ids or []

    @property
    def _editor(self) -> str | None:
        return self.__configuration.text_editor

    @on(TextareaCollapsible.EditContent)
    def _edit_content(self, event: TextareaCollapsible.EditContent) -> None:
        if self._updating_rich_text_is_enabled:
            if self._editor:
                new_content = self._open_as_temporary_file(self._editor, event.content)
                self.run_worker(
                    self._update_field(
                        {'jira_field_key': event.jira_field_key, 'content': new_content}
                    )
                )
            else:
                self.app.push_screen(
                    EditTextContentScreen(event.content, event.jira_field_key, event.title),
                    self._update_field,
                )
        event.stop()

    async def _update_field(self, data: dict) -> None:
        """Updates the value of a text-based field in the work item."""
        if self._updating_rich_text_is_enabled:
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            payload = {data.get('jira_field_key'): data.get('content')}
            response: APIControllerResponse = await application.api.update_issue(
                self.issue, payload
            )
            if not response.success:
                self.notify(f'Unable to update the work item: {response.error}', severity='error')
            else:
                self.post_message(self.WorkItemUpdated(self.issue.key))
                self.notify('Work item updated successfully')
        else:
            self.notify(
                'Updating this field is not enabled. Check config.enable_updating_rich_text',
                severity='warning',
            )

    @property
    def help_anchor(self) -> str:
        return '#work-item-info'

    @property
    def issue_summary_widget(self) -> Static:
        return self.query_one('#issue_summary', expect_type=Static)

    @property
    def loading_container(self) -> Center:
        return self.query_one('#work-item-info-loading-container', expect_type=Center)

    @property
    def content_container(self) -> VerticalGroup:
        return self.query_one('#work-item-info-content', expect_type=VerticalGroup)

    @property
    def collapsible_container(self) -> VerticalScroll:
        return self.query_one('#collapsible-container', expect_type=VerticalScroll)

    def compose(self) -> ComposeResult:
        with Center(id='work-item-info-loading-container') as loading_container:
            loading_container.display = False
            yield LoadingIndicator()
        with VerticalGroup(id='work-item-info-content') as vg:
            vg.can_focus = False
            yield Static(id='issue_summary', markup=False)
            yield Rule()
            yield VerticalScroll(id='collapsible-container', classes='work-item-info-collapsible')

    async def _setup_work_item_description(self, work_item: JiraIssue) -> None:
        if issue_edit_metadata := work_item.get_edit_metadata():
            if field_metadata := issue_edit_metadata.get(JiraWorkItemFields.DESCRIPTION.value, {}):
                field_name = field_metadata.get('name', field_metadata.get('key')).title()
                widget_for_collapsible: ADFTextAreaWidget | TextAreaWidget | Static
                if work_item.rich_text_value_is_empty(work_item.description):  # type:ignore[arg-type]
                    widget_for_collapsible = Static(
                        f'There is no "{field_name}" set. Press "e" to edit it.', classes='tip'
                    )
                else:
                    widget_for_collapsible = build_read_only_rich_text_widget(
                        jira_field_key=field_metadata.get('key'),
                        field_name=field_name,
                        required=field_metadata.get('required', False),
                        content=work_item.description,
                    )
                collapsible = TextareaCollapsible(
                    jira_field_key=field_metadata.get('key'),
                    widget=widget_for_collapsible,
                    field_name=field_name,
                    required=field_metadata.get('required', False),
                    collapsed=False,
                )
                await self.collapsible_container.mount(collapsible)

    def watch_issue(self, work_item: JiraIssue | None) -> None:
        # "reset" the information of any previous widget
        self.clear_information = True

        if not work_item:
            return None

        # set the summary of the work item and make the widget visible
        self.issue_summary_widget.update(work_item.summary)
        self.issue_summary_widget.visible = True
        self.query_one(Rule).visible = True

        # set the description of the work item and make the widget visible
        self.run_worker(self._setup_work_item_description(work_item))

        # build widgets for the fields with rich-text support
        if self._enable_updating_additional_fields:
            widgets: list[TextareaCollapsible] = self._build_textarea_widgets(work_item)
            self.collapsible_container.mount_all(widgets)
        return None

    def _build_textarea_widgets(self, work_item: JiraIssue) -> list[TextareaCollapsible]:
        widgets: list[TextareaCollapsible] = []
        if issue_edit_metadata := work_item.get_edit_metadata():
            ignored_fields = self._update_additional_fields_ignore_ids
            for field_id, field in issue_edit_metadata.items():
                if field_id in ignored_fields:
                    continue

                metadata = FieldMetadata(field)
                metadata.field_id = field_id  # override with the actual field ID; to ensure we always refer to the field's id

                if metadata.key and metadata.key.lower() == JiraWorkItemFields.DESCRIPTION.value:
                    # already added above
                    continue

                if not (schema := field.get('schema')):
                    continue

                if schema.get('custom') == CustomFieldType.TEXTAREA.value or (
                    metadata.key and metadata.key.lower() == JiraWorkItemFields.ENVIRONMENT.value
                ):
                    field_name = metadata.name or metadata.key.replace('_', ' ').title()
                    widget_for_collapsible: ADFTextAreaWidget | TextAreaWidget | Static
                    if metadata.key.lower() == JiraWorkItemFields.ENVIRONMENT.value:
                        if work_item.rich_text_value_is_empty(work_item.environment):  # type:ignore[arg-type]
                            widget_for_collapsible = Static(
                                f'There is no "{field_name}" set. Press "e" to edit it.',
                                classes='tip',
                            )
                        else:
                            widget_for_collapsible = build_read_only_rich_text_widget(
                                jira_field_key=metadata.key,
                                field_name=field_name,
                                required=metadata.required,
                                content=work_item.environment,
                            )
                    else:
                        # get the value of the field
                        field_value: Any | None = work_item.get_custom_field_value(field_id)
                        if work_item.rich_text_value_is_empty(field_value):
                            widget_for_collapsible = Static(
                                f'There is no "{field_name}" set. Press "e" to edit it.',
                                classes='tip',
                            )
                        else:
                            widget_for_collapsible = build_read_only_rich_text_widget(
                                jira_field_key=metadata.key,
                                field_name=field_name,
                                required=metadata.required,
                                content=field_value,
                            )

                    widgets.append(
                        TextareaCollapsible(
                            jira_field_key=metadata.key,
                            widget=widget_for_collapsible,
                            field_name=field_name,
                            required=metadata.required,
                            collapsed=True,
                        )
                    )
        return widgets

    def watch_clear_information(self, clear: bool = False) -> None:
        if clear:
            # reset the value of the summary and hide the widget
            self.issue_summary_widget.update('')
            self.issue_summary_widget.visible = False
            self.collapsible_container.remove_children()
            self.query_one(Rule).visible = False

    def show_loading(self) -> None:
        """Shows the loading indicator and hides content."""
        self.loading_container.display = True
        self.content_container.display = False

    def hide_loading(self) -> None:
        """Hides the loading indicator and shows content."""
        self.loading_container.display = False
        self.content_container.display = True

    def _open_as_temporary_file(self, command: str, content: str) -> str:
        editor_args: list[str] = shlex.split(command)
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp_file:
            temp_file_name = temp_file.name
            temp_file.write(content.encode('utf-8'))
            temp_file.flush()

        editor_args.append(temp_file_name)
        with self.app.suspend():
            try:
                subprocess.call(editor_args)
            except OSError:
                self.app.notify(
                    severity='error',
                    title="Can't run command",
                    message=f'The command [b]{command}[/b] failed to run.',
                )

        new_content = content
        with open(temp_file_name, 'r', encoding='utf-8') as temp_file:
            new_content = temp_file.read()

        os.remove(temp_file_name)
        return new_content
