from textual import on
from textual.reactive import Reactive, reactive
from textual.widgets import Checkbox, Input, Select

from jiratui.widgets.base import DateInput
from jiratui.widgets.jql import JQLEditorScreen


class ProjectSelectionInput(Select):
    HELP = 'See Projects List section in the help'

    projects: Reactive[dict | None] = reactive(None, always_update=True)
    """A dictionary with 2 keys: projects: list and selection: str | None"""

    def __init__(self, projects: list):
        super().__init__(
            options=projects,
            prompt='Select a project',
            name='project',
            id='jira-project-selector',
            type_to_search=True,
            compact=True,
            classes='jira-selector',
        )
        self.border_title = 'Project'
        self.border_subtitle = '(p)'

    @property
    def help_anchor(self) -> str:
        return '#projects-list'

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


class IssueTypeSelectionInput(Select):
    HELP = 'See Search by Work Item Type section in the help'

    def __init__(self, types: list):
        super().__init__(
            options=types,
            prompt='Select issue type',
            name='issue_types',
            id='jira-issue-types-selector',
            type_to_search=True,
            compact=True,
            classes='jira-selector',
        )
        self.border_title = 'Issue Type'
        self.border_subtitle = '(t)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-work-item-type'


class IssueStatusSelectionInput(Select):
    HELP = 'See Search by Status section in the help'
    WIDGET_ID = 'jira-issue-status-selector'

    statuses: Reactive[list[tuple[str, str]] | None] = reactive(None, always_update=True)

    def __init__(self, statuses: list):
        super().__init__(
            options=statuses,
            prompt='Select a status',
            name='issue_status',
            id=self.WIDGET_ID,
            type_to_search=True,
            compact=True,
            classes='jira-selector',
        )
        self.border_title = 'Status'
        self.border_subtitle = '(s)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-status'

    async def watch_statuses(self, statuses: list[tuple[str, str]] | None = None) -> None:
        self.clear()
        await self.recompose()
        self.set_options(statuses or [])


class UserSelectionInput(Select):
    HELP = 'See Search by Assignee section in the help'
    WIDGET_ID = 'jira-users-selector'
    users: Reactive[dict | None] = reactive(None, always_update=True)
    """A dictionary with 2 keys:
    - users: list
    - selection: str | None
    """

    def __init__(self, users: list):
        super().__init__(
            options=users,
            prompt='Select a user',
            name='users',
            id=self.WIDGET_ID,
            type_to_search=True,
            compact=True,
            classes='jira-selector',
        )
        self.border_title = 'Assignee'
        self.border_subtitle = '(a)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-assignee'

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


class WorkItemInputWidget(Input):
    HELP = 'See Search by Work Item Key section in the help'

    def __init__(self, value: str | None = None):
        super().__init__(
            id='input_issue_key',
            classes='work-item-key',
            type='text',
            placeholder='e.g. ABC-1234',
            tooltip='Search work items by key',
            value=value,
        )
        self.border_title = 'Work Item Key'
        self.border_subtitle = '(k)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-work-item-key'

    @on(Input.Changed)
    def clean_value(self, event: Input.Changed) -> None:
        if event.value is not None:
            self.value = event.value.strip()


class IssueSearchCreatedFromWidget(DateInput):
    HELP = 'See Search by Created From Date section in the help'
    LABEL = 'Created From'
    TOOLTIP = 'Search issues created after this date (inclusive)'
    ID = 'input_date_from'
    BORDER_SUBTITLE = '(f)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-created-from-date'


class IssueSearchCreatedUntilWidget(DateInput):
    HELP = 'See Search by Created Until Date section in the help'
    LABEL = 'Created Until'
    TOOLTIP = 'Search issues created until this date (inclusive)'
    ID = 'input_date_until'
    BORDER_SUBTITLE = '(u)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-created-until-date'


class OrderByWidget(Select):
    def __init__(self, options: list, initial_value: str | None = None):
        super().__init__(
            options=options,
            prompt='Sort By',
            id='issue-search-order-by-selector',
            type_to_search=False,
            compact=True,
            classes='jira-selector',
            value=initial_value,
        )
        self.border_title = 'Sort'
        self.border_subtitle = '(o)'


class ActiveSprintCheckbox(Checkbox):
    HELP = 'See Search by Active Sprint section in the help'

    def __init__(self, value: bool = False):
        super().__init__(
            id='active-sprint-checkbox',
            label='Active Sprint',
            value=value,
            classes='active-sprint-checkbox',
        )
        self.border_subtitle = '(v)'

    @property
    def help_anchor(self) -> str:
        return '#search-by-active-sprint'


class JQLSearchWidget(Input):
    HELP = 'See Searching Using JQL Expressions section in the help'

    BINDINGS = [
        (
            'ctrl+e',
            'open_jql_editor',
            'JQL Editor',
        )
    ]

    expression: Reactive[str | None] = reactive(None)

    def __init__(self):
        super().__init__(
            id='input_search_term',
            placeholder='Type in a JQL expression to search issues...',
            tooltip='Search issues using JQL (Jira Query Language)',
            type='text',
        )
        self.border_title = 'JQL Query'
        self.border_subtitle = '(j)'

    @property
    def help_anchor(self) -> str:
        return '#searching-using-jql-expressions'

    def watch_expression(self, value: str | None = None) -> None:
        if value and value not in self.value:  # type:ignore[has-type]
            if self.value:  # type:ignore[has-type]
                self.value = f'{self.value} AND {self._clean_value(value)}'  # type:ignore[has-type]
            else:
                self.value = self._clean_value(value)

    async def action_open_jql_editor(self) -> None:
        await self.app.push_screen(JQLEditorScreen(self.value), callback=self.update_input_value)

    def update_input_value(self, value: str) -> None:
        self.value = self._clean_value(value)

    @staticmethod
    def _clean_value(value: str) -> str | None:
        if value:
            return (
                value.replace('\n', ' ')
                .replace('\t', ' ')
                .replace('True', 'true')
                .replace('False', 'false')
            )
        return value
