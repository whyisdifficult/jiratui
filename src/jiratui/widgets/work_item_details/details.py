import asyncio
from datetime import datetime
from typing import Any, cast

from dateutil import parser  # type:ignore[import-untyped]
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalGroup, ItemGrid, Right, Vertical, VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import ProgressBar, Select
from textual.widgets._select import SelectOverlay

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.exceptions import UpdateWorkItemException, ValidationError
from jiratui.models import IssuePriority, JiraIssue, JiraUser, TimeTracking
from jiratui.utils.work_item_updates import (
    work_item_assignee_has_changed,
    work_item_parent_has_changed,
    work_item_priority_has_changed,
)
from jiratui.widgets.base import ReadOnlyTextField
from jiratui.widgets.common import (
    ADFTextAreaWidget,
    DateInputWidget,
    DateTimeInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    SelectionWidget,
    TextInputWidget,
    URLWidget,
    UserPickerWidget,
)
from jiratui.widgets.common.base_fields import LabelsAutoComplete
from jiratui.widgets.work_item_details.factory import create_dynamic_widgets_for_updating_work_item
from jiratui.widgets.work_item_details.fields import (
    IssueDetailsAssigneeSelection,
    IssueDetailsPrioritySelection,
    IssueDetailsStatusSelection,
    IssueKeyField,
    IssueParentField,
    IssueSprintField,
    IssueSummaryField,
    IssueTypeField,
    ProjectIDField,
    ReporterField,
    TimeTrackingWidget,
    WorkItemDetailsDueDate,
    WorkItemFlagField,
    WorkItemLabelsField,
)
from jiratui.widgets.work_item_details.flag_work_item import FlagWorkItemScreen
from jiratui.widgets.work_item_details.work_log import (
    LogWorkScreen,
    WorkItemWorkLogScreen,
)


class DynamicFieldsWidgets(ItemGrid):
    pass


class StaticFieldsWidgets(ItemGrid):
    pass


class IssueDetailsWidget(Vertical):
    """Implements a form to allow the user to view and edit some of the fields associated to a work item.

    The list of fields that can be updated are fixed:
    - Summary
    - Assignee
    - Status
    - Priority
    - Due Date
    - Labels
    - Parent
    - Flagged (a custom field)
    - Components
    - (Some) Custom field types
    - (Some) System field types

    Whether these fields can be updated depends on the work item's edit metadata. Some work items disallow editing
    certain fields. For example, work items of type "subtask" typically do not allow the user to update the due date.
    """

    HELP = 'See Updating Work Items section in the help'
    issue: Reactive[JiraIssue | None] = reactive(None, always_update=True)
    """Reactive variable that contains the work item currently being displayed."""
    clear_form: Reactive[bool] = reactive(False, always_update=True)
    """Reactive variable to clear the fields in the form."""

    BINDINGS = [
        ('ctrl+s', 'save_work_item', 'Save'),
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
            action='view_worklog',
            description='Worklog',
            show=True,
        ),
        Binding(
            key='ctrl+t',
            action='log_work',
            description='Log Work',
            show=True,
        ),
        Binding(
            key='ctrl+f',
            action='flag_work_item',
            description='Flag It',
            show=True,
        ),
    ]

    def __init__(self):
        super().__init__(id='issue_details')
        self.available_users: list[tuple[str, str]] | None = None
        self.can_focus = True
        self._work_item_is_flagged = None
        """Indicates whether the issue contains a flag, i.e. it has been flagged."""
        self._issue_supports_flagging = True
        """Indicates whether adding/removing a flag to a work item is supported. This depends on the issue's
        metadata or the configuration of the field used for storing the value of the flag."""

    @property
    def issue_is_flagged(self) -> bool:
        return self._work_item_is_flagged

    @property
    def help_anchor(self) -> str:
        return '#updating-work-items'

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
    def time_tracking_widget(self) -> TimeTrackingWidget:
        return self.query_one(TimeTrackingWidget)

    @property
    def work_item_labels_widget(self) -> WorkItemLabelsField:
        return self.query_one(WorkItemLabelsField)

    @property
    def issue_resolution_date_field(self) -> ReadOnlyTextField:
        return self.query_one('#issue_resolution_date', expect_type=ReadOnlyTextField)

    @property
    def time_tracking_container(self) -> HorizontalGroup:
        return self.query_one('#time-tracking-container', expect_type=HorizontalGroup)

    @property
    def work_item_flag_widget(self) -> WorkItemFlagField:
        return self.query_one(WorkItemFlagField)

    @property
    def dynamic_fields_widgets_container(self) -> DynamicFieldsWidgets:
        return self.query_one(DynamicFieldsWidgets)

    def compose(self) -> ComposeResult:
        with Right():
            yield WorkItemFlagField()  # row 0
        with VerticalScroll(id='issue-details-form'):
            with StaticFieldsWidgets():
                yield IssueSummaryField()  # row 1
                yield IssueDetailsAssigneeSelection([])  # row 2
                yield IssueDetailsPrioritySelection([])  # row 2
                yield IssueDetailsStatusSelection([])  # row 2
                yield IssueKeyField()  # row 3
                yield IssueParentField()  # row 3
                yield IssueSprintField()  # row 3
                yield ProjectIDField()  # row 4
                yield IssueTypeField()  # row 5
                yield ReporterField()  # row 5
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
                yield HorizontalGroup(id='time-tracking-container', classes='cols-3')
            yield DynamicFieldsWidgets()

    def on_mount(self) -> None:
        """Initialize the labels autocomplete widget after mounting."""
        # Get the labels field and create an autocomplete widget for it
        labels_field = self.work_item_labels_widget
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821

        # Create and mount the autocomplete widget
        autocomplete = LabelsAutoComplete(
            target=labels_field,
            api_controller=application.api,
            required=False,
            title='Labels',
        )
        self.mount(autocomplete)

    def action_focus_widget(self, key: str) -> None:
        """Focuses a widget depending on the key pressed.

        This will only focus the following widgets:
        - assignee_selector (key `x`)
        - priority_selector (key `y`)
        - issue_status_selector (key `z`)

        Args:
            key: the key that was pressed.

        Returns:
            `None`.
        """
        if key == 'x':
            self.screen.set_focus(self.assignee_selector)
        elif key == 'y':
            self.screen.set_focus(self.priority_selector)
        elif key == 'z':
            self.screen.set_focus(self.issue_status_selector)

    def action_flag_work_item(self) -> None:
        """Opens a modal screen to let the user add/remove a flag with an optional comment/note."""

        if self.issue and self.issue.key and self._issue_supports_flagging:
            self.app.push_screen(
                FlagWorkItemScreen(self.issue.key, self.issue_is_flagged),
                self._request_flagging_work_item,
            )
        else:
            self.notify(
                'Flagging this issue is not supported.', severity='warning', title='Flag Work Item'
            )

    def _request_flagging_work_item(self, value: dict | None = None) -> None:
        """If we need to update the flag run a worker to do so."""

        if value and value.get('update_flag'):
            self.run_worker(self._toggle_work_item_flag(key=self.issue.key, note=value.get('note')))

    async def _toggle_work_item_flag(self, key: str, note: str | None = None) -> None:
        """Toggles the flag of the work item."""

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.update_issue_flagged_status(
            issue_id_or_key=key,
            note=note,
            add_flag=not self.issue_is_flagged,
        )
        if response.success:
            self.notify('Work item flagged successfully', title='Update Work Item')
            # refresh the details of the work item to reflect the changes in time tracking information
            await self._refresh_work_item_details()
        else:
            self.notify(
                f'Failed to flag the item: {response.error}',
                severity='error',
                title='Update Work Item',
            )

    def action_view_worklog(self) -> None:
        """Opens a pop-up modal to display the work log of a work item.

        Returns:
            `None`.
        """
        if self.issue:
            self.app.push_screen(
                WorkItemWorkLogScreen(self.issue.key), self._handle_worklog_screen_dismissal
            )

    def action_log_work(self) -> None:
        """Opens a pop-up modal to allow the user to log work for the current work item.

        Returns:
            `None`.
        """
        if self.issue:
            current_remaining_estimate = None
            if self.issue.time_tracking:
                current_remaining_estimate = self.issue.time_tracking.remaining_estimate
            self.app.push_screen(
                LogWorkScreen(self.issue.key, current_remaining_estimate),
                self._request_adding_worklog,
            )

    def _handle_worklog_screen_dismissal(self, response: dict | None = None) -> None:
        # when the screen that shows work logs for a work item is dismissed, check the result and if
        # required fetch the details of the work item to refresh the details form and reflect the changes in time
        # tracking information
        if response.get('work_logs_deleted'):
            self.run_worker(self._refresh_work_item_details)

    async def _refresh_work_item_details(self) -> None:
        """Fetches the details of the work item to retrieve the latest changes and update the details form.

        This is useful for operations that update the details, e.g. saving the work item's details or, deleting a
        worklog."""

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        issue_details_response = await application.api.get_issue(issue_id_or_key=self.issue.key)
        if issue_details_response.success and issue_details_response.result:
            self.issue = issue_details_response.result.issues[0]

    def _request_adding_worklog(self, data: dict) -> None:
        """Requests a worker to attempt to log work for the currently-selected item.

        Args:
            data: the data returned by the modal screen after the user clicks the "save" button.

        Returns:
            `None`.
        """
        self.run_worker(
            self._add_worklog(
                time_spent=data.get('time_spent'),
                time_remaining=data.get('time_remaining'),
                description=data.get('description'),
                started=data.get('started'),
                current_remaining_estimate=data.get('current_remaining_estimate'),
            )
        )

    async def _add_worklog(
        self,
        time_spent: str,
        started: str,
        time_remaining: str | None = None,
        description: str | None = None,
        current_remaining_estimate: str | None = None,
    ) -> None:
        """Logs work for the currently-selected item.

        Args:
            time_spent: the time spent on the task. E.g. 1w 1d
            time_remaining: the time remaining in the task. E.g. 1w 1d
            description: an optional description of the work done in the task.
            started: the date/time on which the work was started.
            current_remaining_estimate: the current remaining estimate of the task.

        Return:
            `None`
        """

        if not time_spent:
            # this should not happen but if for some reason it does then make sure to let the user know that we can't
            # add the worklog
            self.notify(
                'You need to provide the time spent on the task to log work', title='Worklog'
            )
        else:
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            response: APIControllerResponse = await application.api.add_work_item_worklog(
                issue_key_or_id=self.issue.key,
                started=parser.parse(f'{started}Z') if started else None,
                time_spent=time_spent,
                time_remaining=time_remaining,
                comment=description,
                current_remaining_estimate=current_remaining_estimate,
            )
            if response.success:
                self.notify('Work logged successfully', title='Worklog')
                # refresh the details of the work item to reflect the changes in time tracking information
                await self._refresh_work_item_details()
            else:
                self.notify(
                    f'Failed to log work for the item: {response.error}',
                    severity='error',
                    title='Worklog',
                )

    def _update_priority_selection(self, priorities, priority_id: str) -> None:
        for priority in priorities or []:
            if priority[1] == priority_id:
                self.priority_selector.value = priority_id
                return

    def _setup_priority_selector(
        self, issue_edit_meta: dict | None, issue_priority: IssuePriority
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
            self.issue_due_date_field.set_original_value(None)
            self.work_item_labels_widget.value = ''
            self._work_item_is_flagged = None
            self._issue_supports_flagging = True
            self.work_item_flag_widget.show = False

    def _setup_time_tracking(self, time_tracking_data: TimeTracking) -> None:
        self.time_tracking_container.remove_children(TimeTrackingWidget)

        if not time_tracking_data:
            return

        self.time_tracking_container.mount(
            TimeTrackingWidget(
                time_tracking_data.original_estimate,
                time_tracking_data.time_spent,
                time_tracking_data.remaining_estimate,
                time_tracking_data.original_estimate_seconds,
                time_tracking_data.time_spent_seconds,
                time_tracking_data.remaining_estimate_seconds,
            )
        )

    def _build_payload_for_update(self) -> dict:
        # maps field id to field value
        payload: dict[str, Any] = {}
        # process the "static" fields
        if self.issue_summary_field.update_enabled:
            # check if the summary is not empty and has changed
            if (
                summary := self.issue_summary_field.validated_summary
            ) and summary != self.issue.summary:
                payload[self.issue_summary_field.jira_field_key] = summary

        if self.issue_due_date_field.update_enabled:
            # check if the due date has changed using the widget's built-in change detection
            if self.issue_due_date_field.value_has_changed:
                payload[self.issue_due_date_field.jira_field_key] = (
                    self.issue_due_date_field.get_value_for_update()
                )

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
                    payload[self.priority_selector.jira_field_key] = (
                        self.priority_selector.selection
                    )

        if self.issue_parent_field.update_enabled:
            if work_item_parent_has_changed(
                self.issue.parent_issue_key, self.issue_parent_field.value
            ):
                payload[self.issue_parent_field.jira_field_key] = self.issue_parent_field.value

        if self.assignee_selector.update_enabled:
            # check if the assignee has changed
            if work_item_assignee_has_changed(
                self.issue.assignee, self.assignee_selector.selection
            ):
                # TODO replace with self.assignee_selector.jira_field_key
                payload['assignee_account_id'] = self.assignee_selector.selection

        if self.work_item_labels_widget.update_enabled:
            # update the issue's labels - strip whitespace and remove internal spaces
            labels: list[str] = (
                [
                    label.strip().replace(' ', '')
                    for label in self.work_item_labels_widget.value.split(',')
                    if label.strip() and label.strip() != '-'
                ]
                if self.work_item_labels_widget.value
                else []
            )

            current_labels: list[str] = list(self.issue.labels or [])
            # Case-insensitive comparison, but preserve original case
            if {lbl.lower() for lbl in labels} != {lbl.lower() for lbl in current_labels}:
                # update the list of labels (empty list will remove all labels)
                payload[self.work_item_labels_widget.jira_field_key] = labels

        # process dynamically-generated field widgets; e.g. additional system fields and custom fields
        if CONFIGURATION.get().enable_updating_additional_fields:
            # process the "dynamic" fields, which include custom and system fields
            for dynamic_widget in self.dynamic_fields_widgets_container.children:
                if (
                    not isinstance(dynamic_widget, NumericInputWidget)
                    and not isinstance(dynamic_widget, DateInputWidget)
                    and not isinstance(dynamic_widget, DateTimeInputWidget)
                    and not isinstance(dynamic_widget, SelectionWidget)
                    and not isinstance(dynamic_widget, URLWidget)
                    and not isinstance(dynamic_widget, MultiSelectWidget)
                    and not isinstance(dynamic_widget, TextInputWidget)
                    and not isinstance(dynamic_widget, LabelsWidget)
                    and not isinstance(dynamic_widget, UserPickerWidget)
                ):
                    continue
                if dynamic_widget.value_has_changed:
                    value_for_update = dynamic_widget.get_value_for_update()

                    # Handle float fields - ensure value is valid before assignment
                    if isinstance(dynamic_widget, NumericInputWidget):
                        # NumericInputWidget should handle float conversion, but ensure it's not None
                        if value_for_update is not None:
                            payload[dynamic_widget.jira_field_key] = value_for_update
                    else:
                        payload[dynamic_widget.jira_field_key] = value_for_update
        return payload

    async def action_save_work_item(self) -> None:
        """Updates the fields of a work item that have changed.

        Returns:
            `None`.
        """

        if not self.issue:
            self.notify('You must select a work item before saving changes')
            return

        issue_was_updated: bool = False
        # build the payload with the fields that will be updated
        payload: dict = self._build_payload_for_update()
        # check if we need to transition the issue and move it to the new status if needed
        issue_requires_transition = (
            self.issue_status_selector.selection is not None
            and self.issue_status_selector.selection != self.issue.status.id
        )

        if not payload and not issue_requires_transition:
            self.notify('Nothing to update.', title='Update Work Item')
            return

        # attempt to update the issue
        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        if payload:
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
                    issue_was_updated = True
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

        if issue_requires_transition:
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
                issue_was_updated = True
                self.notify(
                    'Successfully transitioned the work item to a different status.',
                    title='Update Work Item',
                )

        if issue_was_updated:
            # fetch the issue again to retrieve the latest changes and update the form
            await self._refresh_work_item_details()

    @staticmethod
    def _determine_editable_fields(work_item: JiraIssue) -> dict:
        """Determines which of fields of a work item that can be updated via the details form support updates based on
        the work item's edit metadata.

        Args:
            work_item: the work item to check.

        Returns:
            A dictionary with the ID of the fields that support updates. If a field does not support updates then the
            app will not allow the user to update its value.
        """

        work_item_edit_metadata: dict | None = work_item.edit_meta
        if not work_item_edit_metadata:
            return {}

        if not (fields := work_item_edit_metadata.get('fields', {})):
            return {}

        # if a field does nto have edit metadata then we assume we can not edit its value
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

        if field_parent := fields.get('parent', {}):
            if work_item.issue_type.hierarchy_level == 1:
                # we assume that this is work item whose type is at the top of the issue types hierarchy thus it
                # can not have parent items
                editable_fields[field_parent.get('key')] = False
            else:
                editable_fields[field_parent.get('key')] = 'set' in field_parent.get(
                    'operations', {}
                )

        if field_assignee := fields.get('assignee', {}):
            editable_fields[field_assignee.get('key')] = 'set' in field_assignee.get(
                'operations', {}
            )

        if field_labels := fields.get('labels', {}):
            editable_fields[field_labels.get('key')] = 'set' in field_labels.get('operations', {})

        if field_components := fields.get('components', {}):
            editable_fields[field_components.get('key')] = 'set' in field_components.get(
                'operations', {}
            )

        # Include custom fields (fields starting with 'customfield_')
        for field_id, field_meta in fields.items():
            if field_id.startswith('customfield_') and field_id not in editable_fields:
                editable_fields[field_meta.get('key')] = 'set' in field_meta.get('operations', {})

        return editable_fields

    @staticmethod
    def _generate_assignable_users_for_dropdown(
        users: list[JiraUser] | None = None,
        current_assignee: JiraUser | None = None,
        default_assignable_users: list[tuple[str, str]] | None = None,
    ) -> list[tuple[str, str]]:
        assignable_users: set[str] = set()
        selectable_users: list[tuple[str, str]] = []
        for user in users or []:
            if user.account_id:
                selectable_users.append((user.display_name, user.account_id))
                assignable_users.add(user.account_id)

        if not selectable_users:
            selectable_users = default_assignable_users
            for selectable_user in selectable_users:
                assignable_users.add(selectable_user[1])

        if current_assignee and current_assignee.account_id not in assignable_users:
            selectable_users.append((current_assignee.display_name, current_assignee.account_id))

        return selectable_users

    async def _retrieve_users_assignable_to_work_item(
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
        # fetch the list of users that can be assigned to the current issue
        response: APIControllerResponse = await application.api.search_users_assignable_to_issue(
            issue_key=work_item_key
        )
        # generate the list of users for the dropdown menu
        selectable_users: list[tuple[str, str]] = self._generate_assignable_users_for_dropdown(
            response.result,
            current_assignee,
            self.available_users,
        )

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

    async def _retrieve_applicable_status_codes(
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

    def watch_issue(self, work_item: JiraIssue | None) -> None:
        """Updates the form fields associated to a work item with the details of the work item.

        Args:
            work_item: a work item selected by the user in the left-hand side panel.

        Returns:
            `None`.
        """

        # "reset" the form by setting the value of all its elements to the default
        self.clear_form = True

        if not work_item:
            return

        # fetch the list of status codes applicable for this work item and its type
        self.run_worker(
            self._retrieve_applicable_status_codes(
                work_item.project.key, work_item.issue_type.id, str(work_item.status.id)
            )
        )

        # check which of the fields in the details form can be updated; diable the widgets of those that do not support
        # updates
        editable_fields: dict = self._determine_editable_fields(work_item)

        # fetch the list of assignable users for the work item
        self.run_worker(
            self._retrieve_users_assignable_to_work_item(
                work_item.key,
                work_item.assignee,
                editable_fields.get(self.assignee_selector.jira_field_key),
            )
        )

        # set the value fo the form fields based on the work item's data
        if work_item.resolution_date:
            self.issue_resolution_date_field.value = datetime.strftime(
                work_item.resolution_date, '%Y-%m-%d %H:%M'
            )
        if work_item.resolution:
            self.issue_resolution_field.value = work_item.resolution
        if work_item.updated:
            self.issue_last_update_date_field.value = datetime.strftime(
                work_item.updated, '%Y-%m-%d %H:%M'
            )
        if reporter := work_item.reporter:
            self.reporter_field.value = reporter.display_name

        self.issue_created_date_field.value = datetime.strftime(work_item.created, '%Y-%m-%d %H:%M')
        self.issue_key_field.value = work_item.key
        self.project_id_field.value = f'({work_item.project.key}) {work_item.project.name}'
        self.issue_type_field.value = work_item.work_item_type_name
        # set the value of the parent field and determine if it can be edited
        self.issue_parent_field.value = work_item.parent_key
        self.issue_parent_field.update_enabled = editable_fields.get(
            self.issue_parent_field.jira_field_key
        )
        self.issue_sprint_field.value = work_item.sprint_name
        self.issue_summary_field.value = work_item.summary
        self.issue_summary_field.update_enabled = editable_fields.get(
            self.issue_summary_field.jira_field_key
        )

        # Set both original value and current value for proper change tracking
        self.issue_due_date_field.set_original_value(work_item.display_due_date)
        self.issue_due_date_field.update_enabled = editable_fields.get(
            self.issue_due_date_field.jira_field_key
        )
        # update the priority selection depending on whether the issue supports prioritization
        self._setup_priority_selector(work_item.edit_meta, work_item.priority)
        # set up time tracking widgets
        self._setup_time_tracking(work_item.time_tracking)
        # set up the labels; if any exists
        if work_item.labels:
            self.work_item_labels_widget.value = ','.join(work_item.labels)
        self.work_item_labels_widget.update_enabled = editable_fields.get(
            self.work_item_labels_widget.jira_field_key
        )

        # check if the work item has been flagged; and show a label at the top with a message for the user
        self.run_worker(self._determine_issue_flagged_status(work_item))

        if CONFIGURATION.get().enable_updating_additional_fields:
            # add dynamic widgets to support updating additional fields including custom fields and other system fields
            self.run_worker(self._add_dynamic_fields_widgets(work_item, editable_fields))

    async def _add_dynamic_fields_widgets(
        self, work_item: JiraIssue, editable_fields: dict
    ) -> None:
        """Builds and mounts a list of (dynamic) widgets to support updating (some) system and custom field types

        Args:
            work_item: the work item.

        Returns:
            None; updates the `DynamicFieldsWidgets` widget.
        """
        config = CONFIGURATION.get()

        # Get filter configuration
        ignore_filter_ids = config.update_additional_fields_ignore_ids

        await self.dynamic_fields_widgets_container.remove_children()
        if dynamic_widgets := create_dynamic_widgets_for_updating_work_item(
            work_item,
            ignore_filter_ids=ignore_filter_ids,
        ):
            # Sort widgets so ADFTextAreaWidget instances appear last
            # This ensures TEXTAREA fields with rendered markdown are displayed at the bottom
            adf_textarea_widgets = [w for w in dynamic_widgets if isinstance(w, ADFTextAreaWidget)]
            other_widgets = [w for w in dynamic_widgets if not isinstance(w, ADFTextAreaWidget)]
            sorted_widgets = other_widgets + adf_textarea_widgets

            await self.dynamic_fields_widgets_container.mount(*sorted_widgets)
            # Wait for widgets to be fully composed before populating
            # This ensures SelectOverlay is ready in UserPickerWidget
            await asyncio.sleep(0)
            await self._populate_user_picker_widgets(work_item, editable_fields)

    async def _populate_user_picker_widgets(
        self, work_item: JiraIssue, editable_fields: dict
    ) -> None:
        """Populates user picker custom fields with assignable users for the work item.

        Uses the same API and fallback logic as the assignee field to ensure consistency.
        Each user picker widget is populated with users that can be assigned to the specific issue,
        and the current value is preserved even if not in the assignable list.

        Args:
            work_item: the work item being displayed.
            editable_fields: dict of field keys to their editable status.

        Returns:
            Nothing.
        """

        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        user_picker_widgets = self.query(UserPickerWidget)

        if not user_picker_widgets:
            return

        # Fetch the list of users that can be assigned to the current issue (same as assignee)
        response: APIControllerResponse = await application.api.search_users_assignable_to_issue(
            issue_key=work_item.key
        )

        # Process each user picker widget
        for user_picker in user_picker_widgets:
            # Wait for the widget to be fully composed with SelectOverlay
            # This prevents NoMatches errors when calling set_options
            max_retries = 10
            for _ in range(max_retries):
                try:
                    # Try to query for SelectOverlay - if it exists, widget is ready
                    user_picker.query_one(SelectOverlay)
                    break
                except Exception:
                    # Widget not ready yet, wait a bit
                    await asyncio.sleep(0.05)
            else:
                # Widget never became ready, skip it
                continue

            # Get current user value for this field (use pending_value which was extracted in factory)
            current_user_value = user_picker.pending_value

            selectable_users: list[tuple[str, str]] = self._generate_assignable_users_for_dropdown(
                response.result,
                None,  # We don't have a JiraUser object, we'll handle current value separately
                self.available_users,
            )

            if selectable_users:
                if current_user_value:
                    user_ids = [user[1] for user in selectable_users]
                    if current_user_value not in user_ids:
                        for user in response.result or []:
                            if user.account_id == current_user_value:
                                selectable_users.append((user.display_name, user.account_id))
                                break
                        else:
                            selectable_users.append((current_user_value, current_user_value))

                user_picker.set_options(selectable_users)
                if current_user_value:
                    user_picker.value = current_user_value
                user_picker.update_enabled = editable_fields.get(user_picker.jira_field_key)
            else:
                if current_user_value:
                    user_picker.set_options([(current_user_value, current_user_value)])
                    user_picker.value = current_user_value
                    user_picker.update_enabled = editable_fields.get(user_picker.jira_field_key)
                else:
                    user_picker.update_enabled = False

    async def _determine_issue_flagged_status(self, issue: JiraIssue) -> None:
        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        # retrieve the configuration of all the supported fields
        response: APIControllerResponse = await application.api.get_fields('flagged')
        if not response.success or not response.result:
            # we won't be able to find the key of the field that we need to update in order to set/remove a flag;
            # let's disable flagging for the issue
            self._issue_supports_flagging = False
            self.notify(
                'Unable to flag the work item. Missing fields configuration',
                severity='error',
                title='Flag Work Item',
            )
        else:
            # extract the key of the field used for flagging items based on the name of the field
            work_item_flag: Any = issue.get_custom_field_value(response.result[0].id)  # type:ignore
            self._work_item_is_flagged = True if work_item_flag else False
            self.work_item_flag_widget.show = self.issue_is_flagged
