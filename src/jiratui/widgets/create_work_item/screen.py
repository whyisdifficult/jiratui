from typing import cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Rule, Select, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import IssueType, Project
from jiratui.widgets.commons.users import JiraUserInput, UsersAutoComplete
from jiratui.widgets.create_work_item.factory import create_widgets_for_work_item_creation
from jiratui.widgets.create_work_item.fields import (
    CreateWorkItemDescription,
    CreateWorkItemIssueSummaryField,
    CreateWorkItemIssueTypeSelectionInput,
    CreateWorkItemParentKeyField,
    CreateWorkItemProjectSelectionInput,
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
        """Initializes the screen.

        Args:
            project_key: the key of the project for which the work item will be created. If not defined the user will
            need to choose it from a dropdown list.
            reporter_account_id: the account id of the user that acts as a reporter. Ths is injected from the main
            screen which in turn can be picked up from the cli or the configuration file. If not defined the user will
            need to choose it from a dropdown list.
            parent_work_item_key: the key of the parent work item to which this work item belongs. If not defined the
            user will be able to set one.
        """

        super().__init__()
        self._project_key = project_key
        self._reporter_account_id = reporter_account_id
        self._parent_work_item_key = parent_work_item_key

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
    def assignee_selector(self) -> JiraUserInput:
        return self.query_one('#create-work-item-assignee-selector', expect_type=JiraUserInput)

    @property
    def summary_field(self) -> CreateWorkItemIssueSummaryField:
        return self.query_one(CreateWorkItemIssueSummaryField)

    @property
    def description_field(self) -> CreateWorkItemDescription:
        return self.query_one(CreateWorkItemDescription)

    @property
    def parent_key_field(self) -> CreateWorkItemParentKeyField:
        return self.query_one(CreateWorkItemParentKeyField)

    @property
    def additional_fields(self) -> VerticalScroll:
        return self.query_one('#additional_fields', expect_type=VerticalScroll)

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
                    yield CreateWorkItemProjectSelectionInput([])
                    yield CreateWorkItemIssueTypeSelectionInput([])
                    # set widgets in row 2
                    # this input field contains the account id of the Jira user that we can use to update the item's
                    # assignee field
                    reporter_input = JiraUserInput(
                        id='create-work-item-reporter-selector',
                        border_title='Reporter',
                        border_subtitle='(*)',
                        jira_field_key='reporter_account_id',
                    )
                    reporter_input.add_class(*['required'])
                    yield reporter_input
                    yield UsersAutoComplete(reporter_input, self.app.api)
                    # this input field contains the account id of the Jira user that we can use to update the item's
                    # assignee field
                    assignee_input = JiraUserInput(
                        id='create-work-item-assignee-selector',
                        border_title='Assignee',
                        jira_field_key='assignee_account_id',
                    )
                    yield assignee_input
                    yield UsersAutoComplete(assignee_input, self.app.api)
                yield CreateWorkItemParentKeyField(self._parent_work_item_key)
                yield CreateWorkItemIssueSummaryField()
                yield CreateWorkItemDescription()
                yield VerticalScroll(id='additional_fields')
            with ItemGrid(classes='add-work-item-grid-buttons'):
                yield Button(
                    'Save', variant='success', id='add-work-item-button-save', disabled=True
                )
                yield Button('Cancel', variant='error', id='add-work-item-button-quit')

    def on_mount(self):
        """Mounts the widgets.

        This fetches the required data to populate the widgets. It fetches the available projects available types of
        issues that cna be created.
        """

        self.run_worker(self.fetch_available_projects())
        self.run_worker(self.fetch_available_issue_types())
        if self._reporter_account_id:
            self.run_worker(self._fetch_reporter())

    async def _fetch_reporter(self):
        user_response: APIControllerResponse = await self.app.api.get_user(self._reporter_account_id)
        if user_response.success and (use_details := user_response.result):
            self.reporter_selector.set_value(self._reporter_account_id, use_details.display_name)

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

    @on(Select.Changed, 'CreateWorkItemProjectSelectionInput')
    def handle_project_selection(self) -> None:
        # fetch issue types for the project
        self.run_worker(self.fetch_available_issue_types(self.project_selector.selection))
        self.save_button.disabled = not (
            self.project_selector.selection
            and self.issue_type_selector.selection
            and self.reporter_selector.value
            and self.summary_field.value
        )

    @on(Select.Changed, 'CreateWorkItemIssueTypeSelectionInput')
    def handle_issue_type_selection(self) -> None:
        # fetch create metadata for issues in the selected project and of the selected type
        if self.project_selector.selection and self.issue_type_selector.selection:
            self.run_worker(
                self.fetch_issue_create_metadata(
                    self.project_selector.selection, self.issue_type_selector.selection
                ),
            )

        self.save_button.disabled = not all(
            [
                self.project_selector.selection,
                self.issue_type_selector.selection,
                self.reporter_selector.value,
                self.summary_field.value,
            ]
        )

    @on(Select.Changed, '#create-work-item-reporter-selector')
    def handle_reporter_selection(self) -> None:
        self.save_button.disabled = not all(
            [
                self.project_selector.selection,
                self.issue_type_selector.selection,
                self.reporter_selector.value,
                self.summary_field.value,
            ]
        )

    @on(Input.Blurred, 'CreateWorkItemIssueSummaryField')
    def handle_summary_value_change(self):
        self.save_button.disabled = not all(
            [
                self.project_selector.selection,
                self.issue_type_selector.selection,
                self.reporter_selector.value,
                self.summary_field.value,
            ]
        )

    async def fetch_issue_create_metadata(self, project_key: str, issue_type_id: str) -> None:
        await self.additional_fields.remove_children()
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_issue_create_metadata(
            project_key, issue_type_id
        )
        if not response.success or not response.result:
            self.notify('Unable to find the required information for creating work items.')
        else:
            metadata_fields: list[Widget] = create_widgets_for_work_item_creation(
                response.result.get('fields', [])
            )
            await self.additional_fields.mount_all(metadata_fields)

    @on(Button.Pressed, '#add-work-item-button-save')
    def handle_save(self) -> None:
        if not all(
            [
                self.project_selector.selection,
                self.issue_type_selector.selection,
                self.reporter_selector.value,
                self.summary_field.value,
            ]
        ):
            self.notify('Fields marked with (*) must be provided.', title='Create Work Item')
        else:
            data = {
                'project_key': self.project_selector.selection,
                'parent_key': self.parent_key_field.value,
                'issue_type_id': self.issue_type_selector.selection,
                self.assignee_selector.jira_field_key: self.assignee_selector.account_id,
                self.reporter_selector.jira_field_key: self.reporter_selector.account_id,
                'summary': self.summary_field.value,
                'description': self.description_field.text.strip()
                if self.description_field.text
                else None,
            }
            for widget in self.additional_fields.children:
                if isinstance(widget, Select):
                    data[widget.id] = widget.selection
                elif isinstance(widget, Input):
                    data[widget.id] = widget.value
            self.notify('Creating the work item...', title='Create Work Item')
            self.dismiss(data)

    @on(Button.Pressed, '#add-work-item-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})
