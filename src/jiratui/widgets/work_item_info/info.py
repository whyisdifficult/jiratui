import os
import shlex
import subprocess
import tempfile
from typing import Any, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalGroup, VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import (
    LoadingIndicator,
    Rule,
    Static,
)

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.exceptions import UpdateWorkItemException, ValidationError
from jiratui.models import JiraIssue, JiraWorkItemFields
from jiratui.widgets.commons import CustomFieldType
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.factory_utils import (
    FieldMetadata,
    build_read_only_rich_text_widget,
)
from jiratui.widgets.commons.widgets import (
    EmptyTextAreaStaticWidget,
    ReadOnlyPlainTextTextAreaWidget,
)
from jiratui.widgets.work_item_info.screens import DisplayTextContentScreen, EditTextContentScreen
from jiratui.widgets.work_item_info.tabs import InfoTabbedContent, TextAreaTabPane


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

    @on(InfoTabbedContent.EditContent)
    def _edit_content(self, event: InfoTabbedContent.EditContent) -> None:
        if not self.issue:
            self.notify(
                'No work item is loaded. Select a work item and try again.',
                severity='error',
                title='Update Work Item',
            )

        if self._updating_rich_text_is_enabled:
            if self._editor:
                new_content = self._open_as_temporary_file(self._editor, event.content)
                self.run_worker(
                    self._update_field(
                        {'jira_field_key': event.jira_field_key, 'content': new_content}
                    )
                )
            else:
                # fallback to built-in rudimentary editor
                self.app.push_screen(
                    EditTextContentScreen(event.content, event.jira_field_key, event.title),
                    self._update_field,
                )
        event.stop()

    @on(InfoTabbedContent.DisplayContent)
    def _display_content(self, event: InfoTabbedContent.DisplayContent) -> None:
        self.app.push_screen(DisplayTextContentScreen(event.content, event.title))
        event.stop()

    async def _update_field(self, data: dict) -> None:
        """Updates the value of a text-based field in the work item."""

        if not data or not data.get('jira_field_key'):
            return

        if self._updating_rich_text_is_enabled:
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            payload = {data.get('jira_field_key'): data.get('content')}
            try:
                response: APIControllerResponse = await application.api.update_issue(
                    self.issue, payload
                )
            except UpdateWorkItemException as e:
                self.notify(str(e), severity='error', title='Work item update error')
            except ValidationError as e:
                self.notify(str(e), severity='error', title='Data validation error')
            except Exception as e:
                self.notify(str(e), severity='error', title='Unknown error')
            else:
                if not response.success:
                    self.notify(
                        f'Unable to update the work item: {response.error}', severity='error'
                    )
                else:
                    self._send_work_item_updated_message(self.issue.key)
                    self.notify('Work item updated successfully')
        else:
            self.notify(
                'Updating this field is not enabled. Check config.enable_updating_rich_text',
                severity='warning',
            )

    def _send_work_item_updated_message(self, work_item_key: str) -> None:
        self.post_message(self.WorkItemUpdated(work_item_key))

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
    def tabs_container(self) -> VerticalScroll:
        return self.query_one('#tabs-container', expect_type=VerticalScroll)

    @property
    def info_tabbed_content(self) -> InfoTabbedContent:
        return self.query_one('#info-tabbed-content', expect_type=InfoTabbedContent)

    def compose(self) -> ComposeResult:
        with Center(id='work-item-info-loading-container') as loading_container:
            loading_container.display = False
            yield LoadingIndicator()
        with VerticalGroup(id='work-item-info-content') as vg:
            vg.can_focus = False
            yield Static(id='issue_summary', markup=False)
            yield Rule()
            with VerticalScroll(id='tabs-container', classes='work-item-info-tabs-container'):
                yield InfoTabbedContent(
                    id='info-tabbed-content'
                )  # Container for dynamic fields - textarea fields

    def watch_issue(self, work_item: JiraIssue | None) -> None:
        self.run_worker(self._refresh_tabs_and_set_work_item(work_item))

    def _clear_static_widgets(self) -> None:
        self.issue_summary_widget.update('')
        self.issue_summary_widget.visible = False
        self.query_one(Rule).visible = False

    async def _setup_work_item_description(self, work_item: JiraIssue) -> None:
        """Sets up the TextAreaTabPane widget that holds and display the work item's description field.

        The type of widget generated and mounted inside the TextAreaTabPane depends on whether the work item's field
        has data or not and, on whether ADF is supported by the API.

        - If the field does not have data yet then this method will generate a EmptyTextAreaStaticWidget. The widget
        will simply display a hint to the user and hold the field's key so that the API can update its value.
        - If the field has data and ADF is supported by the API then this method will build a
        ReadOnlyADFMarkdownTextAreaWidget. The widget's content will be Markdown rendered from the ADF content of the
        field.
        - If the field has data and ADF is not supported by the API then this method will build a
        ReadOnlyPlainTextTextAreaWidget. The widget's content will be the text content of the field.

        Fields are processed based on the work item's edit-metadata.

        Args:
            work_item: the work item whose description field we want to display.

        Returns:
            None
        """

        if issue_edit_metadata := work_item.get_edit_metadata():
            if field_metadata := issue_edit_metadata.get(JiraWorkItemFields.DESCRIPTION.value, {}):
                field_name = field_metadata.get('name') or field_metadata.get('key', 'Description')
                field_name = field_name.title()
                widget: (
                    ReadOnlyADFMarkdownTextAreaWidget
                    | ReadOnlyPlainTextTextAreaWidget
                    | EmptyTextAreaStaticWidget
                )
                if work_item.rich_text_value_is_empty(work_item.description):  # type:ignore[arg-type]
                    widget = EmptyTextAreaStaticWidget(
                        jira_field_key=field_metadata.get('key')
                        or JiraWorkItemFields.DESCRIPTION.value,
                        id=field_metadata.get('key') or JiraWorkItemFields.DESCRIPTION.value,
                        classes='tip',
                        name=field_name,
                    )
                else:
                    widget = build_read_only_rich_text_widget(
                        jira_field_key=field_metadata.get('key')
                        or JiraWorkItemFields.DESCRIPTION.value,
                        field_name=field_name,
                        required=field_metadata.get('required', False),
                        content=work_item.description,
                    )
                pane = TextAreaTabPane(title='Description', widget_id='pane-description')
                await self.info_tabbed_content.add_pane(pane)
                await pane.mount(widget)

    async def _refresh_tabs_and_set_work_item(self, work_item: JiraIssue | None) -> None:
        """Updates the content of the Info tab, i.e. its TextAreaTabPane widgets and the summary widget.

        After the user select a work item form the search results the application needs to set up the "Info" tab. This
        tab contains a series of TextAreaTabPane, each of which holds and display the work' item's textarea-based
        fields. The info tab also shows holds a widget that displays the summary of the item.

        This method updates the content of the Info tab, i.e. its TextAreaTabPane widgets and the summary widget.

        How the widgets are set up?

        If updating additional fields for a work item is enabled then this method will build a list of widgets to
        display textarea-based content. Each widget is mounted within a TextAreaTabPane.
        The type of widget that is generated depends on whether the work item's field has data and, on whether ADF is
        supported by the API. For more details refer to self._build_textarea_widgets.

        Args:
            work_item: the instance of the work item whose text-based widgets we want to set up.

        Returns:
            None
        """

        self._clear_static_widgets()

        # re-build the InfoTabbedContent widget by removing it first
        info_tabbed_content: InfoTabbedContent | None = self.query_one_optional(
            '#info-tabbed-content', expect_type=InfoTabbedContent
        )
        if info_tabbed_content is not None:
            # remove all existing TextAreaTabPane children
            await info_tabbed_content.query(TextAreaTabPane).remove()
            # remove the tabbed content widget
            await info_tabbed_content.remove()

        # create and mount a new InfoTabbedContent
        await self.tabs_container.mount(InfoTabbedContent(id='info-tabbed-content'))

        if work_item:
            # set the summary and make the widget visible
            self.issue_summary_widget.update(work_item.summary)
            self.issue_summary_widget.visible = True
            self.query_one(Rule).visible = True

            # set the description
            await self._setup_work_item_description(work_item)

            # build widgets for the fields with rich-text support
            if self._enable_updating_additional_fields:
                widgets: list[
                    ReadOnlyADFMarkdownTextAreaWidget
                    | ReadOnlyPlainTextTextAreaWidget
                    | EmptyTextAreaStaticWidget
                ] = self._build_textarea_widgets(work_item)
                for widget in widgets:
                    if isinstance(widget, EmptyTextAreaStaticWidget):
                        pane_title = widget.name
                    else:
                        pane_title = widget.field_title

                    pane_id = f'pane-{widget.jira_field_key}'
                    pane = TextAreaTabPane(title=pane_title, widget_id=pane_id)
                    await self.info_tabbed_content.add_pane(pane)
                    await pane.mount(widget)

    def _build_textarea_widgets(
        self,
        work_item: JiraIssue,
    ) -> list[
        ReadOnlyADFMarkdownTextAreaWidget
        | ReadOnlyPlainTextTextAreaWidget
        | EmptyTextAreaStaticWidget
    ]:
        """Build a list of widgets to hold and display the value of textarea-based fields.

        The type of widget generated depends on whether the work item's field has data or not and, on whether ADF is
        supported by the API.

        - If the field does not have data yet then this method will generate a EmptyTextAreaStaticWidget. The widget
        will simply display a hint to the user and hold the field's key so that the API can update its value.
        - If the field has data and ADF is supported by the API then this method will build a
        ReadOnlyADFMarkdownTextAreaWidget. The widget's content will be Markdown rendered from the ADF content of the
        field.
        - If the field has data and ADF is not supported by the API then this method will build a
        ReadOnlyPlainTextTextAreaWidget. The widget's content will be the text content of the field.

        Fields are processed based on the work item's edit-metadata.

        Important: the work item's description field is handled separately. For details
        see: self._setup_work_item_description

        Args:
            work_item: the instance of the work item whose text-based widgets we want to set up.

        Returns:
            A list of ReadOnlyADFMarkdownTextAreaWidget, ReadOnlyPlainTextTextAreaWidget or EmptyTextAreaStaticWidget.
        """

        widgets: list[
            ReadOnlyADFMarkdownTextAreaWidget
            | ReadOnlyPlainTextTextAreaWidget
            | EmptyTextAreaStaticWidget
        ] = []
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
                    textarea_widget: (
                        ReadOnlyADFMarkdownTextAreaWidget
                        | ReadOnlyPlainTextTextAreaWidget
                        | EmptyTextAreaStaticWidget
                    )
                    if metadata.key.lower() == JiraWorkItemFields.ENVIRONMENT.value:
                        # handle the pre-defined environment field
                        if work_item.rich_text_value_is_empty(work_item.environment):  # type:ignore[arg-type]
                            textarea_widget = EmptyTextAreaStaticWidget(
                                jira_field_key=metadata.key or JiraWorkItemFields.ENVIRONMENT.value,
                                classes='tip',
                                id=metadata.key or metadata.field_id,
                                name=field_name,
                            )
                        else:
                            textarea_widget = build_read_only_rich_text_widget(
                                jira_field_key=metadata.key or JiraWorkItemFields.ENVIRONMENT.value,
                                field_name=field_name,
                                required=metadata.required,
                                content=work_item.environment,
                            )
                    else:
                        # handle any other textarea-based field
                        # get the value of the field
                        field_value: Any | None = work_item.get_custom_field_value(field_id)
                        if work_item.rich_text_value_is_empty(field_value):
                            textarea_widget = EmptyTextAreaStaticWidget(
                                jira_field_key=metadata.key,
                                classes='tip',
                                id=metadata.key or metadata.field_id,
                                name=field_name,
                            )
                        else:
                            textarea_widget = build_read_only_rich_text_widget(
                                jira_field_key=metadata.key,
                                field_name=field_name,
                                required=metadata.required,
                                content=field_value,
                            )

                    widgets.append(textarea_widget)

        return widgets

    def watch_clear_information(self, clear: bool = False) -> None:
        if clear:
            self._clear_static_widgets()
            self.run_worker(self._clear_dynamic_tabs)

    async def _clear_dynamic_tabs(self) -> None:
        info_tabbed_content: InfoTabbedContent | None = self.query_one_optional(
            '#info-tabbed-content', expect_type=InfoTabbedContent
        )
        if info_tabbed_content is not None:
            # remove all existing TextAreaTabPane children
            await info_tabbed_content.query(TextAreaTabPane).remove()
            # remove the tabbed content widget
            await info_tabbed_content.remove()

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
