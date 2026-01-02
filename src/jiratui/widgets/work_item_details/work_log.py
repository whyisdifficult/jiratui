from datetime import datetime
import re
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ItemGrid, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Collapsible, Footer, Input, Label, Markdown, TextArea

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraWorklog, PaginatedJiraWorklog
from jiratui.utils.urls import build_external_url_for_work_log
from jiratui.widgets.base import DateInput


class WorkLogCollapsible(Collapsible):
    """A collapsible widget to display information of a worklog and to handle opening the worklog details in the
    browser and deleting work logs."""

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
            description='Delete Worklog',
            show=True,
        ),
    ]

    class Deleted(Message):
        """A worklog is deleted."""

        pass

    def __init__(self, *args, **kwargs):
        self._url = kwargs.pop('url')
        self._worklog_id = kwargs.pop('worklog_id')
        self._work_item_key = kwargs.pop('work_item_key')
        super().__init__(*args, **kwargs)

    def action_open_in_browser(self) -> None:
        """Opens the worklog in the default browser."""
        if self._url:
            self.app.open_url(self._url)

    def action_delete_worklog(self):
        """Attempts to delete the worklog."""
        if self._worklog_id:
            self.run_worker(self._delete_worklog)

    async def _delete_worklog(self) -> None:
        """Deletes a worklog."""
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.remove_worklog(
            self._work_item_key, self._worklog_id
        )
        if response.success:
            self.notify('Worklog deleted', title='Worklog')
            self.styles.display = 'none'
            # notify the parents to update necessary information after deleting a worklog
            self.post_message(self.Deleted())
        else:
            self.notify(
                f'Failed to delete the worklog: {response.error}', title='Worklog', severity='error'
            )


class WorkItemWorkLogScreen(Screen[dict]):
    """A screen that displays the work logs of a work item."""

    HELP = 'See Worklogs section in the help'
    DEFAULT_CSS = """
    WorkItemWorkLogScreen > Vertical > Label {
        color: $accent;
    }
    """
    BINDINGS = [
        ('escape', 'close_screen', 'Close'),
    ]
    TITLE = 'Worklog'

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key
        self._worklog_counter = 0
        self._worklog_total_count = 0
        # True when at least 1 work log was deleted; useful for refreshing the details of the work item after this
        # screen is dismissed
        self._work_logs_deleted = False

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
            yield VerticalScroll()
        yield Footer(show_command_palette=False)

    async def on_mount(self) -> None:
        if self._work_item_key:
            self.run_worker(self.fetch_work_log())

    def on_work_log_collapsible_deleted(self, message: WorkLogCollapsible.Deleted) -> None:
        """Refreshes the subtitle of the main container to reflect the number of work logs remaining after
        deleting one."""
        self._update_subtitle(True)
        self._work_logs_deleted = True
        message.stop()

    def action_close_screen(self) -> None:
        self.dismiss({'work_logs_deleted': self._work_logs_deleted})

    def _update_subtitle(self, update_counters: bool = False) -> None:
        if update_counters:
            if self._worklog_counter > 0:
                self._worklog_counter -= 1
            if self._worklog_total_count > 0:
                self._worklog_total_count -= 1
        self.root_container.border_subtitle = (
            f'Showing {self._worklog_counter} of {self._worklog_total_count}'
        )

    async def fetch_work_log(self) -> None:
        """Retrieves the work log data associated to a work item and updates the details in the screen.

        Returns:
            `None`.
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_work_item_worklog(
            self._work_item_key
        )
        result: PaginatedJiraWorklog
        if response.success and (result := response.result):
            self._worklog_counter = len(result.logs)
            self._worklog_total_count = result.total
            self._update_subtitle()
            elements: list[WorkLogCollapsible] = []
            worklog: JiraWorklog
            for worklog in result.logs:
                comment_text = ''
                base_url = getattr(getattr(self.app, 'config', None), 'jira_base_url', None)
                if worklog.comment and not (comment_text := worklog.get_comment(base_url=base_url)):
                    # this may happen if we fail to parse the ADF data for Jira Cloud API
                    comment_text = 'Unable to display the description associated to the worklog.'

                url = build_external_url_for_work_log(self._work_item_key, worklog.id)
                elements.append(
                    WorkLogCollapsible(
                        Markdown(comment_text),
                        title=worklog.display(),
                        url=url or None,
                        worklog_id=worklog.id,
                        work_item_key=self._work_item_key,
                    )
                )
            await self.work_log_items_container.mount_all(elements)


class TimeSpentInput(Input):
    def __init__(self):
        super().__init__(placeholder='E.g. 1w 1d', valid_empty=False, classes='required')
        self.border_title = 'Time Spent'
        self.border_subtitle = '(*)'
        self.tooltip = 'Enter the amount of time you work on this task'


class TimeRemainingInput(Input):
    def __init__(self, initial_value: str | None = None):
        super().__init__(value=initial_value, placeholder='E.g. 1d 1h 30m')
        self.border_title = 'Time Remaining'
        self.tooltip = 'Optionally, enter the time remaining in the task'


class LogDateTimeInput(DateInput):
    TEMPLATE = '9999-99-99 99:99'
    PLACEHOLDER = '2025-10-12 13:50'

    def __init__(self):
        super().__init__(valid_empty=False)
        self.disabled = True
        self.border_title = 'Date Started'
        self.tooltip = 'Enter the date/time on which the work was done'
        self.value = datetime.now().strftime('%Y-%m-%d %H:%M')


class WorkDescription(TextArea):
    def __init__(self):
        super().__init__()
        self.disabled = True
        self.border_title = 'Work Description'
        self.compact = True
        self.tooltip = 'Add an optional description'


class LogWorkScreen(Screen[dict]):
    """A modal screen to allow the user to log work for a work item.

    The screen's result is a dictionary with the following keys:
    {
        'time_spent': the time spent as provided by the user in the screen's form.
        'time_remaining': the time remaining as provided by the user in the screen's form.
        'description': an optional as provided by the user in the screen's form.
        'started': an optional datetime string.
        'current_remaining_estimate': the issue's current remaining time.
    }
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
    ]

    def __init__(self, work_item_key: str, current_remaining_estimate: str | None = None):
        super().__init__()
        self._work_item_key = work_item_key
        self._current_remaining_estimate = current_remaining_estimate

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
                yield TimeSpentInput()
                yield TimeRemainingInput(initial_value=self._current_remaining_estimate)
            with ItemGrid(classes='log-work-date-hint-grid'):
                yield LogDateTimeInput()
                yield Label('w = week | d = day | h = hour | m = minutes')
            yield WorkDescription()
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
        self.dismiss({})

    @on(Button.Pressed, '#log-work-button-save')
    def handle_save_button(self) -> None:
        self.dismiss(
            {
                'time_spent': self.time_spent_input.value,
                'time_remaining': self.time_remaining_input.value,
                'description': self.work_description_input.text,
                'started': (
                    self.log_date_time_input.value.replace(' ', 'T')
                    if self.log_date_time_input.value
                    else None
                ),
                'current_remaining_estimate': self._current_remaining_estimate,
            }
        )
