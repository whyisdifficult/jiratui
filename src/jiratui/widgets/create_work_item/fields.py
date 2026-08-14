"""These widgets are used by the screen that allows users to create new work items."""

from textual import on
from textual.widgets import Input

from jiratui.widgets.commons.base import FieldMode, IssueTypeSelectionWidget, ProjectSelectionWidget
from jiratui.widgets.commons.widgets import TextInputWidget
from jiratui.widgets.filters import IssueStatusSelectionInput


class WorkItemProjectSelectionField(ProjectSelectionWidget):
    """A [ProjectSelectionWidget](#jiratui.widgets.commons.base.ProjectSelectionWidget) widget for choosing the project
    for which we want to create a new work item."""

    def __init__(self):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='project_key',
            title='Project',
            required=True,
            jira_field_key='project_key',
        )


class WorkItemTypeSelectionField(IssueTypeSelectionWidget):
    """A [IssueTypeSelectionWidget](#jiratui.widgets.commons.base.IssueTypeSelectionWidget) widget for choosing the type
    of issue we want to create."""

    def __init__(self, options: list[tuple[str, str]]):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='issue_type_id',
            jira_field_key='issue_type_id',
            title='Issue Type',
            required=True,
            options=options,
        )


class SummaryField(Input):
    """An Input widget for setting the summary field of the issue we want to create."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = 'Summary'
        self.add_class(*['create-update-field-widget', 'required', 'summary', 'cols-2'])
        self.border_subtitle = '(*)'
        self._jira_field_key = 'summary'

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip()


class ParentKeyField(TextInputWidget):
    def __init__(self, value: str | None = None):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='parent_key',
            jira_field_key='parent_key',
            title='Parent Key',
            required=False,
            placeholder='Enter Key...',
        )
        self.value = value.strip() if value is not None else ''
        self.compact = True
        self.add_class(*['create-update-field-widget', 'parent-key'])
        self.tooltip = 'The Key of the parent work item'
        self.field_supports_update = 1

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip().replace(' ', '')


class WorkItemStatusField(IssueStatusSelectionInput):
    """A [IssueStatusSelectionInput](#jiratui.widgets.filters.IssueStatusSelectionInput) widget to pick the status of
    the work item being created."""

    WIDGET_ID = 'jira-issue-status-selector-create'

    def __init__(self, statuses: list):
        super().__init__(statuses, classes='create-work-item-generic-selector')
        self.jira_field_key = 'status'
        """The key to used by Jira to identify this field in the edit-metadata."""
        self.border_subtitle = None
