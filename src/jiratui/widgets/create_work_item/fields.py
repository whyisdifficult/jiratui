from textual import on
from textual.reactive import Reactive, reactive
from textual.widgets import Input

from jiratui.widgets.common.base_fields import (
    FieldMode,
    IssueTypeSelectionWidget,
    ProjectSelectionWidget,
    UserPickerWidget,
)


class CreateWorkItemProjectSelectionInput(ProjectSelectionWidget):
    """Select for choosing a project."""

    def __init__(self):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='create-work-item-select-project',
            title='Project',
            required=True,
        )


class CreateWorkItemIssueTypeSelectionInput(IssueTypeSelectionWidget):
    """Select for choosing an issue type."""

    def __init__(self, options: list[tuple[str, str]]):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='create-work-item-select-issue-type',
            title='Issue Type',
            required=True,
            options=options,
        )


class CreateWorkItemAssigneeSelectionInput(UserPickerWidget):
    """Select for choosing an assignee."""

    def __init__(self):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='create-work-item-select-assignee',
            title='Assignee',
            required=False,
        )
        self.prompt = 'Select an assignee'


class CreateWorkItemReporterSelectionInput(UserPickerWidget):
    """Select for choosing a reporter."""

    reporters: Reactive[dict | None] = reactive(None, always_update=True)

    def __init__(self):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='create-work-item-select-reporter',
            title='Reporter',
            required=True,
        )
        self.prompt = 'Select a reporter (*)'

    def watch_reporters(self, reporters: dict | None = None) -> None:
        self.users = reporters


class CreateWorkItemIssueSummaryField(Input):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = 'Summary'
        self.add_class(*['issue_details_input_field', 'required'])
        self.border_subtitle = '(*)'

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip()


class CreateWorkItemParentKeyField(Input):
    def __init__(self, value: str | None = None):
        super().__init__(
            id='parent_key',
            classes='create-work-item-parent-input-field',
            placeholder='ABC-12345',
            tooltip='The Key of the parent work item',
            value=value.strip() if value is not None else None,
        )
        self.compact = True
        self.border_title = 'Parent Key'

    @on(Input.Changed)
    def clean_value(self, event: Input.Changed) -> None:
        if event.value is not None:
            self.value = event.value.strip()
