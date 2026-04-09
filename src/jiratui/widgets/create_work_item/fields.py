from textual import on
from textual.reactive import Reactive, reactive
from textual.widgets import Input, Select

from jiratui.widgets.commons.base import FieldMode, IssueTypeSelectionWidget


class CreateWorkItemProjectSelectionInput(Select):
    """A Select widget for choosing the project for which we want to create a new work item."""

    projects: Reactive[dict | None] = reactive(None, always_update=True)
    """A dictionary with 2 keys:

    projects: list
    selection: str | None
    """

    def __init__(self, projects: list, **kwargs):
        super().__init__(
            options=projects,
            prompt='Select a project',
            name='project',
            id='create-work-item-project-selector',  # the id of this widget
            type_to_search=True,
            compact=True,
            **kwargs,
        )
        self.border_title = 'Project'
        self.border_subtitle = '(*)'
        self._jira_field_key = 'project_key'

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    def watch_projects(self, projects: dict | None = None) -> None:
        self.clear()
        if projects and (items := projects.get('projects', []) or []):
            options = [(f'({project.key}) {project.name}', project.key) for project in items]
            self.set_options(options)
            if selection := projects.get('selection'):
                for option in options:
                    if option[1] == selection:
                        self.value = option[1]
                        break


class CreateWorkItemIssueTypeSelectionInput(IssueTypeSelectionWidget):
    """A Select widget for choosing the type of issue we want to create."""

    def __init__(self, options: list[tuple[str, str]], **kwargs):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='create-work-item-issue-type-selector',  # TODO or this? create-work-item-select-issue-type
            jira_field_key='issue_type_id',
            title='Issue Type',
            required=True,
            options=options,
        )
        self.border_title = 'Issue Type'
        self.border_subtitle = '(*)'


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
