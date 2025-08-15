from textual import on
from textual.reactive import Reactive, reactive
from textual.widgets import Input, Select, TextArea

from jiratui.widgets.base import DateInput


class CreateWorkItemProjectSelectionInput(Select):
    projects: Reactive[dict | None] = reactive(None, always_update=True)
    """A dictionary with 2 keys: projects: list and selection: str | None"""

    def __init__(self, projects: list, **kwargs):
        super().__init__(
            options=projects,
            prompt='Select a project',
            name='project',
            id='create-work-item-project-selector',
            type_to_search=True,
            compact=True,
            **kwargs,
        )
        self.border_title = 'Project'
        self.border_subtitle = '(*)'

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


class CreateWorkItemIssueTypeSelectionInput(Select):
    def __init__(self, types: list, **kwargs):
        super().__init__(
            options=types,
            prompt='Select issue type',
            name='issue_types',
            id='create-work-item-issue-types-selector',
            type_to_search=True,
            compact=True,
            **kwargs,
        )
        self.border_title = 'Issue Type'
        self.border_subtitle = '(*)'


class CreateWorkItemAssigneeSelectionInput(Select):
    WIDGET_ID = 'create-work-item-assignee-selector'
    users: Reactive[dict | None] = reactive(None, always_update=True)
    """A dictionary with 2 keys:
    - users: list
    - selection: str | None
    """
    BORDER_TITLE = 'Assignee'
    BORDER_SUB_TITLE = None

    def __init__(self, users: list, **kwargs):
        super().__init__(
            options=users,
            prompt='Select a user',
            id=self.WIDGET_ID,
            type_to_search=True,
            compact=True,
            **kwargs,
        )
        self.border_title = self.BORDER_TITLE
        if self.BORDER_SUB_TITLE:
            self.border_subtitle = self.BORDER_SUB_TITLE

    def watch_users(self, users: dict | None = None) -> None:
        self.clear()
        if users and (items := users.get('users', []) or []):
            options = [(item.display_name, item.account_id) for item in items]
            self.set_options(options)
            if selection := users.get('selection'):
                for option in options:
                    if option[1] == selection:
                        self.value = option[1]
                        break


class CreateWorkItemReporterSelectionInput(Select):
    WIDGET_ID = 'create-work-item-reporter-selector'
    BORDER_TITLE = 'Reporter'
    BORDER_SUB_TITLE = '(*)'
    reporters: Reactive[dict | None] = reactive(None, always_update=True)

    def __init__(self, users: list, **kwargs):
        super().__init__(
            options=users,
            prompt='Select a user',
            id=self.WIDGET_ID,
            type_to_search=True,
            compact=True,
            **kwargs,
        )
        self.border_title = self.BORDER_TITLE
        if self.BORDER_SUB_TITLE:
            self.border_subtitle = self.BORDER_SUB_TITLE

    def watch_reporters(self, users: dict | None = None) -> None:
        self.clear()
        if users and (items := users.get('users', []) or []):
            options = [(item.display_name, item.account_id) for item in items]
            self.set_options(options)
            if selection := users.get('selection'):
                for option in options:
                    if option[1] == selection:
                        self.value = option[1]
                        break


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


class CreateWorkItemDescription(TextArea):
    def __init__(self):
        super().__init__(
            '',
            id='description',
            compact=True,
            classes='create-work-item-description',
        )
        self.border_title = 'Description'


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


class CreateWorkItemDueDate(DateInput):
    LABEL = 'Due Date'
    TOOLTIP = 'Enter the due date for this work item.'
    CLASSES = 'create-work-item-input-date'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.compact = True


class CreateWorkItemTextField(Input):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compact = True
        self.add_class('create-work-item-generic-input-field')


class CreateWorkItemSelectionInput(Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compact = True
        self.add_class('create-work-item-generic-selector')
