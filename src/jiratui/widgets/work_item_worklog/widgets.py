from datetime import datetime

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Label, ProgressBar, TextArea

from jiratui.widgets.base import DateInput


class TimeTrackingWidget(Widget):
    """A widget to display time tracking information for a work item using a progress bar and a label."""

    DEFAULT_CSS = """
    Bar > .bar--bar {
        color: $accent;
        background: $secondary;
    }
    """

    def __init__(
        self,
        original_estimate: str | None = None,
        time_spent: str | None = None,
        remaining_estimate: str | None = None,
        original_estimate_seconds: int | None = None,
        time_spent_seconds: int | None = None,
        remaining_estimate_seconds: int | None = None,
    ):
        super().__init__()
        self.border_title = 'Time Tracking'
        self._original_estimate = original_estimate or ''
        self._time_spent = time_spent or ''
        self._remaining_estimate = remaining_estimate or ''
        self._original_estimate_seconds = original_estimate_seconds
        self._time_spent_seconds = time_spent_seconds or 0
        self._remaining_estimate_seconds = remaining_estimate_seconds

    @property
    def progress_bar(self) -> ProgressBar:
        return self.query_one(ProgressBar)

    def compose(self) -> ComposeResult:
        yield Label(
            f'Original Estimate: {self._original_estimate} | Time Spent: {self._time_spent} | Remaining Estimate: {self._remaining_estimate}'
        )
        yield ProgressBar(total=100, show_percentage=True, show_eta=False)

    def on_mount(self):
        if self._original_estimate_seconds:
            self.progress_bar.progress = (
                self._time_spent_seconds * 100
            ) / self._original_estimate_seconds
        elif self._remaining_estimate_seconds and self._time_spent_seconds:
            self.progress_bar.progress = (self._time_spent_seconds * 100) / (
                self._remaining_estimate_seconds + self._time_spent_seconds
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
