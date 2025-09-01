from dataclasses import dataclass
from datetime import date, datetime
import logging

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, ItemGrid, Vertical, VerticalScroll
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Rule, Select, TabbedContent, TabPane
from textual.worker import Worker

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.constants import LOGGER_NAME
from jiratui.models import (
    IssueType,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraUser,
    WorkItemsSearchOrderBy,
)
from jiratui.utils.adf2md.adf2md import adf2md
from jiratui.widgets.attachments.attachments import IssueAttachmentsWidget
from jiratui.widgets.comments.comments import IssueCommentsWidget
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen
from jiratui.widgets.filters import (
    ActiveSprintCheckbox,
    IssueSearchCreatedFromWidget,
    IssueSearchCreatedUntilWidget,
    IssueStatusSelectionInput,
    IssueTypeSelectionInput,
    JQLSearchWidget,
    OrderByWidget,
    ProjectSelectionInput,
    UserSelectionInput,
    WorkItemInputWidget,
)
from jiratui.widgets.related_work_items.related_issues import RelatedIssuesWidget
from jiratui.widgets.remote_links.links import IssueRemoteLinksWidget
from jiratui.widgets.search import IssuesSearchResultsTable, SearchResultsContainer
from jiratui.widgets.subtasks import IssueChildWorkItemsWidget
from jiratui.widgets.summary import IssueDescriptionWidget, IssueSummaryWidget
from jiratui.widgets.work_item_details.details import IssueDetailsWidget


@dataclass
class WorkItemSearchResult:
    total: int = 0
    start: int = 0
    end: int = 0
    response: JiraIssueSearchResponse | None = None


class MainScreen(Screen):
    """The main screen of the application."""

    BINDINGS = [
        (
            'ctrl+r',
            'search',
            'Search Issues',
        ),
        Binding(
            key='p',
            action='focus_widget("p")',
            description='Focus the project selection widget',
            show=False,
        ),
        Binding(
            key='t',
            action='focus_widget("t")',
            description='Focus the issue type selection widget',
            show=False,
        ),
        Binding(
            key='s',
            action='focus_widget("s")',
            description='Focus the status selection widget',
            show=False,
        ),
        Binding(
            key='a',
            action='focus_widget("a")',
            description='Focus the assignee selection widget',
            show=False,
        ),
        Binding(
            key='k',
            action='focus_widget("k")',
            description='Focus the "work item key" input widget',
            show=False,
        ),
        Binding(
            key='f',
            action='focus_widget("f")',
            description='Focus the "created from" input widget',
            show=False,
        ),
        Binding(
            key='u',
            action='focus_widget("u")',
            description='Focus the "created until" input widget',
            show=False,
        ),
        Binding(
            key='o',
            action='focus_widget("o")',
            description='Focus the "Order By" selection widget',
            show=False,
        ),
        Binding(
            key='v',
            action='focus_widget("v")',
            description='Focus the Active Sprint Checkbox',
            show=False,
        ),
        Binding(
            key='j',
            action='focus_widget("j")',
            description='Focus the JQL expression input widget',
            show=False,
        ),
        Binding(
            key='1',
            action='focus_widget("1")',
            description='Focus the Search Results widget',
            show=False,
        ),
        Binding(
            key='2',
            action='focus_widget("2")',
            description='Focus the Description tab widget',
            show=False,
        ),
        Binding(
            key='3',
            action='focus_widget("3")',
            description='Focus the Details tab widget',
            show=False,
        ),
        Binding(
            key='4',
            action='focus_widget("4")',
            description='Focus the Comments tab widget',
            show=False,
        ),
        Binding(
            key='5',
            action='focus_widget("5")',
            description='Focus the Related tab widget',
            show=False,
        ),
        Binding(
            key='6',
            action='focus_widget("6")',
            description='Focus the Attachments tab widget',
            show=False,
        ),
        Binding(
            key='7',
            action='focus_widget("7")',
            description='Focus the Links tab widget',
            show=False,
        ),
        Binding(
            key='8',
            action='focus_widget("8")',
            description='Focus the Subtasks tab widget',
            show=False,
        ),
        Binding(
            key='ctrl+n',
            action='create_work_item',
            description='New Work Item',
            show=True,
            key_display='^n',
        ),
    ]

    def __init__(
        self,
        api: APIController | None = None,
        project_key: str | None = None,
        user_account_id: str | None = None,
        jql_expression_id: int | None = None,
        work_item_key: str | None = None,
    ):
        super().__init__()
        self.api = APIController() if not api else api
        """The API instance used by the screen to interact with the Jira REST API via a an API controller."""
        self.available_users: list[tuple[str, str]] = []
        """The list of available users."""
        self.available_issues_status: list[tuple[str, str]] = []
        self.initial_project_key = project_key
        """A project key to set as the initial value of the projects dropdown widget."""
        self.initial_work_item_key = work_item_key
        """A work item key to set as the initial value of the work-item-key widget."""
        """Pre-selected project key. This is passed during the initialization of the application."""
        self.initial_assignee_account_id = user_account_id
        """Pre-selected user/assignee account id. This is passed during the initialization of the application."""
        self.initial_jql_expression_id = jql_expression_id
        """Pre-selected JQL expression ID to load into the JQL expression widget on start-up."""
        self.logger = logging.getLogger(LOGGER_NAME)

    @property
    def project_selector(self) -> ProjectSelectionInput:
        return self.query_one(ProjectSelectionInput)

    @property
    def issue_status_selector(self) -> IssueStatusSelectionInput:
        return self.query_one(IssueStatusSelectionInput)

    @property
    def issue_type_selector(self) -> IssueTypeSelectionInput:
        return self.query_one(IssueTypeSelectionInput)

    @property
    def users_selector(self) -> UserSelectionInput:
        return self.query_one(UserSelectionInput)

    @property
    def run_button(self) -> Button:
        return self.query_one('#run-button', expect_type=Button)

    @property
    def tabs(self) -> TabbedContent:
        return self.query_one(TabbedContent)

    @property
    def search_results_table(self) -> IssuesSearchResultsTable:
        return self.query_one(IssuesSearchResultsTable)

    @property
    def search_results_container(self) -> SearchResultsContainer:
        return self.query_one(SearchResultsContainer)

    @property
    def issue_details_widget(self) -> IssueDetailsWidget:
        return self.query_one(IssueDetailsWidget)

    @property
    def issue_comments_widget(self) -> IssueCommentsWidget:
        return self.query_one(IssueCommentsWidget)

    @property
    def related_issues_widget(self) -> RelatedIssuesWidget:
        return self.query_one(RelatedIssuesWidget)

    @property
    def issue_summary_widget(self) -> IssueSummaryWidget:
        return self.query_one(IssueSummaryWidget)

    @property
    def issue_description_widget(self) -> IssueDescriptionWidget:
        return self.query_one(IssueDescriptionWidget)

    @property
    def issue_remote_links_widget(self) -> IssueRemoteLinksWidget:
        return self.query_one(IssueRemoteLinksWidget)

    @property
    def issue_child_work_items_widget(self) -> IssueChildWorkItemsWidget:
        return self.query_one(IssueChildWorkItemsWidget)

    @property
    def issue_attachments_widget(self) -> IssueAttachmentsWidget:
        return self.query_one(IssueAttachmentsWidget)

    @property
    def issue_key_input(self) -> WorkItemInputWidget:
        return self.query_one('#input_issue_key', expect_type=WorkItemInputWidget)

    @property
    def jql_expression_input(self) -> JQLSearchWidget:
        return self.query_one('#input_search_term', expect_type=JQLSearchWidget)

    @property
    def order_by_widget(self) -> OrderByWidget:
        return self.query_one(OrderByWidget)

    @property
    def active_sprint_checkbox(self) -> ActiveSprintCheckbox:
        return self.query_one(ActiveSprintCheckbox)

    @property
    def issue_date_from_input(self) -> IssueSearchCreatedFromWidget:
        return self.query_one('#input_date_from', expect_type=IssueSearchCreatedFromWidget)

    @property
    def issue_date_until_input(self) -> IssueSearchCreatedUntilWidget:
        return self.query_one('#input_date_until', expect_type=IssueSearchCreatedUntilWidget)

    def compose(self) -> ComposeResult:
        """Composes the widgets of the application's main screen.

        Returns:
            An instance of `ComposeResult`.
        """

        yield Header(id='app-header', icon='*')
        with Vertical(id='main-container'):
            with HorizontalGroup():
                yield ProjectSelectionInput(projects=[])
                yield IssueTypeSelectionInput(types=[])
                yield IssueStatusSelectionInput(statuses=[])
                yield UserSelectionInput(users=[])
            with ItemGrid(classes='bottom-search-bar'):
                yield WorkItemInputWidget(value=self.initial_work_item_key)
                yield IssueSearchCreatedFromWidget()
                yield IssueSearchCreatedUntilWidget()
                yield OrderByWidget(WorkItemsSearchOrderBy.to_choices())
                yield ActiveSprintCheckbox()
                yield JQLSearchWidget()
                yield Button('Search', id='run-button', variant='success', disabled=False)
            with Horizontal():
                with SearchResultsContainer(id='search_results_container'):
                    yield IssuesSearchResultsTable()
                with TabbedContent(id='tabs'):
                    with TabPane(title='Description', classes='summary-description-container'):
                        yield IssueSummaryWidget()
                        yield Rule(classes='summary-description-rule')
                        with VerticalScroll():
                            yield IssueDescriptionWidget()
                    with TabPane(title='Details'):
                        yield IssueDetailsWidget()  # will contain a form to view and update some of the fields of the issue
                    with TabPane(title='Comments'):
                        yield IssueCommentsWidget()
                    with TabPane(title='Related'):
                        yield RelatedIssuesWidget()
                    with TabPane(title='Attachments'):
                        yield IssueAttachmentsWidget()
                    with TabPane(title='Links'):
                        yield IssueRemoteLinksWidget()
                    with TabPane(title='Subtasks'):
                        yield IssueChildWorkItemsWidget()
        yield Footer()

    async def on_mount(self) -> None:
        # fetch the list of projects
        self.run_worker(self.fetch_projects())
        # if there is an initial value for the project key the worker that fetches the projects will trigger fetching
        # users, status codes and work item types after the project dropdown is updated with the selection.
        # the same happens when the user configures the app to fetch only projects on start up
        if not CONFIGURATION.get().on_start_up_only_fetch_projects and not self.initial_project_key:
            # in this case there is no need to fetch users, status codes and work item types
            self.run_worker(self.fetch_issue_types())
            self.run_worker(self.fetch_statuses())
            self.run_worker(self.fetch_users())

        if self.initial_jql_expression_id and (
            pre_defined_jql_expressions := CONFIGURATION.get().pre_defined_jql_expressions
        ):
            if (
                expression_data := pre_defined_jql_expressions.get(self.initial_jql_expression_id)
            ) and (expression := expression_data.get('expression')):
                self.jql_expression_input.expression = expression.replace('\n', ' ').replace(
                    '\t', ' '
                )

    async def fetch_projects(self) -> None:
        """Fetches the list of available projects.

        If the user pre-selects a project using the configuration setting `default_project_key_or_id` or by passing the
        `--project-key` in the CLI command `jiratui ui --project-key` then the application will only fetch that
        project. This speeds up the launching of the app because less API requests are needed.

        If on the other hand, no project key is pre-selected then the application will fetch all available
        projects. This may require multiple API requests; making the application launch slower.

        If a project is pre-selected the application will pre-select the project from the dropdown list.
        a value if required.

        If no project is found then the application will leave the dropdown empty.

        Returns:
            Nothing.
        """
        project_keys = [self.initial_project_key] if self.initial_project_key else None
        response: APIControllerResponse = await self.api.search_projects(keys=project_keys)
        if not response.success:
            self.notify(f'Failed to fetch the list of projects: {response.error}')
        projects = response.result or []
        projects.sort(key=lambda x: x.name)
        self.project_selector.projects = {
            'projects': projects,
            'selection': self.initial_project_key,
        }

    async def fetch_statuses(self) -> list[tuple[str, str]]:
        """Retrieves the valid status codes depending on the selected project and type of work item.

        Returns:
            A list of tuples with the name and id of every project status code.
        """
        self.logger.info('Fetching status codes')
        if self.project_selector.selection:
            return await self._fetch_project_statuses(self.project_selector.selection)
        response: APIControllerResponse = await self.api.status()
        if not response.success:
            self.logger.error(
                'Failed to fetch the available status codes', extra={'error': response.error}
            )
            return []
        seen_statuses: set[str] = set()
        statuses: list[tuple[str, str]] = []
        for status in response.result or []:
            if str(status.id) not in seen_statuses:
                seen_statuses.add(str(status.id))
                statuses.append((status.name, str(status.id)))
        return sorted(statuses, key=lambda x: x[0])

    async def _fetch_project_statuses(self, project_key: str) -> list[tuple[str, str]]:
        """Fetches the status codes applicable to a project and optionally to the type of issue selected by the user.

        Args:
            project_key: the key of the project whose status codes we want to retrieve.

        Returns:
            A list of tuples with the name and id of every project status code.
        """

        response: APIControllerResponse = await self.api.get_project_statuses(project_key)
        if not response.success:
            self.logger.error(
                'Failed to retrieve the status codes associated to the project',
                extra={'error': response.error, 'project_key': project_key},
            )
            return []
        result = response.result or {}
        if self.issue_type_selector.selection:
            record: dict = result.get(self.issue_type_selector.selection, {})
            return sorted(
                [(status.name, str(status.id)) for status in record.get('issue_type_statuses', [])],
                key=lambda x: x[0],
            )
        statuses: list[tuple[str, str]] = []
        # make sure we don't have duplicate status codes/ids in the select dropdown
        seen_statuses: set[str] = set()
        for _issue_type_id, data in result.items():
            for status in data.get('issue_type_statuses', []):
                if str(status.id) not in seen_statuses:
                    seen_statuses.add(str(status.id))
                    statuses.append((status.name, str(status.id)))
        return sorted(statuses, key=lambda x: x[0])

    async def fetch_issue_types(self) -> list[tuple[str, str]]:
        """Retrieves the list of type of work items.

        If a project is selected then it will retrieve the types of work items associated to the project; otherwise it
        will retrieve all the possible types of work items.

        Returns:
            A list of tuples with the id of the type of issue and the name of the type of issue.
        """
        self.logger.info('Fetching type of work items')
        types: list[IssueType]
        if self.project_selector.selection:
            response: APIControllerResponse = await self.api.get_issue_types_for_project(
                self.project_selector.selection
            )
            if not response.success:
                return []
            types = response.result or []
            types.sort(key=lambda x: x.name)
            return [(item.name, item.id) for item in types or []]

        # retrieve all available types of work items
        response = await self.api.get_issue_types()
        if not response.success:
            return []
        types = response.result or []
        types.sort(key=lambda x: x.name)
        work_item_types: list[tuple[str, str]] = []
        for item in types:
            if item.scope_project:
                name = f'({item.scope_project.name}) {item.name}'
            else:
                name = item.name
            work_item_types.append((name, item.id))
        return work_item_types

    async def fetch_users(self) -> list[JiraUser]:
        """Retrieves a list of users.

        If a project is selected from the projects dropdown then this will retrieve all the users associated to the
        project.

        Returns:
            A list of `JiraUser` instances.
        """
        self.logger.info('Fetching users')
        return await self.get_users(project_key=self.project_selector.selection)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == 'fetch_statuses':
            self.available_issues_status = event.worker.result or []
            self.issue_status_selector.statuses = self.available_issues_status
        elif event.worker.name == 'fetch_issue_types':
            self.issue_type_selector.set_options(event.worker.result or [])
        elif event.worker.name == 'fetch_users':
            users: list[JiraUser] = event.worker.result or []
            self.available_users = [(user.display_name, user.account_id) for user in users]
            self.users_selector.users = {
                'users': users,
                'selection': self.initial_assignee_account_id,
            }

    @on(Select.Changed, '#jira-project-selector')
    async def handle_project_selection(self, event: Select.Changed) -> None:
        """Handles the selection of a project.

        This will trigger the actions to fetch users, types of issues and applicable project status codes.

        Args:
            event: the event triggered by the selection.

        Returns:
            Nothing.
        """
        # fetch issue types for the project
        self.run_worker(self.fetch_issue_types())
        # fetch users for the project
        self.run_worker(self.fetch_users())
        # fetch valid status codes
        self.run_worker(self.fetch_statuses())

    async def get_users(self, project_key: str | None = None) -> list[JiraUser]:
        if project_key:
            # fetch the users that can be assigned to items in this project
            response: APIControllerResponse = await self.api.search_users_assignable_to_projects(
                project_keys=[project_key],
                active=True,
            )
            if not response.success:
                self.logger.error(
                    'Failed to retrieve the users assignable to the project',
                    extra={'error': response.error, 'project_key': project_key},
                )
                return []
            return response.result or []

        if group_id := CONFIGURATION.get().jira_user_group_id:
            # fetch the users that belong to this Jira user group ID
            response = await self.api.list_all_active_users_in_group(group_id=group_id)
            if not response.success:
                self.logger.error(
                    'Failed to retrieve the active users in the selected user group',
                    extra={'error': response.error, 'group_id': group_id},
                )
                return []
            return response.result or []
        self.notify(
            'Unable to find users. Check if the configuration option "jira_user_group_id" is set.',
            severity='warning',
            title='Find Users',
        )
        return []

    async def _search_work_items(
        self,
        next_page_token: str | None = None,
        calculate_total: bool = True,
    ) -> WorkItemSearchResult:
        # search work items based on search criteria selected by the user
        search_field_status: int | None = None
        if value := self.issue_status_selector.selection:
            search_field_status = int(value)

        search_field_created_from: date | None = None
        if value := self.issue_date_from_input.value:
            search_field_created_from = datetime.fromisoformat(value).date()

        search_field_created_until: date | None = None
        if value := self.issue_date_until_input.value:
            search_field_created_until = datetime.fromisoformat(value).date()

        search_field_assignee: str | None = None
        if value := self.users_selector.selection:
            search_field_assignee = value

        search_field_issue_type: int | None = None
        if value := self.issue_type_selector.selection:
            search_field_issue_type = value

        project_key: str | None = None
        if value := self.project_selector.selection:
            project_key = value

        order_by = (
            WorkItemsSearchOrderBy(self.order_by_widget.selection)
            if self.order_by_widget.selection
            else None
        )

        # search work items by different criteria
        response: APIControllerResponse = await self.api.search_issues(
            project_key=project_key,
            created_from=search_field_created_from,
            created_until=search_field_created_until,
            status=search_field_status,
            assignee=search_field_assignee,
            issue_type=search_field_issue_type,
            search_in_active_sprint=self.active_sprint_checkbox.value,
            jql_query=self.jql_expression_input.value,
            next_page_token=next_page_token,
            limit=CONFIGURATION.get().search_results_per_page,
            order_by=order_by,
        )
        if not response.success:
            self.notify(
                'There was an error while performing the search',
                severity='warning',
                title='Work Item Search',
            )
            WorkItemSearchResult(total=0, start=0, end=0)

        result: JiraIssueSearchResponse = response.result
        estimated_total_issues: int | None = None
        if calculate_total:
            counting: APIControllerResponse = await self.api.count_issues(
                project_key=project_key,
                created_from=search_field_created_from,
                created_until=search_field_created_until,
                status=search_field_status,
                assignee=search_field_assignee,
                issue_type=search_field_issue_type,
                jql_query=self.jql_expression_input.value,
            )
            if counting.success:
                estimated_total_issues = counting.result
            else:
                estimated_total_issues = 0
                self.notify(
                    'Failed to calculate the number of work items',
                    title='Work Items Search',
                    severity='warning',
                )

        issues_count = len(result.issues)
        return WorkItemSearchResult(
            response=result,
            total=estimated_total_issues,
            start=1 if issues_count else 0,
            end=issues_count,
        )

    async def _search_single_issue(self, issue_key: str) -> WorkItemSearchResult:
        response: APIControllerResponse = await self.api.get_issue(
            issue_id_or_key=issue_key, fields=['summary', 'status', 'issuetype']
        )
        if not response.success:
            self.notify(
                f'There was an error while fetching the selected work item {issue_key}',
                title='Work Items Search',
                severity='error',
            )
            return WorkItemSearchResult(total=0, start=0, end=0)
        if not response.result:
            self.notify(
                f'The selected work item {issue_key} was not found',
                title='Work Items Search',
                severity='error',
            )
            return WorkItemSearchResult(total=0, start=0, end=0)
        total = len(response.result.issues or [])
        return WorkItemSearchResult(response=response.result, total=total, start=total, end=total)

    async def search_issues(self, next_page_token: str | None = None) -> None:
        """Searches work items.

        If a specific issue is specified in the Issue Key input widget then the app searches the details of that issue
        only. If, on the other hand, no issue is specified then the app searches issues based on the given criteria.

        Once the results are retrieved this method will update a reactive attribute in the search results table to
        update the results.

        Args:
            next_page_token: a token that identifies the next page of results.

        Returns:
            Nothing.
        """

        # clear current results page
        table = self.search_results_table
        table.clear(columns=True)

        results: WorkItemSearchResult
        # search single issue
        if (value := self.issue_key_input.value) and value.strip():
            results = await self._search_single_issue(value.strip())
        else:
            results = await self._search_work_items(next_page_token)

        # update the result set in the table
        table.search_results = results.response

        # update results count for the table's container
        self.search_results_container.pagination = {
            'total': results.total,
            'current_page_number': self.search_results_table.page,
        }

    @on(Button.Pressed, '#run-button')
    async def handle_run_button(self) -> None:
        self.run_worker(self.action_search())

    async def action_search(self) -> None:
        """Handles the event that happens when the user presses the "search" button or "ctrl+r"."""
        self.run_button.loading = True
        # clear the description pane
        await self.issue_description_widget.update('')
        self.issue_summary_widget.update('')
        # clear the details pane
        self.issue_details_widget.clear_form = True
        # clear the comments
        self.issue_comments_widget.comments = None
        self.issue_comments_widget.issue_key = None
        # clear related issues
        self.related_issues_widget.issue_key = None
        self.related_issues_widget.issues = None
        # clear the web links
        self.issue_remote_links_widget.issue_key = None
        # clear the attachments
        self.issue_attachments_widget.attachments = None
        self.issue_attachments_widget.issue_key = None
        # reset the current page
        self.search_results_table.page = 1
        # clear the token-based pagination control
        self.search_results_table.token_by_page = {}
        next_page_token: str | None = self.search_results_table.token_by_page.get(
            self.search_results_table.page
        )
        # search the work items that match the criteria
        self.run_worker(self.search_issues(next_page_token), exclusive=True)
        self.run_button.loading = False

    def action_focus_widget(self, key: str) -> None:
        """Focuses a widget based on the key pressed by the user.

        Args:
            key: the key the user pressed in the UI.

        Returns:
            Nothing.
        """
        if key == 'p':
            self.set_focus(self.project_selector)
        elif key == 't':
            self.set_focus(self.issue_type_selector)
        elif key == 's':
            self.set_focus(self.issue_status_selector)
        elif key == 'a':
            self.set_focus(self.users_selector)
        elif key == 'k':
            self.set_focus(self.issue_key_input)
        elif key == 'f':
            self.set_focus(self.issue_date_from_input)
        elif key == 'u':
            self.set_focus(self.issue_date_until_input)
        elif key == 'o':
            self.set_focus(self.order_by_widget)
        elif key == 'v':
            self.set_focus(self.active_sprint_checkbox)
        elif key == 'j':
            self.set_focus(self.jql_expression_input)
        elif key == '2':
            self.set_focus(self.issue_description_widget)
        elif key == '3':
            self.set_focus(self.issue_details_widget)
        elif key == '4':
            self.set_focus(self.issue_comments_widget)
        elif key == '5':
            self.set_focus(self.related_issues_widget)
        elif key == '6':
            self.set_focus(self.issue_attachments_widget)
        elif key == '7':
            self.set_focus(self.issue_remote_links_widget)
        elif key == '8':
            self.set_focus(self.issue_child_work_items_widget)
        elif key == '1':
            self.set_focus(self.search_results_table)

    async def action_create_work_item(self) -> None:
        """Handles the event to create a new work item."""
        await self.app.push_screen(
            AddWorkItemScreen(
                project_key=self.project_selector.selection,
                reporter_account_id=CONFIGURATION.get().jira_account_id,
            ),
            callback=self.create_work_item,
        )

    async def create_work_item(self, data: dict) -> None:
        """Handles the event to create a work item after the user clicks on the "save" button in the create-work-item
        screen.

        Args:
            data: a dictionary with the details of the fields and values to create the item.

        Returns:
            Nothing.
        """

        if data:
            response: APIControllerResponse = await self.api.create_work_item(data)
            if response.success:
                self.notify(
                    f'Work item {response.result.key} created successfully',
                    title='Create Work Item',
                )
            else:
                self.logger.error('Failed to create the work item', extra={'error': response.error})
                self.notify(
                    f'Failed to create the work item: {response.error}',
                    severity='error',
                    title='Create Work Item',
                )

    async def on_key(self, event: Key) -> None:
        """Handles events triggered every time the user presses a key.

        The only events being handled are the keystrokes related to the pagination of search results.

        Args:
            event: the event with the details of the key pressed.

        Returns:
            Nothing.
        """
        if event.key in ['alt+right']:
            # fetch contents of page self.page + 1
            if next_page_token := self.search_results_table.token_by_page.get(
                self.search_results_table.page + 1
            ):
                self.search_results_table.page += 1
                await self.search_issues(next_page_token)
        elif event.key in ['alt+left']:
            if self.search_results_table.page > 1:
                # fetch contents of page self.page - 1
                next_page_token = self.search_results_table.token_by_page.get(
                    self.search_results_table.page - 1
                )
                self.search_results_table.page -= 1
                await self.search_issues(next_page_token)

    async def _setup_work_item_description(self, description: dict | list) -> None:
        if description:
            try:
                await self.issue_description_widget.update(adf2md(description))
            except Exception:
                await self.issue_description_widget.update('Unable to display the description.')
        else:
            await self.issue_description_widget.update('')

    async def retrieve_issue_subtasks(self, issue_key: str) -> None:
        if issue_key:
            self.issue_child_work_items_widget.issue_key = issue_key
            response: APIControllerResponse = await self.api.search_issues(
                jql_query=f'parent={issue_key}',
                fields=['id', 'key', 'status', 'summary', 'issuetype', 'assignee'],
            )
            if not response.success:
                self.logger.error(
                    'Unable to retrieve the sub tasks of the work item',
                    extra={'error': response.error, 'issue_key': issue_key},
                )
                self.notify(
                    'Unable to retrieve the sub tasks of the work item',
                    severity='warning',
                    title='Work Item Search',
                )
            else:
                self.issue_child_work_items_widget.issues = response.result.issues

    async def fetch_issue(self, selected_work_item_key: str) -> None:
        """Retrieves the details of a work item selected by the user in the search results.

        This is triggered from the datatable that holds the search results:
        `jiratui.widgets.search.IssuesSearchResultsTable`

        Every time a user selects a work item in the search results the application will do the following:

        - retrieve the details of the work item by sending a request to the
        API's [get_issue](#jiratui.api_controller.controller.APIController.get_issue) method.

        - update the information on the description tab (summary and description)

        - retrieve the subtasks associated to the selected work item

        - update the data in all the other tabs

        Args:
            selected_work_item_key: the key if the work item selected by the user from the search results datatable.

        Returns:
            Nothing
        """
        if not selected_work_item_key:
            self.notify(
                'You need to select a work item before fetching its details.',
                title='Find Work Item',
                severity='error',
            )
            return

        # step 1: fetch issue
        response: APIControllerResponse = await self.api.get_issue(
            issue_id_or_key=selected_work_item_key
        )
        if not response.success:
            self.notify(
                'Unable to find the selected work item', title='Find Work Item', severity='error'
            )
            return

        result: JiraIssueSearchResponse = response.result
        work_item: JiraIssue = result.issues[0]
        # step 2: populate description tab
        self.issue_summary_widget.update(work_item.summary)
        self.run_worker(self._setup_work_item_description(work_item.description))

        # step 3: set up the details tab
        # set the assignable users for the selected work item
        self.issue_details_widget.available_users = self.available_users
        # set the work item
        self.issue_details_widget.issue = work_item

        # step 4: populate the related-issues tab
        self.related_issues_widget.issue_key = work_item.key
        self.related_issues_widget.issues = work_item.related_issues

        # step 5: populate comments tab
        self.issue_comments_widget.issue_key = work_item.key
        self.issue_comments_widget.comments = work_item.comments

        # step 6: populate attachments tab
        self.issue_attachments_widget.issue_key = work_item.key
        self.issue_attachments_widget.attachments = work_item.attachments

        # fetch the issue's web links
        if CONFIGURATION.get().show_issue_web_links:
            self.issue_remote_links_widget.issue_key = work_item.key

        # fetch sub-tasks
        self.run_worker(self.retrieve_issue_subtasks(work_item.key))
