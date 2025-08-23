from datetime import datetime
from typing import Any, cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import Input, Label, ProgressBar, Select, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.exceptions import UpdateWorkItemException, ValidationError
from jiratui.models import IssuePriority, JiraIssue, JiraUser, TimeTracking
from jiratui.utils.work_item_updates import (
    work_item_assignee_has_changed,
    work_item_priority_has_changed,
)
from jiratui.widgets.base import DateInput, ReadOnlyField, ReadOnlyTextField
from jiratui.widgets.filters import IssueStatusSelectionInput, UserSelectionInput
from jiratui.widgets.work_item_details.work_log import WorkItemWorkLogScreen


class IssueDetailsAssigneeSelection(UserSelectionInput):
    WIDGET_ID = 'jira-users-selector-edit'
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self, users: list):
        super().__init__(users)
        self.border_subtitle = '(x)'
        self.jira_field_key = 'assignee'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled: bool = True
        """Indicates whether the work item allows editing/updating this field."""

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled


class IssueDetailsStatusSelection(IssueStatusSelectionInput):
    WIDGET_ID = 'jira-issue-status-selector-edit'

    def __init__(self, statuses: list):
        super().__init__(statuses)
        self.border_subtitle = '(z)'
        self.jira_field_key = 'status'
        """The key to used by Jira to identify this field in the edit-metadata."""


class IssueDetailsPrioritySelection(Select):
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self, priorities: list[tuple[str, str]]):
        super().__init__(
            options=priorities,
            prompt='Select a priority',
            name='priorities',
            id='jira-issue-priority-selector-edit',
            type_to_search=True,
            compact=True,
        )
        self.border_title = 'Priority'
        self.border_subtitle = '(y)'
        self.jira_field_key = 'priority'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled: bool = True
        """Indicates whether the work item allows editing/updating this field."""

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled


class ProjectIDField(ReadOnlyField):
    def __init__(self):
        super().__init__()
        self.border_title = 'Project'
        self.add_class(*['issue_details_input_field', 'cols-3'])


class ReporterField(ReadOnlyField):
    def __init__(self):
        super().__init__(placeholder='-')
        self.border_title = 'Reporter'
        self.add_class(*['issue_details_input_field', 'cols-2'])


class IssueSprintField(ReadOnlyField):
    def __init__(self):
        super().__init__()
        self.border_title = 'Sprint'
        self.classes = 'issue_details_input_field'


class IssueKeyField(ReadOnlyField):
    def __init__(self):
        super().__init__()
        self.border_title = 'Key'
        self.add_class(*['issue_details_input_field', 'work-item-key'])


class IssueParentField(ReadOnlyField):
    def __init__(self):
        super().__init__()
        self.border_title = 'Parent'
        self.add_class(*['issue_details_input_field', 'work-item-key'])


class IssueSummaryField(Input):
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self):
        super().__init__()
        self.border_title = 'Summary'
        self.border_subtitle = '(*)'
        self.add_class(*['issue_details_input_field', 'required', 'cols-3'])
        self.jira_field_key = 'summary'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled: bool = True
        """Indicates whether the work item allows editing/updating this field."""

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip()

    @property
    def validated_summary(self) -> str | None:
        if self.value:
            return self.value.strip()
        return self.value


class WorkItemLabelsField(Input):
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self):
        super().__init__()
        self.border_title = 'Labels'
        self.add_class(*['issue_details_input_field', 'cols-3'])
        self.jira_field_key = 'labels'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled: bool = True
        """Indicates whether the work item allows editing/updating this field."""

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.value:
            self.value = event.value.lower().replace(' ', '-')

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled


class IssueTypeField(ReadOnlyField):
    def __init__(self):
        super().__init__()
        self.border_title = 'Type'
        self.classes = 'issue_details_input_field'


class WorkItemDetailsDueDate(DateInput):
    LABEL = 'Due Date'
    TOOLTIP = 'The due date for this work item'
    ID = 'input_due_date'
    CLASSES = None
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self):
        super().__init__()
        self.jira_field_key = 'duedate'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled: bool = True
        """Indicates whether the work item allows editing/updating this field."""

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled


class TimeTrackingContainer(Center):
    DEFAULT_CSS = """
    TimeTrackingContainer {
        align-horizontal: left;
        box_sizing: content-box;
        height: auto;
        border: round $primary-lighten-3;
        margin: 0 0;
        padding: 0 1;
        background: $background;
        &.required {
            border: round red;
        }
        &:focus {
            border: round $accent-lighten-3;
        }
    }
    Bar > .bar--bar {
        color: yellow;
        background: $secondary;
    }
    """

    def __init__(self):
        super().__init__(classes='cols-3')
        self.border_title = 'Time Tracking'


class IssueDetailsWidget(VerticalScroll):
    """Implements a form to allow the user to view and edit some of the fields associated to a work item.

    The list of fields that can be updated are fixed:
    - Summary
    - Assignee
    - Status
    - Priority
    - Due Date
    - Labels

    Whether these fields can be updated depends on the work item's edit metadata. Some work items disallow editing
    certain fields. For example, work items of type "subtask" typically do not allow the user to update the due date.
    """

    HELP = """\
# Work Item Details

This contains the details of the selected work item. Some of these detail scan be edited. Currently, the fields that
can be edited are:
- Summary
- Assignee
- Status
- Priority
- Due Date
- Labels

To edit a field simply focus on it, change its value and then press `^s`.
    """

    issue: Reactive[JiraIssue | None] = reactive(None, always_update=True)
    """Reactive variable that contains the work item currently being displayed."""
    clear_form: Reactive[bool] = reactive(False, always_update=True)
    """Reactive variable to clear the fields in the form."""

    BINDINGS = [
        ('ctrl+s', 'save_work_item', 'Save Changes'),
        Binding(
            key='x',
            action='focus_widget("x")',
            description='Focus the Assignee widget',
            show=False,
        ),
        Binding(
            key='y',
            action='focus_widget("y")',
            description='Focus the Priority widget',
            show=False,
        ),
        Binding(
            key='z',
            action='focus_widget("z")',
            description='Focus the Status widget',
            show=False,
        ),
        Binding(
            key='ctrl+l',
            action='view_issue_work_log',
            description='View Work Log',
            show=True,
        ),
    ]

    def __init__(self):
        super().__init__(id='issue_details')
        self.available_users: list[tuple[str, str]] | None = None

    @property
    def issue_type_field(self) -> IssueTypeField:
        return self.query_one(IssueTypeField)

    @property
    def issue_status_selector(self) -> IssueDetailsStatusSelection:
        return self.query_one(IssueDetailsStatusSelection)

    @property
    def assignee_selector(self) -> IssueDetailsAssigneeSelection:
        return self.query_one(IssueDetailsAssigneeSelection)

    @property
    def priority_selector(self) -> IssueDetailsPrioritySelection:
        return self.query_one(IssueDetailsPrioritySelection)

    @property
    def project_id_field(self) -> ProjectIDField:
        return self.query_one(ProjectIDField)

    @property
    def reporter_field(self) -> ReporterField:
        return self.query_one(ReporterField)

    @property
    def issue_key_field(self) -> IssueKeyField:
        return self.query_one(IssueKeyField)

    @property
    def issue_parent_field(self) -> IssueParentField:
        return self.query_one(IssueParentField)

    @property
    def issue_sprint_field(self) -> IssueSprintField:
        return self.query_one(IssueSprintField)

    @property
    def issue_resolution_field(self) -> ReadOnlyTextField:
        return self.query_one('#issue_resolution', expect_type=ReadOnlyTextField)

    @property
    def issue_time_tracking(self) -> ProgressBar:
        return self.query_one(ProgressBar)

    @property
    def issue_summary_field(self) -> IssueSummaryField:
        return self.query_one(IssueSummaryField)

    @property
    def issue_created_date_field(self) -> ReadOnlyTextField:
        return self.query_one('#issue_created_date', expect_type=ReadOnlyTextField)

    @property
    def issue_last_update_date_field(self) -> ReadOnlyTextField:
        return self.query_one('#issue_last_update_date', expect_type=ReadOnlyTextField)

    @property
    def issue_due_date_field(self) -> WorkItemDetailsDueDate:
        return self.query_one(WorkItemDetailsDueDate)

    @property
    def time_tracking_container(self) -> TimeTrackingContainer:
        return self.query_one(TimeTrackingContainer)

    @property
    def work_item_labels_widget(self) -> WorkItemLabelsField:
        return self.query_one(WorkItemLabelsField)

    @property
    def issue_resolution_date_field(self) -> ReadOnlyTextField:
        return self.query_one('#issue_resolution_date', expect_type=ReadOnlyTextField)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id='issue-details-form'):
            # row 1
            yield IssueSummaryField()
            # row 2
            yield IssueDetailsAssigneeSelection([])
            yield IssueDetailsStatusSelection([])
            yield IssueTypeField()
            # row 3
            yield IssueKeyField()
            yield IssueParentField()
            yield IssueSprintField()
            # row 4
            yield ProjectIDField()
            # row 5
            yield IssueDetailsPrioritySelection([])
            yield ReporterField()
            # row 6
            yield ReadOnlyTextField(
                id='issue_created_date',
                label='Created',
                disabled=True,
                valid_empty=True,
                extra_classes='input-date',
            )
            yield ReadOnlyTextField(
                id='issue_last_update_date',
                label='Last Update',
                disabled=True,
                valid_empty=True,
                extra_classes='input-date',
            )
            yield WorkItemDetailsDueDate()
            # row 7
            yield ReadOnlyTextField(
                id='issue_resolution_date',
                label='Resolved',
                disabled=True,
                valid_empty=True,
                extra_classes='input-date',
            )
            yield ReadOnlyTextField(
                id='issue_resolution',
                label='Resolution',
                disabled=True,
                valid_empty=True,
                extra_classes='cols-2',
            )
            # row 8
            yield WorkItemLabelsField()
            # row 9
            yield TimeTrackingContainer()

    def action_focus_widget(self, key: str) -> None:
        """Focuses a widget depending on the key pressed.

        This will only focus the following widgets:
        - assignee_selector (key `x`)
        - priority_selector (key `y`)
        - issue_status_selector (key `z`)

        Args:
            key: the key that was pressed.

        Returns:
            Nothing.
        """
        if key == 'x':
            self.screen.set_focus(self.assignee_selector)
        elif key == 'y':
            self.screen.set_focus(self.priority_selector)
        elif key == 'z':
            self.screen.set_focus(self.issue_status_selector)

    def action_view_issue_work_log(self) -> None:
        """Opens a pop-up modal to display the work log of a work item.

        Returns:
            Nothing.
        """
        if self.issue:
            self.app.push_screen(WorkItemWorkLogScreen(self.issue.key))

    def _update_priority_selection(self, priorities, priority_id: str) -> None:
        for priority in priorities or []:
            if priority[1] == priority_id:
                self.priority_selector.value = priority_id
                return

    def _setup_priority_selector(
        self, issue_edit_meta: dict, issue_priority: IssuePriority
    ) -> None:
        if issue_edit_meta:
            # the issue may not support priority, for example Epics. In that case disable the select widget
            if not (priority_field := issue_edit_meta.get('fields', {}).get('priority')):
                self.priority_selector.update_enabled = False
            else:
                priorities: list[tuple[str, str]] = []
                for v in priority_field.get('allowedValues', []):
                    priorities.append((v.get('name'), v.get('id')))
                self.priority_selector.set_options(priorities)
                if issue_priority:
                    # update the selection with the issue's current priority value
                    self._update_priority_selection(priorities, issue_priority.id)
        else:
            # we can't determine if priority is supported; disable its selection/editing
            self.priority_selector.update_enabled = False

    def watch_clear_form(self, clear: bool = False) -> None:
        """Resets the fields to make sure that there are no values from the previously selected work item.

        Args:
            clear: if `True` it will reset the form's fields to their default values.

        Returns:
            Nothing.
        """
        if clear:
            self.issue_summary_field.value = ''
            self.issue_parent_field.value = ''
            self.issue_resolution_field.value = ''
            self.issue_resolution_date_field.value = ''
            self.issue_last_update_date_field.value = ''
            self.reporter_field.value = ''
            self.issue_key_field.value = ''
            self.project_id_field.value = ''
            self.issue_type_field.value = ''
            self.issue_sprint_field.value = ''
            self.issue_status_selector.value = Select.BLANK
            self.assignee_selector.value = Select.BLANK
            self.priority_selector.value = Select.BLANK
            self.priority_selector.update_enabled = True
            self.issue_due_date_field.value = ''
            self.work_item_labels_widget.value = ''

    def _setup_time_tracking(self, time_tracking_data: TimeTracking) -> None:
        self.time_tracking_container.remove_children()
        if not time_tracking_data:
            self.time_tracking_container.mount(Static('N/A'))
            return

        self.time_tracking_container.mount_all(
            [
                ProgressBar(total=100, show_percentage=True, show_eta=False),
                Label(
                    f'Original Estimate: {time_tracking_data.original_estimate or "-"} | Time Spent: {time_tracking_data.time_spent or "-"} | Remaining Estimate: {time_tracking_data.remaining_estimate or "-"}'
                ),
            ]
        )
        if time_tracking_data.original_estimate_seconds:
            self.issue_time_tracking.progress = (
                (time_tracking_data.time_spent_seconds or 0) * 100
            ) / time_tracking_data.original_estimate_seconds
        elif (
            time_tracking_data.remaining_estimate_seconds and time_tracking_data.time_spent_seconds
        ):
            self.issue_time_tracking.progress = (time_tracking_data.time_spent_seconds * 100) / (
                time_tracking_data.remaining_estimate_seconds
                + time_tracking_data.time_spent_seconds
            )

    def _build_payload_for_update(self) -> dict:
        payload: dict[str, Any] = {}
        if self.issue_summary_field.update_enabled:
            # check if the summary is not empty and has changed
            if (
                summary := self.issue_summary_field.validated_summary
            ) and summary != self.issue.summary:
                payload['summary'] = summary

        if self.issue_due_date_field.update_enabled:
            # check if the due date has changed
            if (
                cleaned_value := self.issue_due_date_field.value.strip()
            ) != '' or self.issue.due_date is not None:
                if cleaned_value != self.issue.due_date:
                    payload['due_date'] = cleaned_value

        if self.priority_selector.update_enabled:
            if work_item_priority_has_changed(
                self.issue.priority, self.priority_selector.selection
            ):
                if self.priority_selector.selection is None:
                    # the user is trying to set the priority to None; this is not allowed
                    self.notify(
                        'Unsetting the priority of this work item is not possible',
                        severity='warning',
                    )
                else:
                    payload['priority'] = self.priority_selector.selection

        if self.assignee_selector.update_enabled:
            # check if the assignee has changed
            if work_item_assignee_has_changed(
                self.issue.assignee, self.assignee_selector.selection
            ):
                payload['assignee_account_id'] = self.assignee_selector.selection

        if self.work_item_labels_widget.update_enabled and self.work_item_labels_widget.value:
            # update the issue's labels
            labels: list[str] = [
                label
                for label in self.work_item_labels_widget.value.split(',')
                if label and label != '-'
            ]
            if labels:
                current_labels: list[str] = [lbl.lower() for lbl in self.issue.labels or []]
                if not current_labels or (set(labels) != set(current_labels)):
                    # update the list of labels
                    payload['labels'] = labels
        return payload

    async def action_save_work_item(self) -> None:
        """Updates the fields of a work item that have changed.

        Returns:
            Nothing.
        """
        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        if payload := self._build_payload_for_update():
            try:
                response: APIControllerResponse = await application.api.update_issue(
                    self.issue, payload
                )
            except UpdateWorkItemException as e:
                self.notify(
                    f'An error occurred while trying to update the item: {e}',
                    severity='error',
                    title='Update Work Item',
                )
            except ValidationError as e:
                self.notify(
                    f'Data validation error: {e}',
                    severity='error',
                    title='Update Work Item',
                )
            except Exception as e:
                self.notify(
                    f'An unknown error occurred while trying to update the item: {e}',
                    severity='error',
                    title='Update Work Item',
                )
            else:
                if response.success:
                    self.notify('Work item updated successfully.', title='Update Work Item')
                else:
                    self.notify(
                        'The work item was not updated.',
                        severity='error',
                        title='Update Work Item',
                    )
                    self.notify(
                        response.error,
                        severity='error',
                        title='Update Work Item',
                    )

        # check if we need to transition the issue and move it to the new status if needed
        if (
            self.issue_status_selector.selection is not None
            and self.issue_status_selector.selection != self.issue.status.id
        ):
            response = await application.api.transition_issue_status(
                self.issue.key, self.issue_status_selector.selection
            )
            if not response.success:
                self.notify(
                    f'Failed to transition the work item to a different status: {response.error}',
                    severity='error',
                    title='Update Work Item',
                )
            else:
                self.notify(
                    'Successfully transitioned the work item to a different status.',
                    title='Update Work Item',
                )

    @staticmethod
    def _determine_editable_fields(metadata: dict | None = None) -> dict:
        if not metadata:
            return {}
        if not (fields := metadata.get('fields', {})):
            return {}

        editable_fields: dict[str, bool] = {}

        if field_summary := fields.get('summary', {}):
            editable_fields[field_summary.get('key')] = 'set' in field_summary.get('operations', {})

        if field_due_date := fields.get('duedate', {}):
            editable_fields[field_due_date.get('key')] = 'set' in field_due_date.get(
                'operations', {}
            )

        if field_priority := fields.get('priority', {}):
            editable_fields[field_priority.get('key')] = 'set' in field_priority.get(
                'operations', {}
            )

        if field_assignee := fields.get('assignee', {}):
            editable_fields[field_assignee.get('key')] = 'set' in field_assignee.get(
                'operations', {}
            )

        if field_labels := fields.get('labels', {}):
            editable_fields[field_labels.get('key')] = 'set' in field_labels.get('operations', {})

        return editable_fields

    async def retrieve_users_assignable_to_work_item(
        self,
        work_item_key: str,
        current_assignee: JiraUser | None = None,
        field_is_editable: bool | None = None,
    ) -> None:
        """Retrieves the users that can be assigned to a work item and sets the value of the assignee selector.

        If the API does not return a list of users then the widget will fall back to using the list of available users
        fetched by the application on start up; if any user is found.

        Args:
            work_item_key: the (case-sensitive) key of the work item.
            current_assignee: the user currently assigned to the item.
            field_is_editable: indicates whether the work item's assignee field is editable.

        Returns:
            Nothing.
        """
        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.search_users_assignable_to_issue(
            issue_key=work_item_key
        )
        selectable_users: list[tuple[str, str]] = self.available_users or []
        if response.result:
            user: JiraUser
            selectable_users = []
            for user in response.result:
                selectable_users.append((user.display_name, user.account_id))

        if selectable_users:
            self.assignee_selector.set_options(selectable_users)
            if current_assignee:
                # update the current selection
                self.assignee_selector.value = current_assignee.account_id
            self.assignee_selector.update_enabled = field_is_editable
        else:
            if current_assignee:
                self.assignee_selector.set_options(
                    [(current_assignee.display_name, current_assignee.account_id)]
                )
                self.assignee_selector.update_enabled = field_is_editable
            else:
                self.assignee_selector.update_enabled = False

    async def retrieve_applicable_status_codes(
        self,
        project_key: str,
        work_item_type_id: str,
        current_status_id: str,
    ) -> None:
        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_project_statuses(project_key)
        if not response.success:
            self.issue_status_selector.set_options([])
        else:
            status_codes_by_work_item_type_id: dict = response.result or {}
            record: dict = status_codes_by_work_item_type_id.get(work_item_type_id, {})
            work_status_codes_options = sorted(
                [(status.name, str(status.id)) for status in record.get('issue_type_statuses', [])],
                key=lambda x: x[0],
            )
            self.issue_status_selector.set_options(work_status_codes_options)
            if current_status_id and work_status_codes_options:
                self.issue_status_selector.value = current_status_id

    def watch_issue(self, response: JiraIssue | None) -> None:
        """Updates the update-form fields associated to a work item.

        Args:
            response: a work item selected by the user in the left-hand side panel.

        Returns:
            Nothing.
        """

        # "reset" the form by setting the value of all its elements to the default
        self.clear_form = True

        if not response:
            return

        # fetch the list of status codes applicable for this work item and its type
        self.run_worker(
            self.retrieve_applicable_status_codes(
                response.project.key, response.issue_type.id, str(response.status.id)
            )
        )

        editable_fields = self._determine_editable_fields(response.edit_meta)

        # fetch the list of assignable users for the work item
        self.run_worker(
            self.retrieve_users_assignable_to_work_item(
                response.key,
                response.assignee,
                editable_fields.get(self.assignee_selector.jira_field_key),
            )
        )

        # set the value fo the form fields based on the work item's data
        if response.resolution_date:
            self.issue_resolution_date_field.value = datetime.strftime(
                response.resolution_date, '%Y-%m-%d %H:%M'
            )
        if response.resolution:
            self.issue_resolution_field.value = response.resolution
        if response.updated:
            self.issue_last_update_date_field.value = datetime.strftime(
                response.updated, '%Y-%m-%d %H:%M'
            )
        if reporter := response.reporter:
            self.reporter_field.value = reporter.display_name

        self.issue_created_date_field.value = datetime.strftime(response.created, '%Y-%m-%d %H:%M')
        self.issue_key_field.value = response.key
        self.project_id_field.value = f'({response.project.key}) {response.project.name}'
        self.issue_type_field.value = response.work_item_type_name
        self.issue_parent_field.value = response.parent_key
        self.issue_sprint_field.value = response.sprint_name

        self.issue_summary_field.value = response.summary
        self.issue_summary_field.update_enabled = editable_fields.get(
            self.issue_summary_field.jira_field_key
        )

        self.issue_due_date_field.value = response.display_due_date
        self.issue_due_date_field.update_enabled = editable_fields.get(
            self.issue_due_date_field.jira_field_key
        )

        # update the priority selection depending on whether the issue supports prioritization
        self._setup_priority_selector(response.edit_meta, response.priority)

        # set up time tracking widgets
        self._setup_time_tracking(response.time_tracking)

        # set up the labels; if any exists
        if response.labels:
            self.work_item_labels_widget.value = ','.join(response.labels)
        self.work_item_labels_widget.update_enabled = editable_fields.get(
            self.work_item_labels_widget.jira_field_key
        )
