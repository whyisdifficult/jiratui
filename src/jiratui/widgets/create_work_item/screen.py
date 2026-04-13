from typing import Any, cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Rule, Select, Static, TextArea

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import IssueType, Project
from jiratui.widgets.commons import CustomFieldType
from jiratui.widgets.commons.base import (
    FieldMode,
    LabelsAutoComplete,
    MultiUserPickerAutoComplete,
    UserPickerWidget,
)
from jiratui.widgets.commons.users import JiraUserInput, UsersAutoComplete
from jiratui.widgets.commons.widgets import (
    DescriptionWidget,
    LabelsWidget,
    MultiSelectWidget,
    MultiUserPickerWidget,
)
from jiratui.widgets.create_work_item.factory import create_widgets_for_work_item_creation
from jiratui.widgets.create_work_item.fields import (
    CreateWorkItemIssueSummaryField,
    CreateWorkItemIssueTypeSelectionInput,
    CreateWorkItemParentKeyField,
    CreateWorkItemProjectSelectionInput,
)


class AddWorkItemScreen(Screen[dict[str, Any]]):
    """A modal screen for adding work items.

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
    """

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'New Work Item'

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

    @property
    def reporter_account_id(self) -> str | None:
        return self._reporter_account_id

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
    def summary_field(self) -> CreateWorkItemIssueSummaryField:
        return self.query_one(CreateWorkItemIssueSummaryField)

    @property
    def description_field(self) -> DescriptionWidget:
        return self.query_one(DescriptionWidget)

    @property
    def parent_key_field(self) -> CreateWorkItemParentKeyField:
        return self.query_one(CreateWorkItemParentKeyField)

    @property
    def additional_fields(self) -> VerticalScroll:
        return self.query_one('#create-additional-fields', expect_type=VerticalScroll)

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
                    # set widgets in row 1
                    yield CreateWorkItemProjectSelectionInput()
                    yield CreateWorkItemIssueTypeSelectionInput([])
                    # set widgets in row 2
                    # this input field contains the account id of the Jira user that we can use to update the item's
                    # assignee field
                    yield JiraUserInput(
                        id='create-work-item-reporter-selector',
                        border_title='Reporter',
                        border_subtitle='(*)',
                        jira_field_key='reporter_account_id',
                    ).add_class(*['required'])
                    # this input field contains the account id of the Jira user that we can use to update the item's
                    # assignee field
                    yield JiraUserInput(
                        id='create-work-item-assignee-selector',
                        border_title='Assignee',
                        jira_field_key='assignee_account_id',
                    )
                yield CreateWorkItemParentKeyField(self._parent_work_item_key)
                yield CreateWorkItemIssueSummaryField()
                yield DescriptionWidget(
                    mode=FieldMode.CREATE, field_id='description', title='Description'
                )
                yield VerticalScroll(id='create-additional-fields')
            with ItemGrid(classes='add-work-item-grid-buttons'):
                yield Button(
                    'Save', variant='success', id='add-work-item-button-save', disabled=True
                )
                yield Button('Cancel', variant='error', id='add-work-item-button-quit')

    def on_mount(self):
        """Mounts the widgets.

        This fetches the required data to populate the widgets. It fetches the available projects and the available
        types of issues that can be created.
        """

        self.run_worker(self.fetch_available_projects())
        self.run_worker(self.fetch_available_issue_types())
        # TODO check if this works because at mounting time _reporter_is_editable is always false
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
        self.mount_all([reporter_autocomplete, assignee_autocomplete])

    async def _search_and_filter_assignees(self, query: str) -> APIControllerResponse:
        # searches and filters users that can be assignees of the work item being created.
        return await self.app.api.search_users_assignable_to_issue(  # type:ignore[attr-defined]
            project_id_or_key=self.project_selector.selection, query=query
        )

    async def _fetch_reporter(self):
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

        Args:
            project_key: the key of the project selected by the user.

        Returns:
            None
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        key = project_key or self.project_selector.selection
        if key:
            response: APIControllerResponse = await application.api.get_issue_types_for_project(key)
            types: list[IssueType] = []
            if response.success:
                types = response.result or []
            types.sort(key=lambda x: x.name)
            options = [(t.name, t.id) for t in types]
            self.issue_type_selector.set_options(options)

    @on(Select.Changed, 'CreateWorkItemProjectSelectionInput')
    def handle_project_selection(self) -> None:
        """Fetches the applicable types of work items for creating issues in the selected project.

        This also updates the status of the "Save" button.

        Returns:
            None.
        """

        self.run_worker(self.fetch_available_issue_types(self.project_selector.selection))
        self.save_button.disabled = not self._validate_required_fields()

    @on(Select.Changed, 'CreateWorkItemIssueTypeSelectionInput')
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

    @on(Input.Blurred, 'CreateWorkItemIssueSummaryField')
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
                fields_data,
                api_controller=application.api,
            )
            await self.additional_fields.mount_all(metadata_fields)

            # TODO test this logic to see what it does
            if user_picker_widgets := self.additional_fields.query(UserPickerWidget):
                users_response = await application.api.search_users_assignable_to_projects(
                    project_keys=[project_key],
                    active=True,
                )
                if users_response.success and users_response.result:
                    users_data = {'users': users_response.result, 'selection': None}
                    for user_picker in user_picker_widgets:
                        user_picker.users = users_data

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

        elif custom_type == CustomFieldType.FLOAT.value:
            if value:  # Type-safe check to prevent ~AlwaysFalsy error
                try:
                    return float(value)
                except (ValueError, TypeError):
                    # invalid float - skip this field
                    return None
            return None

        # labels field (array of strings)
        elif (
            schema.get('type') == 'array'
            and schema.get('items') == 'string'
            and field_id == 'labels'
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

    @on(Button.Pressed, '#add-work-item-button-save')
    def handle_save(self) -> None:
        """Builds the necessary payload data for creating a new work item.

        This **does not** actually create the work item. Instead, it passes the payload data to the main screen upon
        dismissal. The main screen is then responsible for requesting the API to create a new work item with the given
        payload.

        Returns:
            None.
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
                self.description_field.jira_field_key: self.description_field.text.strip()
                if self.description_field.text
                else None,
            }

            # only include reporter if it's editable
            if self._reporter_is_editable:
                data[self.reporter_selector.jira_field_key] = self.reporter_selector.account_id

            # process widgets that are created dynamically
            for widget in self.additional_fields.children:
                if not (field_id := widget.id):
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

            self.notify('Creating the work item...', title='Create Work Item')
            self.dismiss(data)

    @on(Button.Pressed, '#add-work-item-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})
