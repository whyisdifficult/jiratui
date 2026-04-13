from textual import on
from textual.widgets import Input

from jiratui.widgets.commons.base import FieldMode, IssueTypeSelectionWidget, ProjectSelectionWidget


class CreateWorkItemProjectSelectionInput(ProjectSelectionWidget):
    """A Select widget for choosing the project for which we want to create a new work item."""

    def __init__(self):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='project_key',
            title='Project',
            required=True,
            jira_field_key='project_key',
        )


class CreateWorkItemIssueTypeSelectionInput(IssueTypeSelectionWidget):
    """A Select widget for choosing the type of issue we want to create."""

    def __init__(self, options: list[tuple[str, str]]):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='issue_type_id',
            jira_field_key='issue_type_id',
            title='Issue Type',
            required=True,
            options=options,
        )


class CreateWorkItemIssueSummaryField(Input):
    """An Input widget for setting the summary field of the issue we want to create."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = 'Summary'
        self.add_class(*['issue_details_input_field', 'required'])
        self.border_subtitle = '(*)'
        self._jira_field_key = 'summary'

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip()


class CreateWorkItemParentKeyField(Input):
    """An Input widget for setting the key of an issue that acts as a parent to the issue we want to create."""

    def __init__(self, value: str | None = None):
        super().__init__(
            placeholder='ABC-12345',
            tooltip='The Key of the parent work item',
            value=value.strip() if value is not None else None,
        )
        self.compact = True
        self.border_title = 'Parent Key'
        self._jira_field_key = 'parent_key'

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @on(Input.Changed)
    def clean_value(self, event: Input.Changed) -> None:
        if event.value is not None:
            self.value = event.value.strip()
