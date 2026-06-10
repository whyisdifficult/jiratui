"""This module contains the screen used for creating new work items."""

import os
import shlex
import subprocess
import tempfile
from typing import Any, cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ItemGrid, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Input,
    Rule,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import IssueType, JiraIssue, Project
from jiratui.widgets.commons import CustomFieldType
from jiratui.widgets.commons.adf import ADFMarkdownTextAreaWidget
from jiratui.widgets.commons.base import (
    FieldMode,
    LabelsAutoComplete,
    MultiUserPickerAutoComplete,
    WorkItemKeyAutoComplete,
)
from jiratui.widgets.commons.users import JiraUserInput, UsersAutoComplete
from jiratui.widgets.commons.widgets import (
    LabelsWidget,
    MultiSelectWidget,
    MultiUserPickerWidget,
    PlainTextTextAreaWidget,
    SingleUserPickerWidget,
)
from jiratui.widgets.create_work_item.factory import create_widgets_for_work_item_creation
from jiratui.widgets.create_work_item.fields import (
    ParentKeyField,
    SummaryField,
    WorkItemProjectSelectionField,
    WorkItemTypeSelectionField,
)


class TextAreaTabPane(TabPane):
    """A custom TabPane that contains either ADFMarkdownTextAreaWidget or PlainTextTextAreaWidget as its child."""

    def __init__(
        self, title: str, widget: ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget, **kwargs
    ):
        super().__init__(title, widget, id=f'pane-{widget.jira_field_key}', **kwargs)
        self.__widget = widget
        self.add_class('create-work-item-textarea-field-pane')

    @property
    def widget(self) -> ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget:
        return self.__widget


class TextAreaTabbedContent(TabbedContent):
    """Custom TabbedContent with a key binding for editing content."""

    BINDINGS = [
        Binding('ctrl+e', 'edit_content', 'Edit', show=True, key_display='^e'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__configuration = CONFIGURATION.get()

    def _get_textarea_widget(self) -> ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget | None:
        if (active_pane := self.active_pane) is None:
            return None
        try:
            return active_pane.query_one(ADFMarkdownTextAreaWidget)
        except NoMatches:
            try:
                return active_pane.query_one(PlainTextTextAreaWidget)
            except NoMatches:
                return None

    def _edit_text_content(self, content: str) -> None:
        if not self.__configuration.text_editor:
            self.notify(
                severity='error',
                message='Rich text editor is not enabled. Check config.text_editor',
            )
        else:
            new_content = self._open_as_temporary_file(self.__configuration.text_editor, content)
            # update the content of the textarea widget
            widget: ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget | None = (
                self._get_textarea_widget()
            )
            if widget is not None:
                widget.text = new_content.strip() if new_content else ''

    @on(ADFMarkdownTextAreaWidget.EditContent)
    def edit_adf_content(self, event: ADFMarkdownTextAreaWidget.EditContent) -> None:
        self._edit_text_content(event.content)

    @on(PlainTextTextAreaWidget.EditContent)
    def edit_plain_text_content(self, event: PlainTextTextAreaWidget.EditContent) -> None:
        self._edit_text_content(event.content)

    def action_edit_content(self) -> None:
        """Handle '^e' key press in this widget."""
        widget: ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget | None = (
            self._get_textarea_widget()
        )
        if widget is not None:
            self.notify(f'Trying to update content of the textarea widget: {widget.id}')
            self._edit_text_content(widget.text)

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


class AddWorkItemScreen(Screen[dict[str, Any]]):
    """A modal screen for creating work items.

    The screen is pushed from the main screen of the application. It is responsible for:

    - Displaying a form to allow the user to fill in the basic details to create the work item.
    - Building the required Widgets for the form based on the metadata associated to the project and type of work item
    being created.

    The screen uses the API to:
    - Retrieve the list of projects
    - Retrieve the list of work items types associated to the selected project
    - Retrieve the necessary metadata for creating the work item in within the project.
    - Verify that the reporter provided to the screen does actually exist.

    The screen can be initialized with:
    - A project key
    - The account ID of the reporter
    - An optional key that identifies the parent item of the work item being created. This is useful when the screen
    is open from the Widget that shows the list of subtasks associated to an item.

    ```{important}
    This screen does not actually create the work item. Instead, upon dismissing the screen the caller will receive the
    necessary data to create the work item via the Jira API.
    ```

    **See Also**:
    - [Create Work Item Screen Design](#components-create-work-item-screen)
    - [Use Case: Create Work Item](#use-case-create-work-item)
    - [Architecture](#architecture-create-work-item-classes)
    """

    BINDINGS = [
        Binding('ctrl+s', 'save_work_item', 'Save', show=True, key_display='^s'),
        Binding('escape', 'app.pop_screen', 'Close'),
    ]

    TITLE = 'New Work Item'
    HELP = 'See Creating Work Items section in the help'

    def __init__(
        self,
        project_key: str | None = None,
        reporter_account_id: str | None = None,
        parent_work_item_key: str | None = None,
    ):
        """Initializes the screen.

        Args:
            project_key: the key of the project for which the work item will be created. If not defined the user will
            need to choose it from a dropdown list.
            reporter_account_id: the account id of the user that acts as a reporter. This is injected from the main
            screen which in turn can be picked up from the cli or the configuration file. If not defined the user will
            need to choose it from a dropdown list.
            parent_work_item_key: the key of the parent work item to which this work item belongs. If not defined the
            user will be able to set one.
        """

        super().__init__()
        self._project_key = project_key
        self._reporter_account_id = reporter_account_id
        self._parent_work_item_key = parent_work_item_key
        # groups field metadata by field id
        self._field_metadata: dict[str, dict] = {}
        # this is used for determining whether the reporter field should be requested to the user and updated
        self._reporter_is_editable: bool = True  # default to editable
        self.__configuration = CONFIGURATION.get()

    @property
    def help_anchor(self) -> str:
        return '#creating-work-items'

    @property
    def adf_support_enabled(self) -> bool:
        # determines if the application is connecting to a Jira API instance that supports ADF
        return self.__configuration.cloud and self.__configuration.jira_api_version == 3

    @property
    def reporter_account_id(self) -> str | None:
        return self._reporter_account_id

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-work-item-button-save', expect_type=Button)

    @property
    def project_selector(self) -> WorkItemProjectSelectionField:
        return self.query_one(WorkItemProjectSelectionField)

    @property
    def issue_type_selector(self) -> WorkItemTypeSelectionField:
        return self.query_one(WorkItemTypeSelectionField)

    @property
    def reporter_selector(self) -> JiraUserInput:
        return self.query_one('#create-work-item-reporter-selector', expect_type=JiraUserInput)

    @property
    def reporter_autocomplete(self) -> UsersAutoComplete:
        return self.query_one('#reporter-autocomplete', expect_type=UsersAutoComplete)

    @property
    def assignee_selector(self) -> JiraUserInput:
        return self.query_one('#create-work-item-assignee-selector', expect_type=JiraUserInput)

    @property
    def assignee_autocomplete(self) -> UsersAutoComplete:
        return self.query_one('#assignee-autocomplete', expect_type=UsersAutoComplete)

    @property
    def summary_field(self) -> SummaryField:
        return self.query_one(SummaryField)

    @property
    def description_field(self) -> ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget:
        if self.adf_support_enabled:
            return self.query_one('#description', expect_type=ADFMarkdownTextAreaWidget)
        return self.query_one('#description', expect_type=PlainTextTextAreaWidget)

    @property
    def parent_key_field(self) -> ParentKeyField:
        return self.query_one(ParentKeyField)

    @property
    def additional_fields(self) -> VerticalScroll:
        return self.query_one('#create-additional-fields', expect_type=VerticalScroll)

    @property
    def textarea_fields_tabbed_content(self) -> TextAreaTabbedContent:
        return self.query_one('#textarea-fields-tabs', expect_type=TextAreaTabbedContent)

    def _validate_required_fields(self) -> bool:
        """Checks if all required fields for saving the form data have values.

        Returns:
            True if all required fields are filled, False otherwise.
        """

        # build list of required field checks
        required_checks = [
            self.project_selector.selection,
            self.issue_type_selector.selection,
            self.summary_field.value,
        ]

        # only check reporter if it's editable
        if self._reporter_is_editable:
            required_checks.append(self.reporter_selector.account_id)

        basic_fields_valid = all(required_checks)

        # check if description is required and has a value
        if self.description_field.required and self.description_field.value_is_empty:
            return False

        return basic_fields_valid

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.TITLE
        with vertical:
            yield Static(
                Text('Important: fields marked with (*) are required.', style='orange italic')
            )
            yield Rule()
            with Horizontal():
                # left-hand side panel
                with VerticalScroll(classes='add-work-item-form'):
                    # statically-defined widgets
                    with ItemGrid(classes='add-work-item-fields-grid'):
                        # set widgets in row 1
                        yield WorkItemProjectSelectionField()
                        yield WorkItemTypeSelectionField([])
                        # set widgets in row 2
                        # this input field contains the account id of the Jira user that we can use to set the item's
                        # reporter field
                        yield JiraUserInput(
                            id='create-work-item-reporter-selector',
                            border_title='Reporter',
                            border_subtitle='(*)',
                            jira_field_key='reporter_account_id',
                        ).add_class(*['required', 'create-update-users-field-widget'])
                        # this input field contains the account id of the Jira user that we can use to set the item's
                        # assignee field
                        yield JiraUserInput(
                            id='create-work-item-assignee-selector',
                            border_title='Assignee',
                            jira_field_key='assignee_account_id',
                        ).add_class(*['create-update-users-field-widget'])
                        yield SummaryField()
                        yield ParentKeyField(self._parent_work_item_key)
                    # dynamically-created widgets
                    with VerticalScroll(classes='add-work-item-form-textarea-fields'):
                        with TextAreaTabbedContent(
                            id='textarea-fields-tabs'
                        ):  # Container for dynamic fields - textarea fields
                            widget: ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget
                            if self.adf_support_enabled:
                                widget = ADFMarkdownTextAreaWidget(
                                    mode=FieldMode.CREATE,
                                    jira_field_key='description',
                                    field_id='description',
                                    title='Description',
                                )
                            else:
                                widget = PlainTextTextAreaWidget(
                                    mode=FieldMode.CREATE,
                                    jira_field_key='description',
                                    field_id='description',
                                    title='Description',
                                )
                            yield TextAreaTabPane('Description', widget)
                # right-hand side panel
                with Vertical():
                    yield VerticalScroll(
                        id='create-additional-fields'
                    )  # Container for dynamic fields - non-textarea fields
                    with ItemGrid(classes='add-work-item-grid-buttons'):
                        yield Button(
                            'Save', variant='success', id='add-work-item-button-save', disabled=True
                        )
                        yield Button('Cancel', variant='error', id='add-work-item-button-quit')
        yield Footer(compact=True, show_command_palette=False)

    def on_mount(self):
        """Mounts the widgets.

        This fetches the required data to populate the widgets.

        1. It fetches the available projects.
        2. It fetches the available types of issues that can be created.
        3. If the reporter account id is set and the reporter field is editable then this will also fetch the details of
        the user identified by the reporter account and will set the reporter dropdown if the user exists.
        4. It mounts the autocomplete widgets required for selecting reporter, assignee and parent key.
        """

        self.run_worker(self.fetch_available_projects())
        self.run_worker(self.fetch_available_issue_types())
        if self.reporter_account_id and self._reporter_is_editable:
            self.run_worker(self._fetch_reporter())
        reporter_autocomplete = UsersAutoComplete(
            self.reporter_selector,
            self.app.api,  # type:ignore[attr-defined]
            id='reporter-autocomplete',
        )
        assignee_autocomplete = UsersAutoComplete(
            self.assignee_selector,
            self.app.api,  # type:ignore[attr-defined]
            id='assignee-autocomplete',
            user_search_function=self._search_and_filter_assignees,
        )
        work_item_parent_key_autocomplete = WorkItemKeyAutoComplete(
            self.parent_key_field,
            self.app.api,  # type:ignore[attr-defined]
            work_items_search_function=self._search_work_items,
        )
        self.mount_all(
            [reporter_autocomplete, assignee_autocomplete, work_item_parent_key_autocomplete]
        )

    def _use_advanced_full_text_search(self) -> bool:
        return self.__configuration.enable_advanced_full_text_search

    async def _search_work_items(self, query: str) -> list[JiraIssue] | None:
        """Search and retrieve work items to fill in the autocomplete suggestions for parent key.

        See Also: https://support.atlassian.com/jira-software-cloud/docs/jql-fields/

        Args:
            query: the search term to find work items.

        Returns:
            A list of `JiraIssue` instances of None if it fails to search work items.
        """

        if query:
            jql_query = f'summary ~ "{query}" OR description ~ "{query}" OR workItemKey ~ "{query}"'
            if self._use_advanced_full_text_search():
                jql_query = f'text ~ "{query}" OR workItemKey ~ "{query}"'
            if self.project_selector.selection:
                jql_query = f'({jql_query}) AND (spaceJira = "{self.project_selector.selection}")'
            response: APIControllerResponse = await self.app.api.search_issues(  # type:ignore[attr-defined]
                jql_query=jql_query, fields=['id', 'key', 'summary']
            )
            if response.success and response.result:
                return response.result.issues
        return None

    async def _search_and_filter_assignees(self, query: str) -> APIControllerResponse:
        # searches and filters users that can be assignees of the work item being created.
        return await self.app.api.search_users_assignable_to_issue(  # type:ignore[attr-defined]
            project_id_or_key=self.project_selector.selection, query=query
        )

    async def _fetch_reporter(self):
        """Checks if the user identified by self.reporter_account_id exist and if it does, it sets the reporter
        dropdown widget."""

        response: APIControllerResponse = await self.app.api.get_user(self.reporter_account_id)
        if response.success and (user_details := response.result):
            self.reporter_selector.set_value(self.reporter_account_id, user_details.display_name)

    async def fetch_available_projects(self) -> None:
        """Fetches the available projects and updates the project dropdown widget."""

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.search_projects()
        projects: list[Project] = []
        if response.success:
            projects = response.result or []
        projects.sort(key=lambda x: x.name)
        self.project_selector.projects = {'projects': projects, 'selection': self._project_key}

    async def fetch_available_issue_types(self, project_key: str | None = None) -> None:
        """Fetches the applicable types of work items for the selected project and updates the issue type dropdown
        widget.

        This also removes all the dynamically-created textarea-based widgets. This does not remove the pane that
        contains the description widget.

        Args:
            project_key: the key of the project selected by the user.

        Returns:
            None
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        key = project_key or self.project_selector.selection
        # clean up the panes that contain dynamically-created textarea-based widgets
        await self._remove_textarea_panes()
        # clean up the list of options
        self.issue_type_selector.set_options([])
        if key:
            response: APIControllerResponse = await application.api.get_issue_types_for_project(key)
            types: list[IssueType] = []
            if response.success:
                types = response.result or []
            types.sort(key=lambda x: x.name)
            options = [(t.name, t.id) for t in types]
            self.issue_type_selector.set_options(options)

    @on(Select.Changed, 'WorkItemProjectSelectionField')
    def handle_project_selection(self) -> None:
        """Fetches the applicable types of work items for creating issues in the selected project.

        This also:
        - updates the status of the "Save" button.
        - remove all the panes used for displaying textarea-based field widgets.

        Returns:
            None.
        """

        self.run_worker(self.fetch_available_issue_types(self.project_selector.selection))
        # clean up the panes that contain textarea-based widgets
        self.additional_fields.remove_children()
        self.save_button.disabled = not self._validate_required_fields()

    @on(Select.Changed, 'WorkItemTypeSelectionField')
    def handle_issue_type_selection(self) -> None:
        """Fetches metadata for creating issues in the selected project and of the selected type.

        This also updates the status of the "Save" button.

        Returns:
            None.
        """

        if self.project_selector.selection and self.issue_type_selector.selection:
            self.run_worker(
                self.fetch_issue_create_metadata(
                    self.project_selector.selection, self.issue_type_selector.selection
                ),
            )
        self.save_button.disabled = not self._validate_required_fields()

    @on(Select.Changed, '#create-work-item-reporter-selector')
    def handle_reporter_selection(self) -> None:
        """Updates the status of the "Save" button after the user selects a Reporter."""

        self.save_button.disabled = not self._validate_required_fields()

    @on(Input.Blurred, 'SummaryField')
    def handle_summary_value_change(self) -> None:
        """Updates the status of the "Save" button after the user updates the summary field."""

        self.save_button.disabled = not self._validate_required_fields()

    @on(TextArea.Changed, 'DescriptionWidget')
    def handle_description_value_change(self) -> None:
        """Updates the status of the "Save" button after the user updates the description field."""

        self.save_button.disabled = not self._validate_required_fields()

    async def fetch_issue_create_metadata(self, project_key: str, issue_type_id: str) -> None:
        """Fetches the metadata for creating work items of a given type in the given project.

        This function does a few things:
        - Retrieves the metadata for creating work items of a given type in the given project.
        - Builds and mounts the necessary widgets that compose the create-work-item form.

        Args:
            project_key: the key of the project for which we want to create a work item.
            issue_type_id: the type of work item we want to create.

        Returns:
            None
        """

        await self.additional_fields.remove_children()
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_issue_create_metadata(
            project_key, issue_type_id
        )
        if not response.success or not response.result:
            self.notify('Unable to find the required information for creating work items.')
        else:
            # store fields metadata for proper value formatting later
            fields_data: list[dict] = response.result.get('fields', [])

            for field in fields_data:
                if field_id := field.get('fieldId'):
                    self._field_metadata[field_id] = field

                # check if description is required and update the widget
                if field_id == 'description' and field.get('required', False):
                    self.description_field.mark_required()

                # check if reporter field is editable
                if field_id == 'reporter':
                    operations = field.get('operations', [])
                    self._reporter_is_editable = 'set' in operations
                    # hide reporter field if not editable
                    self.reporter_selector.display = self._reporter_is_editable

            # create all the widgets for the additional fields supported
            metadata_fields: list[Widget] = create_widgets_for_work_item_creation(
                data=fields_data,
                api_controller=application.api,
                adf_support_enabled=self.adf_support_enabled,
            )

            # split the fields based on type so we can mount them in different places in the UI
            textarea_widgets: list[ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget] = []
            non_textarea_widgets: list[Widget] = []
            for widget in metadata_fields:
                if isinstance(widget, ADFMarkdownTextAreaWidget) or isinstance(
                    widget, PlainTextTextAreaWidget
                ):
                    textarea_widgets.append(widget)
                else:
                    non_textarea_widgets.append(widget)

            # mount the (non-textarea) widgets on the left column
            await self.additional_fields.mount_all(non_textarea_widgets)
            # mount the widgets on the right column but before make sure we remove all the panes except the
            # statically-defined pane that contains the description widget
            await self._remove_textarea_panes()
            for textarea_widget in textarea_widgets:
                await self.textarea_fields_tabbed_content.add_pane(
                    TextAreaTabPane(textarea_widget.border_title, textarea_widget)
                )

            # create and mount AutoComplete widgets for labels inputs and custom fields that support multiple users
            for input_widget in self.additional_fields.query(Input):
                if isinstance(input_widget, LabelsWidget):
                    # set up the autocomplete widget for the field that allows users to select labels
                    field_meta = self._field_metadata.get('labels', {})
                    required = field_meta.get('required', False)
                    title = field_meta.get('name', 'Labels')
                    await self.additional_fields.mount(
                        LabelsAutoComplete(
                            target=input_widget,
                            api_controller=application.api,
                            required=required,
                            title=title,
                        )
                    )
                elif isinstance(input_widget, MultiUserPickerWidget):
                    await self.additional_fields.mount(
                        MultiUserPickerAutoComplete(
                            target=input_widget, api_controller=application.api
                        )
                    )
                elif isinstance(input_widget, SingleUserPickerWidget):
                    await self.additional_fields.mount(
                        UsersAutoComplete(target=input_widget, api_controller=application.api)
                    )

    async def _remove_textarea_panes(self) -> None:
        """Removes the panes that contain dynamically-created textarea-based widgets.

        Important: this does not remove the description's widget because we always need at least 1 pane in the tabbed
        content widget.

        Returns:
            None.
        """

        if panes := self.textarea_fields_tabbed_content.query(TextAreaTabPane):
            for pane in panes:
                if pane.id != 'pane-description':
                    await self.textarea_fields_tabbed_content.remove_pane(pane.id)

    @staticmethod
    def _format_field_value(field_id: str, value: Any, field_metadata: dict) -> Any:
        """Formats a field's value based on the field's metadata.

        This consolidated logic handles different field types like user pickers, floats,
        labels, and select fields. Extracted from inline logic for reusability.

        Args:
            field_id: the Jira field ID.
            value: the raw value from the form widget.
            field_metadata: the field's metadata from Jira's create metadata API.

        Returns:
            The formatted value ready for API submission, or None to skip the field.
        """

        if not value:
            return None

        schema = field_metadata.get('schema', {})
        custom_type = schema.get('custom')

        if custom_type == CustomFieldType.USER_PICKER.value:
            return {'accountId': value}

        elif custom_type == CustomFieldType.FLOAT.value or schema.get('type') == 'number':
            if value:  # Type-safe check to prevent ~AlwaysFalsy error
                try:
                    return float(value)
                except (ValueError, TypeError):
                    # invalid float - skip this field
                    return None
            return None

        # labels field (array of strings)
        elif field_id == 'labels' or (
            schema.get('type') == 'array' and schema.get('items') == 'strings'
        ):
            if isinstance(value, str):
                # split by comma and strip whitespace from each label
                return [label.strip() for label in value.split(',') if label.strip()]
            elif isinstance(value, list):
                return value
            else:
                return []

        # select-type fields (fields with allowedValues in the metadata)
        elif field_metadata.get('allowedValues'):
            # array type fields (like multi-select) need array of objects
            if schema.get('type') == 'array':
                if isinstance(value, list):
                    return [{'id': v} for v in value]
                else:
                    return [{'id': value}]
            else:
                # single-select: convert to object with 'id' key
                return {'id': value}

        # default: pass value as-is
        return value

    def action_save_work_item(self) -> None:
        self.handle_save()

    @on(Button.Pressed, '#add-work-item-button-save')
    def handle_save(self) -> None:
        """Builds the necessary payload data for creating a new work item.

        This **does not** actually create the work item. Instead, it passes the payload data to the main screen upon
        dismissal. The main screen is then responsible for requesting the API to create a new work item with the given
        payload.

        Returns:
            None
        """

        if not self._validate_required_fields():
            self.notify('Fields marked with (*) must be provided.', title='Create Work Item')
        else:
            # process widgets that are created statically
            data: dict[str, Any] = {
                self.project_selector.jira_field_key: self.project_selector.selection,
                self.parent_key_field.jira_field_key: self.parent_key_field.value,
                self.issue_type_selector.jira_field_key: self.issue_type_selector.selection,
                self.assignee_selector.jira_field_key: self.assignee_selector.account_id,
                self.summary_field.jira_field_key: self.summary_field.value,
            }

            if self.description_field.value_is_empty:
                data[self.description_field.jira_field_key] = None
            else:
                data[self.description_field.jira_field_key] = (
                    self.description_field.get_value_for_create()
                )

            # only include reporter if it's editable
            if self._reporter_is_editable:
                data[self.reporter_selector.jira_field_key] = self.reporter_selector.account_id

            # process non-textarea widgets that are created dynamically
            for widget in self.additional_fields.children:
                if not hasattr(widget, 'field_id'):
                    continue

                if not (field_id := widget.field_id):
                    continue

                value: Any = None
                if isinstance(widget, MultiSelectWidget):
                    if value := widget.get_value_for_create():
                        data[widget.jira_field_key] = value
                    continue
                elif isinstance(widget, MultiUserPickerWidget):
                    if value := widget.get_value_for_create():
                        data[widget.jira_field_key] = value
                    continue
                elif isinstance(widget, SingleUserPickerWidget):
                    if value := widget.get_value_for_create():
                        data[widget.jira_field_key] = value
                    continue
                elif isinstance(widget, LabelsWidget):
                    if value := widget.get_value_for_create():
                        data[widget.jira_field_key] = value
                    continue
                elif isinstance(widget, Select):
                    value = widget.selection
                elif isinstance(widget, Input):
                    value = widget.value

                # priority and duedate are base fields that don't need formatting
                if field_id in ('priority', 'duedate'):
                    data[field_id] = value
                    continue

                # format the value based on field metadata using consolidated logic
                if value and field_id in self._field_metadata:
                    field_meta = self._field_metadata[field_id]
                    if (
                        formatted_value := self._format_field_value(field_id, value, field_meta)
                    ) is not None:
                        data[field_id] = formatted_value
                elif value:
                    # no metadata available, pass as-is
                    data[field_id] = value

            # process textarea widgets that are created dynamically
            # iterate over every TextAreaTabPane created dynamically to extract the value of its widget
            if tab_panes := self.textarea_fields_tabbed_content.query(TextAreaTabPane):
                pane: TextAreaTabPane
                for pane in tab_panes:
                    pane_inner_widget: (
                        ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget | None
                    ) = pane.widget
                    if pane_inner_widget and (value := pane_inner_widget.get_value_for_create()):
                        data[pane_inner_widget.jira_field_key] = value

            self.dismiss(data)

    @on(Button.Pressed, '#add-work-item-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})
