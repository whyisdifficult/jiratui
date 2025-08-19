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
from jiratui.utils.create_work_item import create_widgets_for_work_item_creation
from jiratui.widgets.base import CustomTitle
from jiratui.widgets.create_work_item.fields import (
    CreateWorkItemAssigneeSelectionInput,
    CreateWorkItemDescription,
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
    def description_field(self) -> CreateWorkItemDescription:
        return self.query_one(CreateWorkItemDescription)

    @property
    def parent_key_field(self) -> CreateWorkItemParentKeyField:
        return self.query_one(CreateWorkItemParentKeyField)

    @property
    def additional_fields(self) -> VerticalScroll:
        return self.query_one('#additional_fields', expect_type=VerticalScroll)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle(self.TITLE)
            yield Static(
                Text('Important: Fields marked with (*) are required.', style='italic orange')
            )
            yield Rule(classes='rule-50')
            with VerticalScroll(id='add-work-item-form'):
                with ItemGrid(classes='add-work-item-fields-grid'):
                    yield CreateWorkItemProjectSelectionInput([])
                    yield CreateWorkItemIssueTypeSelectionInput([])
                    yield CreateWorkItemReporterSelectionInput([])
                    yield CreateWorkItemAssigneeSelectionInput([])
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

    async def fetch_users(self, project_key: str) -> None:
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
        self.save_button.disabled = not (
            self.project_selector.selection
            and self.issue_type_selector.selection
            and self.reporter_selector.selection
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
                self.reporter_selector.selection,
                self.summary_field.value,
            ]
        )

    @on(Select.Changed, 'CreateWorkItemReporterSelectionInput')
    def handle_reporter_selection(self) -> None:
        self.save_button.disabled = not all(
            [
                self.project_selector.selection,
                self.issue_type_selector.selection,
                self.reporter_selector.selection,
                self.summary_field.value,
            ]
        )

    @on(Input.Blurred, 'CreateWorkItemIssueSummaryField')
    def handle_summary_value_change(self):
        self.save_button.disabled = not all(
            [
                self.project_selector.selection,
                self.issue_type_selector.selection,
                self.reporter_selector.selection,
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
                self.reporter_selector.selection,
                self.summary_field.value,
            ]
        ):
            self.notify('All required values (*) must be provided.', title='Create Work Item')
        else:
            data = {
                'project_key': self.project_selector.selection,
                'parent_key': self.parent_key_field.value,
                'issue_type_id': self.issue_type_selector.selection,
                'assignee_account_id': self.assignee_selector.selection,
                'reporter_account_id': self.reporter_selector.selection,
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
