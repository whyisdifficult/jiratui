"""
This module contains the widgets used for displaying and updating some of the fields associated to a wrk item.
"""

from typing import Any

from dateutil.parser import isoparse  # type:ignore[import-untyped]
from textual import on
from textual.app import ComposeResult
from textual.reactive import Reactive, reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Label, MaskedInput, ProgressBar, Select, SelectionList
from textual.widgets.selection_list import Selection

from jiratui.widgets.base import DateInput, ReadOnlyField
from jiratui.widgets.filters import IssueStatusSelectionInput, UserSelectionInput


class IssueDetailsAssigneeSelection(UserSelectionInput):
    """A select widget that stores the assignee field of a work item."""

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
    """A selection field that stores the status field of a work item."""

    WIDGET_ID = 'jira-issue-status-selector-edit'

    def __init__(self, statuses: list):
        super().__init__(statuses)
        self.border_subtitle = '(z)'
        self.jira_field_key = 'status'
        """The key to used by Jira to identify this field in the edit-metadata."""


class IssueDetailsPrioritySelection(Select):
    """A widget to display and update the priority field of a work item."""

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
    """A widget to display and update the project field of a work item."""

    def __init__(self):
        super().__init__()
        self.border_title = 'Project'
        self.add_class(*['issue_details_input_field', 'cols-3'])


class ReporterField(ReadOnlyField):
    """A widget to display and update the reporter field of a work item."""

    def __init__(self):
        super().__init__(placeholder='-')
        self.border_title = 'Reporter'
        self.add_class(*['issue_details_input_field', 'cols-2'])


class IssueSprintField(ReadOnlyField):
    """A widget to display and update the sprint field of a work item."""

    def __init__(self):
        super().__init__()
        self.border_title = 'Sprint'
        self.classes = 'issue_details_input_field'


class IssueKeyField(ReadOnlyField):
    """A widget to display and update the key field of a work item."""

    def __init__(self):
        super().__init__()
        self.border_title = 'Key'
        self.add_class(*['issue_details_input_field', 'work-item-key'])


class IssueParentField(Input):
    """A widget to display and update the parent field of a work item."""

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
    """A widget to display and update the summary field of a work item."""

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
    """A widget to display and update the labels field of a work item."""

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
    """A widget to display and update the type of work item."""

    def __init__(self):
        super().__init__()
        self.border_title = 'Type'
        self.classes = 'issue_details_input_field'


class IssueComponentsField(Widget):
    """A composite widget that allows users to view/update the components associated to a work item."""

    data: Reactive[dict | None] = reactive(None)
    update_enabled: Reactive[bool | None] = reactive(True)

    class WorkItemComponentsScreen(Screen[list[str] | None]):
        """A modal screen that allows users to select components to associate to a work item."""

        BINDINGS = [
            ('escape', 'pop_screen', 'Close'),
        ]

        def __init__(self, selections: list[Selection] = None):
            super().__init__()
            self.__selections = selections

        def compose(self) -> ComposeResult:
            options = self.__selections if self.__selections is not None else []
            components_selection_widget = SelectionList[str](
                *options, id='components-selections-list'
            )
            components_selection_widget.border_title = 'Applicable Components'
            yield components_selection_widget
            yield Button(
                'Update', variant='success', id='work-item-components-button-update', flat=True
            )

        def action_pop_screen(self) -> None:
            self.dismiss(None)  # no changes made to the selections

        @on(Button.Pressed, '#work-item-components-button-update')
        def handle_save_button(self) -> None:
            self.dismiss(self.query_one(SelectionList).selected)

    def __init__(self):
        self.jira_field_key = 'components'
        """The ID/key of the field in Jira."""
        super().__init__(id=self.jira_field_key)
        self.__allowed_values: list[dict] | None = None
        self.__current_selected_ids: list[str] = []
        self.update_is_enabled = True
        """Indicates whether the work item allows editing/updating this field."""

    @property
    def components(self) -> list[dict]:
        # returns the current selection as a list of dict that can be used for updating the field in Jira
        if self.__allowed_values:
            return [
                item
                for item in self.__allowed_values
                if item.get('id') in self.__current_selected_ids
            ]
        return []

    def get_value_for_update(self) -> list[dict]:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: the current selection as a list of dict that can be used for updating the field in Jira.
        """

        if self.__allowed_values:
            return [
                item
                for item in self.__allowed_values
                if item.get('id') in self.__current_selected_ids
            ]
        return []

    def compose(self) -> ComposeResult:
        components_input = Input(id=f'input-field-{self.jira_field_key}')
        components_input.border_title = 'Components'
        components_input.border_subtitle = 'Tip: press enter to update'
        yield components_input

    def watch_data(self, data: dict | None = None) -> None:
        if data:
            self.__allowed_values = data.get('allowed_values', []) or []
            components_input = self.query_one(Input)
            if data.get('current_values', []):
                self.__current_selected_ids = [cv.id for cv in data.get('current_values')]
                components_input.value = '|'.join(
                    [component.name for component in data.get('current_values')]
                )
            else:
                components_input.value = ''

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.query_one(Input).disabled = not enabled

    @on(Input.Submitted, '#input-field-components')
    def open_modal(self, event: Input.Submitted) -> None:
        current_selections: list[Selection] = []
        for allowed_value in self.__allowed_values or []:
            if allowed_value.get('id') in self.__current_selected_ids:
                current_selections.append(
                    Selection(allowed_value.get('name'), allowed_value.get('id'), True)
                )
            else:
                current_selections.append(
                    Selection(allowed_value.get('name'), allowed_value.get('id'))
                )
        self.app.push_screen(
            self.WorkItemComponentsScreen(current_selections), callback=self._update_selections
        )

    def _update_selections(self, selections: list[str] | None) -> None:
        if selections is None:
            # nothing was updated
            return
        self.__current_selected_ids = selections or []
        components_input = self.query_one(Input)
        if self.__allowed_values:
            components_input.value = '|'.join(
                [
                    av.get('name')
                    for av in self.__allowed_values
                    if av.get('id') in self.__current_selected_ids
                ]
            )
        else:
            components_input.value = ''


class WorkItemDetailsDueDate(DateInput):
    """A widget to display the due date of a work item and to allow the user to update its value."""

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


###
# Dynamic Widgets - these are used for displaying and updating data related to custom fields and other system fields
# that the application does not handle with the "static" widgets above.
###


class WorkItemDynamicFieldUpdateWidget(Input):
    """A widget to hold (optional) values."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        self.jira_field_key = jira_field_key
        super().__init__(id=self.jira_field_key, **kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

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
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:float`."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value')
        self.jira_field_key = jira_field_key
        super().__init__(id=self.jira_field_key, type='number', placeholder='123.45', **kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> float | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return None
        if self.__original_value == '' or (
            self.__original_value != '' and self.__original_value.strip() == ''
        ):
            return None
        return float(self.__original_value)

    def get_value_for_update(self) -> float | None:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a float; None if the field has no value
        """

        if self.value is not None:
            try:
                return float(self.value)
            except ValueError:
                return None
        return None

    @property
    def value_has_changed(self) -> bool:
        if self.original_value is None:
            if self.value.strip() != '':
                return True
            return False

        if self.value == '' or (self.value != '' and self.value.strip() == ''):
            return True

        if self.original_value != float(self.value):
            return True
        return False


class WorkItemDynamicFieldUpdateTextWidget(Input):
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:textfield`.

    The custom type does not support ADF.
    """

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', None)
        self.jira_field_key = jira_field_key
        super().__init__(id=self.jira_field_key, placeholder='some string...', **kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value_for_update(self) -> str:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: the string value.
        """

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
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:datepicker`."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        self.jira_field_key = jira_field_key
        super().__init__(
            id=self.jira_field_key, template='9999-99-99', placeholder='2025-12-23', **kwargs
        )
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""

        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value_for_update(self) -> str | None:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a date value in ISO format; None if the field has no value
        """

        if self.value and self.value.strip():
            try:
                return str(isoparse(self.value).date())
            except ValueError:
                return None
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


class WorkItemDynamicFieldUpdateDateTimeWidget(MaskedInput):
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:datetime`."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        self.jira_field_key = jira_field_key
        super().__init__(
            id=self.jira_field_key,
            template='9999-99-99 99:99:99',
            placeholder='2025-12-23 13:45:10',
            **kwargs,
        )
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> str | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return ''
        return self.__original_value

    def get_value_for_update(self) -> str | None:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a date/time value in ISO format; None if the field has no value
        """

        if self.value and self.value.strip():
            try:
                return isoparse(self.value).isoformat()
            except ValueError:
                return None
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


class WorkItemDynamicFieldUpdateSelectionWidget(Select):
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:selection`."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', None)
        self.jira_field_key = jira_field_key
        super().__init__(id=self.jira_field_key, **kwargs)
        self.compact = True
        self.add_class('create-work-item-generic-selector')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> Any:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        return self.__original_value

    def get_value_for_update(self) -> dict | None:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a dictionary with the id of the option selected by the user; None if the user does not select
        anything. This wil unset the field.
        """

        if self.selection is None:
            return None
        return {'id': self.selection}

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


class WorkItemDynamicFieldUpdateURLWidget(Input):
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:url`."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value = kwargs.pop('original_value', '')
        self.jira_field_key = jira_field_key
        super().__init__(
            id=self.jira_field_key, type='text', placeholder='https://jiratui.sh', **kwargs
        )
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> str:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        return self.__original_value

    def get_value_for_update(self) -> str:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a string with the URL.
        """

        return self.value

    def on_input_blurred(self, event: Input.Changed) -> None:
        if event.value and event.value.strip():
            if 'http' not in event.value:
                self.value = f'https://{event.value}'

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


class WorkItemDynamicFieldUpdateLabelsWidget(Input):
    """A widget to show and allow updating custom fields whose schema type is
    `com.atlassian.jira.plugin.system.customfieldtypes:labels`."""

    def __init__(self, jira_field_key: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__original_value: list[str] = kwargs.pop('original_value', [])
        self.jira_field_key = jira_field_key
        super().__init__(id=self.jira_field_key, placeholder='labelA, labelB', **kwargs)
        self.add_class('issue_details_input_field')
        self.disabled = not self.__field_supports_update

    @property
    def original_value(self) -> list[str] | None:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        if self.__original_value is None:
            return []
        return self.__original_value

    def get_value_for_update(self) -> list[str]:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a list of strings.
        """

        if self.value and self.value.strip():
            return [str(x) for x in self.value.split(',')]
        return []

    @property
    def value_has_changed(self) -> bool:
        if self.original_value == [] and not self.value:
            return False

        if self.original_value == [] and not self.value.strip():
            return False

        if self.original_value == []:
            return True

        if self.value == '' or (self.value != '' and self.value.strip() == ''):
            return True

        if set(self.original_value) != {x.lower() for x in self.value.split(',')}:
            return True
        return False


class WorkItemDynamicFieldUpdateMultiCheckboxesWidget(Widget):
    """A composite widget that allows users to view/update custom fields with schema custom type
    `com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes`."""

    class SelectionsScreen(Screen[list[str] | None]):
        """A modal screen that allows users to select components to associate to a work item."""

        BINDINGS = [
            ('escape', 'pop_screen', 'Close'),
        ]

        def __init__(self, jira_field_id: str, selections: list[Selection] = None):
            super().__init__()
            self.__selections = selections
            self.__jira_field_id = jira_field_id

        def compose(self) -> ComposeResult:
            options = self.__selections if self.__selections is not None else []
            components_selection_widget = SelectionList[str](
                *options, id=f'selections-list-{self.__jira_field_id}'
            )
            components_selection_widget.border_title = 'Available Options'
            yield components_selection_widget
            yield Button(
                'Update',
                variant='success',
                id=f'work-item-multicheckbox-button-update-{self.__jira_field_id}',
                flat=True,
            )

        def action_pop_screen(self) -> None:
            self.dismiss(None)  # no changes made to the selections

        @on(Button.Pressed)
        def handle_save_button(self) -> None:
            self.dismiss(self.query_one(SelectionList).selected)

    def __init__(self, jira_field_key: str, field_title: str, **kwargs):
        self.__field_supports_update = kwargs.pop('field_supports_update', False)
        self.__allowed_values: list[dict] | None = kwargs.pop('allowed_values', [])
        """A list of dictionaries. Each dict is expected to have 'id' and 'value' attributes."""
        self.__original_value: list[dict] | None = kwargs.pop('original_value', [])
        """A list of dictionaries. Each dict is expected to have 'id' and 'value' attributes. This is the value as
        stored in Jira and as retrieved from the API."""
        self.jira_field_key = jira_field_key
        super().__init__(id=self.jira_field_key)
        self.__current_selected_ids: list[str] = [
            cv.get('id') for cv in self.__original_value or []
        ]
        """This holds the selections (ids) after every update that the user makes."""
        self.__field_title: str = field_title or self.jira_field_key
        self.disabled = not self.__field_supports_update

    def get_value_for_update(self) -> list[dict]:
        # returns the current selection as a list of dict that can be used for updating the field in Jira
        if self.__allowed_values:
            return [
                item
                for item in self.__allowed_values
                if item.get('id') in self.__current_selected_ids
            ]
        return []

    def compose(self) -> ComposeResult:
        labels_input = Input(id=f'input-field-{self.jira_field_key}')
        labels_input.border_title = self.__field_title
        labels_input.border_subtitle = 'Tip: press enter to update'
        labels_input.disabled = self.disabled
        yield labels_input

    def on_mount(self):
        labels_input = self.query_one(Input)
        labels_input.value = '|'.join([item.get('value') for item in self.__original_value or []])

    @on(Input.Submitted)
    def open_modal(self, event: Input.Submitted) -> None:
        current_selections: list[Selection] = []
        for allowed_value in self.__allowed_values or []:
            if allowed_value.get('id') in self.__current_selected_ids:
                current_selections.append(
                    Selection(allowed_value.get('value'), allowed_value.get('id'), True)
                )
            else:
                current_selections.append(
                    Selection(allowed_value.get('value'), allowed_value.get('id'))
                )
        self.app.push_screen(
            self.SelectionsScreen(self.jira_field_key, current_selections),
            callback=self._update_selections,
        )

    def _update_selections(self, selections: list[str] | None) -> None:
        if selections is None:
            # nothing was updated
            return
        labels_input = self.query_one(Input)
        if self.__allowed_values:
            self.__current_selected_ids = selections or []
            labels_input.value = '|'.join(
                [
                    av.get('value')
                    for av in self.__allowed_values
                    if av.get('id') in self.__current_selected_ids
                ]
            )
        else:
            labels_input.value = ''

    @property
    def value_has_changed(self) -> bool:
        original_ids = [str(cv.get('id')) for cv in self.__original_value or []]
        if original_ids and self.__current_selected_ids:
            if set(original_ids) != set(self.__current_selected_ids):
                return True
            return False
        if original_ids and not self.__current_selected_ids:
            return True
        if not original_ids and self.__current_selected_ids:
            return True
        return False
