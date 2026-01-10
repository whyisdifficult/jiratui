from typing import Any, cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ItemGrid, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Rule, Select, Static, TextArea

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import IssueType, Project
from jiratui.widgets.common.base_fields import FieldMode, LabelsAutoComplete, UserPickerWidget
from jiratui.widgets.common.constants import CustomFieldType
from jiratui.widgets.common.widgets import DescriptionWidget, MultiSelectWidget
from jiratui.widgets.create_work_item.factory import create_widgets_for_work_item_creation
from jiratui.widgets.create_work_item.fields import (
    CreateWorkItemAssigneeSelectionInput,
    CreateWorkItemIssueSummaryField,
    CreateWorkItemIssueTypeSelectionInput,
    CreateWorkItemParentKeyField,
    CreateWorkItemProjectSelectionInput,
    CreateWorkItemReporterSelectionInput,
)


class AddWorkItemScreen(Screen):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'New Work Item'

    def __init__(
        self,
        project_key: str | None = None,
        reporter_account_id: str | None = None,
        parent_work_item_key: str | None = None,
    ):
        super().__init__()
        self._project_key = project_key
        self._reporter_account_id = reporter_account_id
        self._parent_work_item_key = parent_work_item_key
        self._field_metadata: dict[str, dict] = {}
        self._reporter_is_editable: bool = True  # Default to editable

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-work-item-button-save', expect_type=Button)

    @property
    def project_selector(self) -> CreateWorkItemProjectSelectionInput:
        return self.query_one(CreateWorkItemProjectSelectionInput)

    @property
    def issue_type_selector(self) -> CreateWorkItemIssueTypeSelectionInput:
        return self.query_one(CreateWorkItemIssueTypeSelectionInput)

    @property
    def reporter_selector(self) -> CreateWorkItemReporterSelectionInput:
        return self.query_one(CreateWorkItemReporterSelectionInput)

    @property
    def assignee_selector(self) -> CreateWorkItemAssigneeSelectionInput:
        return self.query_one(CreateWorkItemAssigneeSelectionInput)

    @property
    def summary_field(self) -> CreateWorkItemIssueSummaryField:
        return self.query_one(CreateWorkItemIssueSummaryField)

    @property
    def description_field(self) -> DescriptionWidget:
        return self.query_one(DescriptionWidget)

    @property
    def parent_key_field(self) -> CreateWorkItemParentKeyField:
        return self.query_one(CreateWorkItemParentKeyField)

    @property
    def additional_fields(self) -> Container:
        return self.query_one('#additional_fields', expect_type=Container)

    def _validate_required_fields(self) -> bool:
        """Check if all required fields have values.

        Returns:
            True if all required fields are filled, False otherwise.
        """
        # Build list of required field checks
        required_checks = [
            self.project_selector.selection,
            self.issue_type_selector.selection,
            self.summary_field.value,
        ]

        # Only check reporter if it's editable
        if self._reporter_is_editable:
            required_checks.append(self.reporter_selector.selection)

        basic_fields_valid = all(required_checks)

        # Check if description is required and has a value
        if self.description_field.required and not self.description_field.text.strip():
            return False

        return basic_fields_valid

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.TITLE
        with vertical:
            yield Static(
                Text('Important: Fields marked with (*) are required.', style='italic orange')
            )
            yield Rule(classes='rule-50')
            with VerticalScroll(id='add-work-item-form'):
                with ItemGrid(classes='add-work-item-fields-grid'):
                    yield CreateWorkItemProjectSelectionInput()
                    yield CreateWorkItemIssueTypeSelectionInput([])
                    yield CreateWorkItemReporterSelectionInput()
                    yield CreateWorkItemAssigneeSelectionInput()
                yield CreateWorkItemParentKeyField(self._parent_work_item_key)
                yield CreateWorkItemIssueSummaryField()
                yield DescriptionWidget(
                    mode=FieldMode.CREATE, field_id='description', title='Description'
                )
                yield Container(id='additional_fields')
            with ItemGrid(classes='add-work-item-grid-buttons'):
                yield Button(
                    'Save', variant='success', id='add-work-item-button-save', disabled=True
                )
                yield Button('Cancel', variant='error', id='add-work-item-button-quit')

    def on_mount(self):
        self.run_worker(self.fetch_available_projects())
        self.run_worker(self.fetch_available_issue_types())

    async def fetch_available_projects(self) -> None:
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.search_projects()
        if not response.success:
            projects: list[Project] = []
        else:
            projects = response.result or []
        projects.sort(key=lambda x: x.name)
        self.project_selector.projects = {'projects': projects, 'selection': self._project_key}

    async def fetch_available_issue_types(self, project_key: str | None = None) -> None:
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        key = project_key or self.project_selector.selection
        if key:
            response: APIControllerResponse = await application.api.get_issue_types_for_project(key)
            if not response.success:
                types: list[IssueType] = []
            else:
                types = response.result or []
            types.sort(key=lambda x: x.name)
            options = [(t.name, t.id) for t in types]
            self.issue_type_selector.set_options(options)

    async def fetch_users(self, project_key: str | None) -> None:
        if project_key:
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            response: APIControllerResponse = (
                await application.api.search_users_assignable_to_projects(
                    project_keys=[project_key],
                    active=True,
                )
            )
            if not response.success:
                self.assignee_selector.users = None
                self.reporter_selector.reporters = None
            else:
                self.assignee_selector.users = {'users': response.result or [], 'selection': None}
                self.reporter_selector.reporters = {
                    'users': response.result or [],
                    'selection': self._reporter_account_id,
                }

    @on(Select.Changed, 'CreateWorkItemProjectSelectionInput')
    def handle_project_selection(self) -> None:
        # fetch issue types for the project
        self.run_worker(self.fetch_available_issue_types(self.project_selector.selection))
        # fetch assignable users and reporters for the selected project
        self.run_worker(self.fetch_users(self.project_selector.selection))
        self.save_button.disabled = not self._validate_required_fields()

    @on(Select.Changed, 'CreateWorkItemIssueTypeSelectionInput')
    def handle_issue_type_selection(self) -> None:
        # fetch create metadata for issues in the selected project and of the selected type
        if self.project_selector.selection and self.issue_type_selector.selection:
            self.run_worker(
                self.fetch_issue_create_metadata(
                    self.project_selector.selection, self.issue_type_selector.selection
                ),
            )

        self.save_button.disabled = not self._validate_required_fields()

    @on(Select.Changed, 'CreateWorkItemReporterSelectionInput')
    def handle_reporter_selection(self) -> None:
        self.save_button.disabled = not self._validate_required_fields()

    @on(Input.Blurred, 'CreateWorkItemIssueSummaryField')
    def handle_summary_value_change(self):
        self.save_button.disabled = not self._validate_required_fields()

    @on(TextArea.Changed, 'DescriptionWidget')
    def handle_description_value_change(self):
        """Handle description field changes to update save button state."""
        self.save_button.disabled = not self._validate_required_fields()

    async def fetch_issue_create_metadata(self, project_key: str, issue_type_id: str) -> None:
        await self.additional_fields.remove_children()
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_issue_create_metadata(
            project_key, issue_type_id
        )
        if not response.success or not response.result:
            self.notify('Unable to find the required information for creating work items.')
        else:
            # Store field metadata for proper value formatting later
            fields_data = response.result.get('fields', [])
            for field in fields_data:
                field_id = field.get('fieldId')
                if field_id:
                    self._field_metadata[field_id] = field

                # Check if description is required and update the widget
                if field_id == 'description' and field.get('required', False):
                    self.description_field.mark_required()

                # Check if reporter field is editable
                if field_id == 'reporter':
                    operations = field.get('operations', [])
                    self._reporter_is_editable = 'set' in operations
                    # Hide reporter field if not editable
                    self.reporter_selector.display = self._reporter_is_editable

            metadata_fields: list[Widget] = create_widgets_for_work_item_creation(
                fields_data, api_controller=application.api
            )
            await self.additional_fields.mount_all(metadata_fields)

            user_picker_widgets = self.additional_fields.query(UserPickerWidget)
            if user_picker_widgets:
                users_response = await application.api.search_users_assignable_to_projects(
                    project_keys=[project_key],
                    active=True,
                )
                if users_response.success and users_response.result:
                    users_data = {'users': users_response.result, 'selection': None}
                    for user_picker in user_picker_widgets:
                        user_picker.users = users_data

            # Create and mount AutoComplete widgets for labels inputs
            all_inputs = self.additional_fields.query(Input)
            for input_widget in all_inputs:
                if input_widget.id == 'labels':
                    # Get field metadata to check if required
                    field_meta = self._field_metadata.get('labels', {})
                    required = field_meta.get('required', False)
                    title = field_meta.get('name', 'Labels')

                    autocomplete = LabelsAutoComplete(
                        target=input_widget,
                        api_controller=application.api,
                        required=required,
                        title=title,
                    )
                    await self.additional_fields.mount(autocomplete)

    def _format_field_value(self, field_id: str, value: Any, field_metadata: dict) -> Any:
        """Format a field value based on field metadata.

        This consolidated logic handles different field types like user pickers, floats,
        labels, and select fields. Extracted from inline logic for reusability.

        Args:
            field_id: The Jira field ID
            value: The raw value from the form widget
            field_metadata: The field metadata from Jira's create metadata API

        Returns:
            The formatted value ready for API submission, or None to skip the field.
        """
        if not value:
            return None

        schema = field_metadata.get('schema', {})
        custom_type = schema.get('custom')

        if custom_type == CustomFieldType.USER_PICKER.value:
            return {'accountId': value}

        elif custom_type == CustomFieldType.FLOAT.value:
            if value:  # Type-safe check to prevent ~AlwaysFalsy error
                try:
                    return float(value)
                except (ValueError, TypeError):
                    # Invalid float - skip this field
                    return None
            return None

        # Labels field (array of strings)
        elif (
            schema.get('type') == 'array'
            and schema.get('items') == 'string'
            and field_id == 'labels'
        ):
            if isinstance(value, str):
                # Split by comma and strip whitespace from each label
                labels = [label.strip() for label in value.split(',') if label.strip()]
                return labels
            elif isinstance(value, list):
                return value
            else:
                return []

        # Select-type fields (fields with allowedValues)
        elif field_metadata.get('allowedValues'):
            schema_type = schema.get('type')

            # Array type fields (like multi-select) need array of objects
            if schema_type == 'array':
                if isinstance(value, list):
                    return [{'id': v} for v in value]
                else:
                    return [{'id': value}]
            else:
                # Single-select: convert to object with 'id' key
                return {'id': value}

        # Default: pass value as-is
        return value

    @on(Button.Pressed, '#add-work-item-button-save')
    def handle_save(self) -> None:
        if not self._validate_required_fields():
            self.notify('All required values (*) must be provided.', title='Create Work Item')
        else:
            data = {
                'project_key': self.project_selector.selection,
                'parent_key': self.parent_key_field.value,
                'issue_type_id': self.issue_type_selector.selection,
                'assignee_account_id': self.assignee_selector.selection,
                'summary': self.summary_field.value,
                'description': self.description_field.text.strip()
                if self.description_field.text
                else None,
            }

            # Only include reporter if it's editable
            if self._reporter_is_editable:
                data['reporter_account_id'] = self.reporter_selector.selection
            for widget in self.additional_fields.children:
                field_id = widget.id
                if not field_id:
                    continue

                value: Any = None
                if isinstance(widget, MultiSelectWidget):
                    value = widget.get_value_for_update()
                    if value:
                        data[field_id] = value
                    continue
                elif isinstance(widget, Select):
                    value = widget.selection
                elif isinstance(widget, Input):
                    value = widget.value

                # Priority and duedate are base fields that don't need formatting
                if field_id in ('priority', 'duedate'):
                    data[field_id] = value
                    continue

                # Format the value based on field metadata using consolidated logic
                if value and field_id in self._field_metadata:
                    field_meta = self._field_metadata[field_id]
                    formatted_value = self._format_field_value(field_id, value, field_meta)
                    if formatted_value is not None:
                        data[field_id] = formatted_value
                elif value:
                    # No metadata available, pass as-is
                    data[field_id] = value
            self.notify('Creating the work item...', title='Create Work Item')
            self.dismiss(data)

    @on(Button.Pressed, '#add-work-item-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})
