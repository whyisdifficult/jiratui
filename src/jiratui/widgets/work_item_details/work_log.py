import dataclasses
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import re
from typing import cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ItemGrid, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.widgets import (
    Button,
    Collapsible,
    DataTable,
    Footer,
    Input,
    Label,
    Markdown,
    Static,
    TextArea,
)

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import (
    JiraIssue,
    JiraIssueSearchResponse,
    JiraWorklog,
    PaginatedJiraWorklog,
    TimeTracking,
)
from jiratui.utils.urls import build_external_url_for_work_log
from jiratui.widgets.base import DateInput
from jiratui.widgets.work_item_details.fields import TimeTrackingWidget


class LogWorkScreenMode(Enum):
    """The modes supported by the screen that allows users to add/update work log entries."""

    CREATE = 'create'
    UPDATE = 'update'


@dataclass()
class LogWorkScreenResult:
    """The data returned by the screen that allows users to add/update work log entries."""

    work_item_key: str
    mode: LogWorkScreenMode
    time_spent: str
    started: str
    time_remaining: str | None = None
    description: str | None = None
    worklog_id: str | None = None


class WorkLogCollapsible(Collapsible):
    """A collapsible widget to display information of a worklog and to handle opening the worklog details in the
    browser and deleting work logs.

    This widget is responsible for:
    - posting a message [LogEntryDeleted](#jiratui.widgets.work_item_details.work_log.WorkLogCollapsible.LogEntryDeleted)
    when a worklog entry is deleted after the user presses `d`.
    - opening the screen [LogWorkScreen](#jiratui.widgets.work_item_details.work_log.LogWorkScreen) to allow the user to
    update a worklog entry after the user presses `^e`.
    - posting a message [UpdateLogEntry](#jiratui.widgets.work_item_details.work_log.WorkLogCollapsible.UpdateLogEntry)
    when the user wants to update a worklog entry. The handler will take care of making the update.
    - opening a worklog entry's URL in the browser when the user presses `^o`.
    """

    BINDINGS = [
        Binding(
            key='ctrl+o',
            action='open_in_browser',
            description='Browse',
            show=True,
        ),
        Binding(
            key='d',
            action='delete_worklog',
            description='Delete',
            show=True,
        ),
        Binding(
            key='ctrl+e',
            action='edit_worklog_entry',
            description='Edit',
            show=True,
        ),
    ]

    @dataclass
    class LogEntryDeleted(Message):
        """A message to request the handler to delete a worklog entry."""

        worklog_id: str

    @dataclass
    class UpdateLogEntry(Message):
        """A message to request the handler to update a worklog entry."""

        worklog_id: str
        work_item_key: str
        time_spent: str
        time_remaining: str
        started: str
        description: str | None = None
        mode: LogWorkScreenMode = LogWorkScreenMode.UPDATE

        def as_dict(self) -> dict:
            return dataclasses.asdict(self)

    def __init__(self, *args, **kwargs):
        self._url = kwargs.pop('url')
        self._worklog_id: str = kwargs.pop('worklog_id')
        self._work_item_key = kwargs.pop('work_item_key')
        self._worklog_time_spent = kwargs.pop('worklog_time_spent', '') or ''
        self._worklog_date_started = kwargs.pop('worklog_date_started', '') or ''
        self._worklog_time_remaining = kwargs.pop('worklog_time_remaining', '') or ''
        self._worklog_description = kwargs.pop('worklog_description', '') or ''
        super().__init__(*args, **kwargs)

    def action_open_in_browser(self) -> None:
        """Opens the worklog in the default browser."""

        if self._url:
            self.app.open_url(self._url)

    def action_delete_worklog(self):
        """Posts a message to request deleting a work log entry."""

        if self._worklog_id:
            self.post_message(self.LogEntryDeleted(self._worklog_id))

    def action_edit_worklog_entry(self) -> None:
        """Opens a [LogWorkScreen](#jiratui.widgets.work_item_details.work_log.WorkLogCollapsible.LogWorkScreen) to
        allow the user to update a log entry.

        Returns:
            None
        """

        if self._worklog_id and self._work_item_key:
            self.app.push_screen(
                LogWorkScreen(
                    self._work_item_key,
                    mode=LogWorkScreenMode.UPDATE,
                    worklog_id=self._worklog_id,
                    current_time_spent=self._worklog_time_spent,
                    current_date_started=self._worklog_date_started,
                    current_remaining_estimate=self._worklog_time_remaining,
                    current_description=self._worklog_description,
                ),
                callback=self._edit_worklog_entry,
            )

    async def _edit_worklog_entry(self, data: LogWorkScreenResult | None) -> None:
        if data:
            self.post_message(
                self.UpdateLogEntry(
                    mode=data.mode,
                    work_item_key=self._work_item_key,
                    worklog_id=self._worklog_id,
                    time_spent=data.time_spent,
                    time_remaining=data.time_remaining,
                    started=data.started,
                    description=data.description,
                )
            )


class WorkItemWorkLogScreen(Screen[dict]):
    """A screen that displays the work logs of a work item.

    This screen is responsible for:

    - fetching the logs associated to the selected work item and displaying them.
    - optionally fetching the work item's current remaining time estimate; the data is not passed to the screen.
    - allowing the user to add and delete work logs.
    - opening the screen [LogWorkScreen](#jiratui.widgets.work_item_details.work_log.LogWorkScreen) when the user
    presses `n` to add a new log entry.
    - handling the message [UpdateLogEntry](#jiratui.widgets.work_item_details.work_log.WorkLogCollapsible.UpdateLogEntry)
    when the user updates a log entry.
    - handling the message [LogEntryDeleted](#jiratui.widgets.work_item_details.work_log.WorkLogCollapsible.LogEntryDeleted)
    when the user deletes a log entry.

    The screen can be dismissed with dictionary. This dict can contain a key called `work_logs_deleted` to indicate to
    the caller that at least 1 worklog has been deleted. This lets the caller refresh the work item (if needed) to
    reflect the changes to the remaining time estimate.
    """

    HELP = 'See Worklogs section in the help'
    BINDINGS = [
        ('escape', 'close_screen', 'Close'),
        Binding(
            key='n',
            action='log_work',
            description='Log Work',
            show=True,
        ),
    ]
    TITLE = 'Worklog'

    def __init__(self, work_item_key: str, time_tracking: TimeTracking | None = None):
        super().__init__()
        self._work_item_key = work_item_key
        self._work_item_time_tracking = time_tracking
        self._worklog_counter = 0
        self._worklog_total_count = 0
        # True when at least 1 work log was deleted; useful for refreshing the details of the work item after this
        # screen is dismissed
        self._work_logs_deleted = False
        self._log_entries: dict[str, WorkLogCollapsible] = {}

    @property
    def help_anchor(self) -> str:
        return '#worklogs'

    @property
    def work_log_items_container(self) -> VerticalScroll:
        return self.query_one(VerticalScroll)

    @property
    def root_container(self) -> Vertical:
        return self.query_one(Vertical)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = f'{self.TITLE} - {self._work_item_key}'
        with vertical:
            yield Horizontal(id='time-tracking-container', classes='time-tracking-container')
            yield VerticalScroll()
        yield Footer(show_command_palette=False, compact=True)

    def on_mount(self) -> None:
        if self._work_item_key:
            self.run_worker(self._fetch_work_logs())

    async def _fetch_work_logs(self, fetch_time_tracking: bool = False) -> None:
        """Retrieves the work log data associated to a work item and updates the details in the screen.

        This sends a request to the Jira API to retrieve the worklog details of the work item. If the work item has
        worklog entries then this method will build a dictionary of
        [WorkLogCollapsible](#jiratui.widgets.work_item_details.work_log.WorkLogCollapsible) and mounts the values on
        the screen.

        This method also update the counters displayed in the container's border's subtitle.

        Returns:
            None
        """

        await self.work_log_items_container.remove_children(WorkLogCollapsible)
        self._log_entries = {}

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821

        if self._work_item_time_tracking is None or fetch_time_tracking:
            # fetch the work item's time tracking information
            work_item_response: APIControllerResponse = await application.api.get_issue(
                issue_id_or_key=self._work_item_key,
            )
            if not work_item_response.success or not work_item_response.result:
                self.notify(
                    f'Unable to find the work item with key {self._work_item_key}',
                    title='Not Found',
                    severity='warning',
                )
            else:
                work_item_result: JiraIssueSearchResponse = work_item_response.result
                work_item: JiraIssue = work_item_result.issues[0]
                self._work_item_time_tracking = work_item.time_tracking

        # set time tracking
        self.call_next(self._set_time_tracking_information)

        # retrieve the work logs of the item
        response: APIControllerResponse = await application.api.get_work_item_worklog(
            self._work_item_key
        )
        result: PaginatedJiraWorklog
        if response.success and (result := response.result):
            self._worklog_counter = len(result.logs)
            self._worklog_total_count = result.total
            self._update_subtitle()

            worklog: JiraWorklog
            for worklog in result.logs:
                self._log_entries[worklog.id] = self._build_work_log_collapsible(worklog)

            await self.work_log_items_container.mount_all(self._log_entries.values())

    async def _set_time_tracking_information(self) -> None:
        container = self.query_one('#time-tracking-container', Horizontal)
        await container.remove_children(TimeTrackingWidget)
        await container.mount(
            TimeTrackingWidget(
                original_estimate=(
                    self._work_item_time_tracking.original_estimate
                    if self._work_item_time_tracking
                    else None
                ),
                original_estimate_seconds=(
                    self._work_item_time_tracking.original_estimate_seconds
                    if self._work_item_time_tracking
                    else None
                ),
                remaining_estimate=(
                    self._work_item_time_tracking.remaining_estimate
                    if self._work_item_time_tracking
                    else None
                ),
                remaining_estimate_seconds=(
                    self._work_item_time_tracking.remaining_estimate_seconds
                    if self._work_item_time_tracking
                    else None
                ),
                time_spent=self._work_item_time_tracking.time_spent
                if self._work_item_time_tracking
                else None,
                time_spent_seconds=(
                    self._work_item_time_tracking.time_spent_seconds
                    if self._work_item_time_tracking
                    else None
                ),
            )
        )

    def _update_subtitle(self, update_counters: bool = False) -> None:
        if update_counters:
            if self._worklog_counter > 0:
                self._worklog_counter -= 1
            if self._worklog_total_count > 0:
                self._worklog_total_count -= 1
        self.root_container.border_subtitle = (
            f'Showing {self._worklog_counter} of {self._worklog_total_count}'
        )

    def _build_work_log_collapsible(self, worklog: JiraWorklog) -> WorkLogCollapsible:
        url = build_external_url_for_work_log(self._work_item_key, worklog.id)

        work_log_details: DataTable = DataTable(
            cursor_type='row', show_header=False, classes='worklog-details-table'
        )
        work_log_details.add_columns(*('Property', 'Value'))
        work_log_details.add_rows(
            [
                (
                    Text('Time Spent', justify='right'),
                    Text(worklog.display_time_spent(), justify='left'),
                ),
                (
                    Text('Started', justify='right'),
                    Text(worklog.display_started(), justify='left'),
                ),
                (
                    Text('Author', justify='right'),
                    Text(worklog.display_author(), justify='left'),
                ),
                (
                    Text('Update Author', justify='right'),
                    Text(worklog.display_update_author(), justify='left'),
                ),
            ]
        )

        comment_widget: Markdown | Static
        if worklog.comment and (comment_text := worklog.get_comment()):
            comment_widget = Markdown(comment_text)
        elif worklog.comment:
            # this may happen if we fail to parse the ADF data for Jira Cloud API
            comment_widget = Static(
                Text(
                    'Unable to display the comment associated to the worklog.',
                    style='red italic',
                )
            )
        else:
            comment_widget = Static()

        return WorkLogCollapsible(
            comment_widget,
            work_log_details,
            title=worklog.display(),
            url=url or None,
            worklog_id=worklog.id,
            work_item_key=self._work_item_key,
            worklog_time_spent=worklog.time_spent,
            worklog_date_started=worklog.get_date_started(),
            worklog_time_remaining=(
                self._work_item_time_tracking.remaining_estimate
                if self._work_item_time_tracking
                else None
            ),
            worklog_description=worklog.get_comment(),
        )

    def action_close_screen(self) -> None:
        self.dismiss({'work_logs_deleted': self._work_logs_deleted})

    def action_log_work(self) -> None:
        if self._work_item_key:
            self.app.push_screen(
                LogWorkScreen(
                    self._work_item_key,
                    current_remaining_estimate=(
                        self._work_item_time_tracking.remaining_estimate
                        if self._work_item_time_tracking
                        else None
                    ),
                ),
                callback=self._log_work,
            )

    @on(WorkLogCollapsible.UpdateLogEntry)
    async def _request_log_entry_update(self, event: WorkLogCollapsible.UpdateLogEntry) -> None:
        await self._log_work(
            LogWorkScreenResult(
                work_item_key=self._work_item_key,
                mode=event.mode,
                time_spent=event.time_spent,
                started=event.started,
                description=event.description,
                time_remaining=event.time_remaining,
                worklog_id=event.worklog_id,
            )
        )
        event.stop()

    async def _log_work(self, data: LogWorkScreenResult):
        if data:
            if data.mode == LogWorkScreenMode.CREATE:
                await self._add_worklog_entry(work_item_key=self._work_item_key, data=data)
            elif data.mode == LogWorkScreenMode.UPDATE:
                await self._update_worklog_entry(worklog_id=data.worklog_id, data=data)

    async def _add_worklog_entry(self, work_item_key: str, data: LogWorkScreenResult) -> None:
        """Logs work for a work item.

        Return:
            None
        """

        if not work_item_key:
            self.notify('Select a work item before logging work.', title='Validation Error')
            return None

        if not data.time_spent:
            # this should not happen but if for some reason it does then make sure to let the user know that we can't
            # add the worklog
            self.notify(
                'You need to provide the time spent on the task to log work',
                title='Validation Error',
            )
            return None

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821

        started_datetime: datetime | None = None
        if data.started:
            naive_dt = datetime.fromisoformat(data.started)
            # assume the date/time value is in local time and convert to UTC
            started_datetime = naive_dt.replace(
                tzinfo=None
            ).astimezone()  # make it aware of local TZ as defined by the OS
            started_datetime = started_datetime.astimezone(timezone.utc)

        response: APIControllerResponse = await application.api.add_work_item_worklog(
            issue_key_or_id=self._work_item_key,
            started=started_datetime,
            time_spent=data.time_spent,
            time_remaining=data.time_remaining,
            comment=data.description,
            current_remaining_estimate=(
                self._work_item_time_tracking.remaining_estimate
                if self._work_item_time_tracking
                else None
            ),
        )
        if response.success:
            self.notify(f'Logged time to task {self._work_item_key}')
            # a new entry was added; update the time estimate of the work item and the list of logs in the screen
            await self._fetch_work_logs(fetch_time_tracking=True)
        else:
            self.notify(
                f'Failed to log time to task {self._work_item_key}: {response.error}',
                severity='error',
            )
        return None

    async def _update_worklog_entry(self, worklog_id: str, data: LogWorkScreenResult) -> None:
        """Attempts to update a work log entry using the Jira API.

        Returns:
            None
        """

        if not worklog_id:
            return None

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821

        started_datetime: datetime | None = None
        if data.started:
            naive_dt = datetime.fromisoformat(data.started)
            # assume the date/time value is in local time and convert to UTC
            started_datetime = naive_dt.replace(
                tzinfo=None
            ).astimezone()  # make it aware of local TZ as defined by the OS
            started_datetime = started_datetime.astimezone(timezone.utc)

        # request the API to update the worklog entry
        response: APIControllerResponse = await application.api.update_worklog(
            issue_key_or_id=self._work_item_key,
            worklog_id=worklog_id,
            started=started_datetime,
            time_spent=data.time_spent,
            time_remaining=data.time_remaining,
            comment=data.description,
            remaining_estimate=(
                self._work_item_time_tracking.remaining_estimate
                if self._work_item_time_tracking
                else None
            ),
        )

        if response.success:
            self.notify(f'Logged time to task {self._work_item_key}', title='Worklog')
            # an entry was updated; update the time estimate of the work item and the list of logs in the screen
            await self._fetch_work_logs(fetch_time_tracking=True)
        else:
            self.notify('There was an error updating the log entry', severity='error')
        return None

    @on(WorkLogCollapsible.LogEntryDeleted)
    def _delete_worklog_entry(self, event: WorkLogCollapsible.LogEntryDeleted) -> None:
        """Deletes a worklog.

        Args:
            event:

        Returns:

        """

        self.notify('Deleting worklog entry...')
        self.run_worker(self._delete_log_entry(event.worklog_id))
        event.stop()

    async def _delete_log_entry(self, worklog_id: str):
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.remove_worklog(
            self._work_item_key, worklog_id
        )
        if response.success:
            self.notify('Worklog deleted', title='Worklog')
            self._update_subtitle(True)
            self._work_logs_deleted = True
            await self._fetch_work_logs(fetch_time_tracking=True)
        else:
            self.notify(
                f'Failed to delete the worklog: {response.error}', title='Worklog', severity='error'
            )


class TimeSpentInput(Input):
    """An input field that contains a string representing the time spent by the user in a task."""

    def __init__(self, initial_value: str | None = None):
        super().__init__(
            value=initial_value or '',
            placeholder='E.g. 1w 1d',
            valid_empty=False,
            classes='required',
        )
        self.border_title = 'Time Spent'
        self.border_subtitle = '(*)'
        self.tooltip = 'Enter the amount of time you work on this task'


class TimeRemainingInput(Input):
    """An input field that contains a string representing the time remaining in a task."""

    def __init__(self, initial_value: str | None = None):
        super().__init__(value=initial_value or '', placeholder='E.g. 1d 1h 30m')
        self.border_title = 'Time Remaining'
        self.tooltip = 'Optionally, enter the time remaining in the task'


class LogDateTimeInput(DateInput):
    """An DateInput field that contains a string representing the date/time when the user did work on a task."""

    TEMPLATE = '9999-99-99 99:99'
    PLACEHOLDER = '2025-10-12 13:50'

    def __init__(self, initial_value: str | None = None):
        super().__init__(valid_empty=False)
        self.disabled = True
        self.border_title = 'Date Started'
        self.tooltip = 'Enter the date/time on which the work was done'
        self.value = initial_value or datetime.now().strftime('%Y-%m-%d %H:%M')


class WorkDescription(TextArea):
    """A textarea field that contains an optional comment for a work log entry."""

    def __init__(self, initial_value: str | None = None):
        super().__init__(text=initial_value or '')
        self.disabled = True
        self.border_title = 'Work Description'
        self.compact = True
        self.tooltip = 'Add an optional description'


class LogWorkScreen(Screen[LogWorkScreenResult | None]):
    """A modal screen that allow users to provide data for creating new work log entries or updating an existing entry.

    The screen's result is an instance of
    [LogWorkScreenResult](#jiratui.widgets.work_item_details.work_log.LogWorkScreenResult). The object contains the
    values to add or update a work log entry

    **See Also**:
    - [Use Case: Log Work](#use-case-log-work)
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
    ]

    def __init__(
        self,
        work_item_key: str,
        mode: LogWorkScreenMode = LogWorkScreenMode.CREATE,
        worklog_id: str | None = None,
        current_remaining_estimate: str | None = None,
        current_time_spent: str | None = None,
        current_date_started: str | None = None,
        current_description: str | None = None,
    ):
        super().__init__()
        self._work_item_key = work_item_key
        self._worklog_id = worklog_id
        self._current_remaining_estimate = current_remaining_estimate
        self._current_time_spent = current_time_spent
        self._current_date_started = current_date_started
        self._current_description = current_description
        self._mode = mode
        if self._mode == LogWorkScreenMode.UPDATE and not self._worklog_id:
            raise ValueError('Missing worklog Id for update.')

    @property
    def work_log_items_container(self) -> VerticalScroll:
        return self.query_one(VerticalScroll)

    @property
    def time_spent_input(self) -> TimeSpentInput:
        return self.query_one(TimeSpentInput)

    @property
    def time_remaining_input(self) -> TimeRemainingInput:
        return self.query_one(TimeRemainingInput)

    @property
    def log_date_time_input(self) -> LogDateTimeInput:
        return self.query_one(LogDateTimeInput)

    @property
    def work_description_input(self) -> WorkDescription:
        return self.query_one(WorkDescription)

    @property
    def save_button(self) -> Button:
        return self.query_one('#log-work-button-save', expect_type=Button)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = f'Log Work - {self._work_item_key}'
        with vertical:
            with ItemGrid(classes='log-work-time-input-grid'):
                yield TimeSpentInput(initial_value=self._current_time_spent)
                yield TimeRemainingInput(initial_value=self._current_remaining_estimate)
            with ItemGrid(classes='log-work-date-hint-grid'):
                yield LogDateTimeInput(initial_value=self._current_date_started)
                yield Label('w = week | d = day | h = hour | m = minutes')
            yield WorkDescription(initial_value=self._current_description)
            with ItemGrid(classes='log-work-buttons-grid'):
                yield Button(
                    'Save', variant='success', id='log-work-button-save', disabled=True, flat=True
                )
                yield Button('Cancel', variant='error', id='log-work-button-quit', flat=True)

    @on(Input.Changed, 'TimeSpentInput')
    def validate_time_spent(self, event: Input.Changed) -> None:
        self._enable_disable_widgets(
            time_spent_value=event.value,
            time_remaining_value=self.time_remaining_input.value,
            enable_disable_related_widgets=True,
        )

    @on(Input.Changed, 'TimeRemainingInput')
    def validate_time_remaining(self, event: Input.Changed) -> None:
        self._enable_disable_widgets(
            time_spent_value=self.time_spent_input.value,
            time_remaining_value=event.value,
            enable_disable_related_widgets=True,
        )

    @on(Input.Blurred, 'LogDateTimeInput')
    def validate_date_time(self, event: Input.Changed) -> None:
        if not event.value:
            self.save_button.disabled = True
        else:
            try:
                datetime.strptime(event.value, '%Y-%m-%d %H:%M')
                self.save_button.disabled = False
            except ValueError:
                self.save_button.disabled = True

    @staticmethod
    def _valid_time_expression(value: str) -> bool:
        """Validates a time expression.

        Args:
            value: the value to validate.

        Returns:
            True if the expression is valid; False otherwise.
        """

        if not value:
            return False
        if not (cleaned_value := value.strip()):
            return False
        if re.match(r'^\d+[wdhm](\s\d+[wdhm])*$', cleaned_value, re.IGNORECASE):
            return True
        return False

    def _enable_disable_widgets(
        self,
        time_spent_value: str,
        time_remaining_value: str,
        enable_disable_related_widgets: bool = False,
    ) -> None:
        """Validates the user input and enables/disables the save button and other related widgets.

        Args:
            time_spent_value: the value entered by the user for the Time Spent widget.
            time_remaining_value: the value entered by the user for the Time Remaining widget.
            enable_disable_related_widgets: If True, the date/time and description widgets will be enabled/disabled
            according to the validation results.

        Returns:
            None.
        """

        if not time_spent_value and not time_remaining_value:
            # nothing provided by the user then disable the button and widgets
            self.save_button.disabled = True
            if enable_disable_related_widgets:
                self.log_date_time_input.disabled = True
                self.work_description_input.disabled = True
        elif time_spent_value and not time_remaining_value:
            # update the button and related widgets based on the value provided for time spent
            valid_time_spent = self._valid_time_expression(time_spent_value)
            self.save_button.disabled = not valid_time_spent
            if enable_disable_related_widgets:
                self.log_date_time_input.disabled = not valid_time_spent
                self.work_description_input.disabled = not valid_time_spent
        elif not time_spent_value and time_remaining_value:
            # we always need a value for the time spent
            self.save_button.disabled = True
            if enable_disable_related_widgets:
                self.log_date_time_input.disabled = True
                self.work_description_input.disabled = True
        else:
            # both values are provided; remaining time may have changed wrt. to the current remaining time
            # update the button and related widgets based on the value provided for time spent
            valid_time_spent = self._valid_time_expression(time_spent_value)
            self.save_button.disabled = not valid_time_spent
            if enable_disable_related_widgets:
                self.log_date_time_input.disabled = not valid_time_spent
                self.work_description_input.disabled = not valid_time_spent

            # update the button and related widgets based on the value provided for time remaining
            if (not self._current_remaining_estimate and time_remaining_value) or (
                self._current_remaining_estimate
                and time_remaining_value
                and time_remaining_value != self._current_remaining_estimate
            ):
                valid_time_remaining = self._valid_time_expression(time_remaining_value)
                self.save_button.disabled = self.save_button.disabled or not valid_time_remaining
                if enable_disable_related_widgets:
                    if not self.log_date_time_input.disabled and valid_time_remaining:
                        self.log_date_time_input.disabled = False
                    else:
                        self.log_date_time_input.disabled = True

                    if not self.work_description_input.disabled and valid_time_remaining:
                        self.work_description_input.disabled = False
                    else:
                        self.work_description_input.disabled = True

    @on(Button.Pressed, '#log-work-button-quit')
    def handle_quit_button(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, '#log-work-button-save')
    def handle_save_button(self) -> None:
        self.dismiss(
            LogWorkScreenResult(
                work_item_key=self._work_item_key,
                mode=self._mode,
                worklog_id=self._worklog_id,
                time_spent=self.time_spent_input.value,
                time_remaining=self.time_remaining_input.value,
                description=self.work_description_input.text,
                started=(
                    self.log_date_time_input.value.replace(' ', 'T')
                    if self.log_date_time_input.value
                    else None
                ),
            )
        )
