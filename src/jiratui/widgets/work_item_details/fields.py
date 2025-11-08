from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Input, Label, MaskedInput, ProgressBar, Select, SelectionList
from textual.widgets.selection_list import Selection

from jiratui.widgets.base import DateInput, ReadOnlyField
from jiratui.widgets.filters import IssueStatusSelectionInput, UserSelectionInput


class IssueDetailsAssigneeSelection(UserSelectionInput):
    WIDGET_ID = 'jira-users-assignee-selector-edit'
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


class IssueParentField(Input):
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self):
        super().__init__()
        self.border_title = 'Parent'
        self.add_class(*['issue_details_input_field', 'work-item-key'])
        self.jira_field_key = 'parent'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled = True
        """Indicates whether the work item allows editing/updating this field."""

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.value:
            self.value = event.value.strip()


class IssueSummaryField(Input):
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self):
        super().__init__()
        self.border_title = 'Summary'
        self.border_subtitle = '(*)'
        self.add_class(*['issue_details_input_field', 'required', 'cols-3'])
        self.jira_field_key = 'summary'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled = True
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


class WorkItemFlagField(Label):
    """A widget that shows whether a work item is flagged."""

    show: Reactive[bool | None] = reactive(True)
    """Toggles the widget display."""

    def __init__(self):
        super().__init__('Flagged!', classes='cols-3 accent')
        self.styles.display = 'block'
        self.disabled = True

    def watch_show(self, value: bool = True) -> None:
        if value:
            self.styles.display = 'block'
        else:
            self.styles.display = 'none'


class WorkItemLabelsField(Input):
    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self):
        super().__init__()
        self.border_title = 'Labels'
        self.add_class(*['issue_details_input_field', 'cols-3'])
        self.jira_field_key = 'labels'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.update_is_enabled = True
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
        self.update_is_enabled = True
        """Indicates whether the work item allows editing/updating this field."""

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled


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


class WorkItemDynamicFieldUpdateWidget(Input):
    """A widget to hold (optional) values."""

    def __init__(self, **kwargs):
        self.update_enabled = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        super().__init__(**kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.update_enabled

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value(self) -> str:
        return self.value

    @property
    def value_has_changed(self) -> bool:
        if self.original_value == '':
            if self.value.strip() != '':
                return True
            return False

        if self.original_value.strip() == '':
            if self.value.strip() != '':
                return True
            return False

        if self.value == '' or (self.value != '' and self.value.strip() == ''):
            return True

        if self.original_value != self.value:
            return True
        return False


class WorkItemDynamicFieldUpdateNumericWidget(Input):
    """A widget to hold (optional) numeric values."""

    def __init__(self, **kwargs):
        self.update_enabled = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        super().__init__(type='number', placeholder='123', **kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.update_enabled

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value(self) -> float | None:
        if self.value is not None:
            return float(self.value)
        return None

    @property
    def value_has_changed(self) -> bool:
        if self.original_value == '':
            if self.value.strip() != '':
                return True
            return False

        if self.original_value.strip() == '':
            if self.value.strip() != '':
                return True
            return False

        if self.value == '' or (self.value != '' and self.value.strip() == ''):
            return True

        if self.original_value != self.value:
            return True
        return False


class WorkItemDynamicFieldUpdateTextWidget(Input):
    """A widget to hold (optional) text values."""

    def __init__(self, **kwargs):
        self.update_enabled = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', None)
        super().__init__(**kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.update_enabled

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value(self) -> str:
        return self.value

    @property
    def value_has_changed(self) -> bool:
        if self.original_value == '':
            if self.value.strip() != '':
                return True
            return False

        if self.original_value.strip() == '':
            if self.value.strip() != '':
                return True
            return False

        if self.value == '' or (self.value != '' and self.value.strip() == ''):
            return True

        if self.original_value != self.value:
            return True
        return False


class WorkItemDynamicFieldUpdateDateWidget(MaskedInput):
    """A widget to hold (optional) date values."""

    def __init__(self, **kwargs):
        self.update_enabled = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        super().__init__(template='9999-99-99', placeholder='2025-12-23', **kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.update_enabled

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value(self) -> str:
        return self.value

    @property
    def value_has_changed(self) -> bool:
        if self.original_value == '':
            if self.value.strip() != '':
                return True
            return False

        if self.original_value.strip() == '':
            if self.value.strip() != '':
                return True
            return False

        if self.value == '' or (self.value != '' and self.value.strip() == ''):
            return True

        if self.original_value != self.value:
            return True
        return False


class WorkItemDynamicFieldUpdateSelectionWidget(Select):
    def __init__(self, **kwargs):
        self.update_enabled = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', None)
        super().__init__(**kwargs)
        self.compact = True
        self.add_class('create-work-item-generic-selector')
        self.disabled = not self.update_enabled

    @property
    def original_value(self) -> Any:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        return self.__original_value

    def get_value(self) -> Any:
        return self.selection

    @property
    def value_has_changed(self) -> bool:
        if not self.original_value:
            if not self.selection:
                return False
            return True

        if not self.selection:
            return True

        if self.original_value != self.selection:
            return True
        return False


class WorkItemDynamicFieldUpdateMultiSelectWidget(SelectionList):
    # TODO
    def __init__(self, options: list[Selection], **kwargs):
        self.update_enabled = kwargs.pop('field_supports_update', False)
        super().__init__(*options, compact=True, **kwargs)
        self.add_class('create-work-item-generic-selector')
        self.disabled = not self.update_enabled
