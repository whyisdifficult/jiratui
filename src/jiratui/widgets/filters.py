from textual import on
from textual.reactive import Reactive, reactive
from textual.widgets import Checkbox, Input, Select

from jiratui.widgets.base import DateInput
from jiratui.widgets.jql import JQLEditorScreen


class ProjectSelectionInput(Select):
    HELP = """\
# Jira Projects

The list of projects displayed depends on the permissions of the user making the requests. This in turn is determined by
the Jira Account ID you configured when you run the tool. For a project to appear on this list one of these conditions
must be satisfied:

- The user Jira account must have the [Browse Projects project permission](https://confluence.atlassian.com/x/yodKLg) for the project.
- The user Jira account must have the [Administer Projects project permission](https://confluence.atlassian.com/x/yodKLg) for the project.
- The user Jira account must have the [Administer Jira global permission](https://confluence.atlassian.com/x/x4dKLg).
    """

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
    HELP = """
# Search by Type of Work Item

Search work items based on their type. If a project is selected then this list will contain the type of work items
supported by the project. If no project is selected then this list will contain all the types of work items available
in the known projects.

**Important**: this list may contain types with duplicated names when there is no project selected. The id of these
types will be different though.
    """

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


class IssueStatusSelectionInput(Select):
    HELP = """
# Search by Status

Search work items based on their status. If a project is selected then this list will contain the statuses supported by
the work types in the project. If no project is selected then this list will contain all possible statuses.
    """

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

    async def watch_statuses(self, statuses: list[tuple[str, str]] | None = None) -> None:
        self.clear()
        await self.recompose()
        self.set_options(statuses or [])


class UserSelectionInput(Select):
    HELP = """
# Search by Assignee

Search work items based on their assignee. If a project is selected then this list will contain the active users that
can have work items assigned in the project. If no project is selected then this list will contain all available
(active) users.
    """
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
    HELP = """\
# Search by Work Item Key

This expects a case-sensitive string. If defined, this has precedence over all the other search criteria.
    """

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

    @on(Input.Changed)
    def clean_value(self, event: Input.Changed) -> None:
        if event.value is not None:
            self.value = event.value.strip()


class IssueSearchCreatedFromWidget(DateInput):
    HELP = """\
# Search Work Items by Date

If defined, only work items that were created after this date (inclusive) will be fetched.

If no `Created From` and `Created Until` search criteria are defined then the tool will fetch work items created
within the last 15 days. The number of days can be specified by the configuration variable
`search_issues_default_day_interval`.
    """
    LABEL = 'Created From'
    TOOLTIP = 'Search issues created after this date (inclusive)'
    ID = 'input_date_from'
    BORDER_SUBTITLE = '(f)'


class IssueSearchCreatedUntilWidget(DateInput):
    HELP = """\
# Search Work Items by Date

If defined, only work items that were created until this date (inclusive) will be fetched.

If no `Created From` and `Created Until` search criteria are defined then the tool will fetch work items created
within the last 15 days. The number of days can be specified by the configuration variable
`search_issues_default_day_interval`.
    """
    LABEL = 'Created Until'
    TOOLTIP = 'Search issues created until this date (inclusive)'
    ID = 'input_date_until'
    BORDER_SUBTITLE = '(u)'


class OrderByWidget(Select):
    def __init__(self, options: list):
        super().__init__(
            options=options,
            prompt='Sort By',
            id='issue-search-order-by-selector',
            type_to_search=False,
            compact=True,
            classes='jira-selector',
        )
        self.border_title = 'Sort'
        self.border_subtitle = '(o)'


class ActiveSprintCheckbox(Checkbox):
    HELP = """\
# Search Work Items in the Active Sprint

When this checkbox is checked the application will filter work items that correspond to the currently active
sprint.
    """

    def __init__(self):
        super().__init__(label='Active Sprint', value=False, classes='active-sprint-checkbox')
        self.border_subtitle = '(v)'


class JQLSearchWidget(Input):
    HELP = """\
# Search Expression

You can search work items using
[JQL expressions](https://support.atlassian.com/jira-software-cloud/docs/what-is-advanced-search-in-jira-cloud/).

## Examples
- Search work items assigned to John Smith

```python
assignee = "John Smith"
```

or searching by the user's email address:

```python
assignee = "john@smith.com"
```

In addition, you can define JQL expressions in the config file using the option `pre_defined_jql_expressions` and then
load these expressions in the JQL Editor by focussing this field `(j)` and then pressing `^e`.
    """

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
