from dataclasses import dataclass
from datetime import date
import logging

from dateutil.parser import isoparse  # type:ignore[import-untyped]
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Select, TabbedContent, TabPane
from textual.worker import Worker

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.constants import FULL_TEXT_SEARCH_DEFAULT_MINIMUM_TERM_LENGTH, LOGGER_NAME
from jiratui.models import (
    IssueType,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraUser,
    WorkItemsSearchOrderBy,
)
from jiratui.utils.urls import build_external_url_for_issue
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
from jiratui.widgets.git_screen import GitScreen
from jiratui.widgets.related_work_items.related_issues import RelatedIssuesWidget
from jiratui.widgets.remote_links.links import IssueRemoteLinksWidget
from jiratui.widgets.search import (
    DataTableSearchInput,
    IssuesSearchResultsTable,
    SearchResultsContainer,
)
from jiratui.widgets.subtasks import IssueChildWorkItemsWidget
from jiratui.widgets.text_search import TextSearchScreen
from jiratui.widgets.work_item_details.details import IssueDetailsWidget
from jiratui.widgets.work_item_info.info import WorkItemInfoContainer


@dataclass
class WorkItemSearchResult:
    total: int = 0
    start: int = 0
    end: int = 0
    response: JiraIssueSearchResponse | None = None


class MainScreen(Screen):
    """The main screen of the application."""

    BINDINGS = [
        Binding(
            key='/',
            action='find_by_text',
            description='Find',
            key_display='/',
            tooltip='Find items using full-text search',
            show=True,
        ),
        Binding(
            key='ctrl+r',
            action='search',
            description='Search',
            tooltip='Search items by search criteria',
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
            description='Focus the Info tab widget',
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
            description='New Issue',
            show=True,
            key_display='^n',
        ),
        Binding(
            key='ctrl+k',
            action='copy_issue_key',
            description='Copy Key',
            show=True,
            key_display='^k',
            tooltip='Copy the work item key',
        ),
        Binding(
            key='ctrl+j',
            action='copy_issue_url',
            description='Copy URL',
            show=True,
            key_display='^j',
            tooltip='Copy the work item URL',
        ),
        Binding(
            key='ctrl+g',
            action='create_git_branch',
            description='Git',
            show=True,
            key_display='^g',
            tooltip='Creates a Git branch with the key of the work item',
        ),
    ]

    def __init__(
        self,
        api: APIController | None = None,
        project_key: str | None = None,
        user_account_id: str | None = None,
        jql_expression_id: int | None = None,
        work_item_key: str | None = None,
        focus_item_on_startup: int | None = None,
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
        self.initial_jql_expression_id: int | None = jql_expression_id
        """Pre-selected JQL expression ID to load into the JQL expression widget on start-up. This JQL expression will
        be used for searching issues when the user does not select any filter/criteria in the UI. """
        self.focus_item_on_startup = focus_item_on_startup
        """The position of the work item to focus and open on startup. Requires search_on_startup to be enabled."""
        self.logger = logging.getLogger(LOGGER_NAME)
        # maps keys to widget ids to enable quick navigation
        self.keys_widget_ids_mapping: dict[str, str] = {
            'p': '#jira-project-selector',
            't': '#jira-issue-types-selector',
            's': '#jira-issue-status-selector',
            'a': '#jira-users-selector',
            'k': '#input_issue_key',
            'f': '#input_date_from',
            'u': '#input_date_until',
            'o': '#issue-search-order-by-selector',
            'v': '#active-sprint-checkbox',
            'j': '#input_search_term',
            '1': '#search_results',
            '2': '#work_item_info_container',
            '3': '#issue_details',
            '4': '#issue_comments',
            '5': '#related_issues',
            '6': '#attachments',
            '7': '#issue_remote_links',
            '8': '#issue_subtasks',
        }

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
    def search_results_filter_input(self) -> DataTableSearchInput:
        return self.query_one(DataTableSearchInput)

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
    def issue_info_container(self) -> WorkItemInfoContainer:
        return self.query_one(WorkItemInfoContainer)

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

        # Only render header if tui_custom_title is not explicitly set to empty string
        config = CONFIGURATION.get()
        should_show_header = True
        if config.tui_custom_title is not None and config.tui_custom_title == '':
            should_show_header = False

        if should_show_header:
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
                yield OrderByWidget(
                    WorkItemsSearchOrderBy.to_choices(),
                    initial_value=CONFIGURATION.get().search_results_default_order.value,
                )
                yield ActiveSprintCheckbox(value=CONFIGURATION.get().active_sprint_on_startup)
                yield JQLSearchWidget()
                yield Button(
                    'Search',
                    id='run-button',
                    variant='warning',
                    disabled=False,
                    flat=True,
                    compact=True,
                )
            with Horizontal():
                with SearchResultsContainer(id='search_results_container'):
                    yield DataTableSearchInput()
                    yield IssuesSearchResultsTable()
                with TabbedContent(id='tabs'):
                    with TabPane(title='Info', classes='summary-description-container'):
                        yield WorkItemInfoContainer()
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
        yield Footer(show_command_palette=False)

    async def on_mount(self) -> None:
        # fetch the list of projects
        workers: list[Worker] = [self.run_worker(self.fetch_projects())]
        # if there is an initial value for the project key the worker that fetches the projects will trigger fetching
        # users, status codes and work item types after the project dropdown is updated with the selection.
        # the same happens when the user configures the app to fetch only projects on start up
        if not CONFIGURATION.get().on_start_up_only_fetch_projects and not self.initial_project_key:
            # in this case we need to fetch users, status codes and work item types
            self.run_worker(self.fetch_issue_types())
            self.run_worker(self.fetch_statuses())
            workers.append(self.run_worker(self.fetch_users()))

        if self.initial_jql_expression_id and (
            pre_defined_jql_expressions := CONFIGURATION.get().pre_defined_jql_expressions
        ):
            if (
                expression_data := pre_defined_jql_expressions.get(self.initial_jql_expression_id)
            ) and (expression := expression_data.get('expression')):
                self.jql_expression_input.expression = expression.replace('\n', ' ').replace(
                    '\t', ' '
                )

        # Trigger search on startup if enabled
        if CONFIGURATION.get().search_on_startup:
            # make sure to wait for the related workers so the method that searches work items have the necessary
            # filters set up, e.g. the selected project (if any) and the selected users (if any)
            await self.app.workers.wait_for_complete(workers)
            search_worker = self.run_worker(self.action_search(), exclusive=True)

            # If focus_item_on_startup is specified, wait for search to complete and then focus the item
            if self.focus_item_on_startup:
                await self.app.workers.wait_for_complete([search_worker])
                self.run_worker(self._focus_item_after_startup(self.focus_item_on_startup))

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
        project_keys = [self.initial_project_key] if self.initial_project_key else []
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

        if (group_id := CONFIGURATION.get().jira_user_group_id) and CONFIGURATION.get().cloud:
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
            'Unable to find users. Check if the configuration option "jira_user_group_id" is set and that you are using Jira Cloud.',
            severity='warning',
            title='Find Users',
        )
        return []

    async def _search_work_items(
        self,
        next_page_token: str | None = None,
        calculate_total: bool = True,
        search_term: str | None = None,
        page: int | None = None,
    ) -> WorkItemSearchResult:
        """Searches work items.

        Args:
            next_page_token: if provided then the results page with this token wil be retrieved. This is used for
            pagination of results in Jira Cloud Platform.
            calculate_total: if `True` the method will attempt to estimate the total number of results that match the
            search query.
            search_term: this is the search term used for ull-text search.
            page: if provided, then the results page with this number wil/ be retrieved. This is used for
            pagination of results in Jira Data Center Platform.

        Returns:
            An instance of `WorkItemSearchResult` with the results of the search.
        """
        search_field_status: int | None = None
        if value := self.issue_status_selector.selection:
            search_field_status = int(value)

        search_field_created_from: date | None = None
        if value := self.issue_date_from_input.value:
            search_field_created_from = isoparse(value).date()

        search_field_created_until: date | None = None
        if value := self.issue_date_until_input.value:
            search_field_created_until = isoparse(value).date()

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

        # build the JQL query to search items based on a user-provided JQL query expression or a search term.
        jql_query: str | None = self._build_jql_query(
            search_term=search_term,
            jql_expression=self.jql_expression_input.value,
            use_advance_search=CONFIGURATION.get().enable_advanced_full_text_search,
        )

        # search work items by different criteria
        response: APIControllerResponse
        if CONFIGURATION.get().cloud:
            response = await self.api.search_issues(
                project_key=project_key,
                created_from=search_field_created_from,
                created_until=search_field_created_until,
                status=search_field_status,
                assignee=search_field_assignee,
                issue_type=search_field_issue_type,
                search_in_active_sprint=self.active_sprint_checkbox.value,
                jql_query=jql_query,
                next_page_token=next_page_token,
                limit=CONFIGURATION.get().search_results_per_page,
                order_by=order_by,
            )
        else:
            response = await self.api.search_issues_by_page_number(
                project_key=project_key,
                created_from=search_field_created_from,
                created_until=search_field_created_until,
                status=search_field_status,
                assignee=search_field_assignee,
                issue_type=search_field_issue_type,
                search_in_active_sprint=self.active_sprint_checkbox.value,
                jql_query=jql_query,
                page=page,
                limit=CONFIGURATION.get().search_results_per_page,
                order_by=order_by,
            )

        if not response.success or response.result is None:
            self.notify(
                'There was an error while performing the search',
                severity='warning',
                title='Work Item Search',
            )
            return WorkItemSearchResult(total=0, start=0, end=0)

        # estimation of search results count is only available in Jira Cloud
        if not CONFIGURATION.get().cloud:
            calculate_total = False

        result: JiraIssueSearchResponse = response.result
        estimated_total_issues: int = 0
        if calculate_total:
            counting: APIControllerResponse = await self.api.count_issues(
                project_key=project_key,
                created_from=search_field_created_from,
                created_until=search_field_created_until,
                status=search_field_status,
                assignee=search_field_assignee,
                issue_type=search_field_issue_type,
                jql_query=jql_query,
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

        # the actual number of results
        issues_count = len(result.issues)
        return WorkItemSearchResult(
            response=result,
            total=estimated_total_issues if estimated_total_issues else 0,
            start=1 if issues_count else 0,
            end=issues_count,
        )

    @staticmethod
    def _build_jql_query(
        search_term: str | None = None,
        jql_expression: str | None = None,
        use_advance_search: bool = False,
    ) -> str | None:
        if search_term:
            if use_advance_search:
                return f'text ~ "{search_term}"'
            return f'summary ~ "{search_term}" OR description ~ "{search_term}"'
        elif jql_expression:
            return jql_expression
        return None

    async def _search_single_issue(self, issue_key: str) -> WorkItemSearchResult:
        response: APIControllerResponse = await self.api.get_issue(
            issue_id_or_key=issue_key, fields=['summary', 'status', 'issuetype', 'parent']
        )
        if not response.success:
            self.notify(
                response.error or 'Unable to fetch the given issue',
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

    async def search_issues(
        self,
        next_page_token: str | None = None,
        search_term: str | None = None,
        page: int | None = None,
    ) -> None:
        """Searches work items.

        If a specific issue is specified in the Issue Key input widget then the app searches the details of that issue
        only. If, on the other hand, no issue is specified then the app searches issues based on the given criteria.

        Once the results are retrieved this method will update a reactive attribute in the search results table to
        update the results.

        Args:
            next_page_token: a token that identifies the next page of results.
            search_term: a search term to search items using full-text search.
            page: the page number to fetch results; this is only supported for Jira Data Center (aka. on-premises)

        Returns:
            Nothing.
        """
        self.run_button.loading = True
        results: WorkItemSearchResult
        if (value := self.issue_key_input.value) and isinstance(value, str) and value.strip():
            # search single issue
            results = await self._search_single_issue(value.strip())
        else:
            results = await self._search_work_items(
                next_page_token=next_page_token, search_term=search_term, page=page
            )
        # set the data in the results table
        table = self.search_results_table
        # store the initial results set in the table to handle local searches
        table.set_initial_results_set(results.response)
        # update the result set in the table
        table.search_results = results.response
        table.focus()

        # update results count for the table's container
        self.search_results_container.pagination = {
            'total': results.total,
            'current_page_number': self.search_results_table.page,
        }
        self.run_button.loading = False

    @on(Button.Pressed, '#run-button')
    async def handle_run_button(self) -> None:
        self.run_worker(self.action_search())

    async def action_search(self, search_term: str | None = None) -> None:
        """Handles the event  when the user presses the "search" button or "ctrl+r"."""

        # clear the information pane
        self.issue_info_container.clear_information = True
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
        # Jira Cloud supports pagination based on a next page token; Jira Data Center (aka. on-premises) uses offset
        # to fetch pages.
        next_page_token: str | None = self.search_results_table.token_by_page.get(
            self.search_results_table.page
        )
        # search the work items that match the criteria
        self.run_worker(
            self.search_issues(
                next_page_token=next_page_token,
                search_term=search_term,
                page=self.search_results_table.page,
            ),
            exclusive=True,
        )

    def action_focus_widget(self, key: str) -> None:
        """Focuses a widget based on the key pressed by the user.

        Args:
            key: the key the user pressed in the UI.

        Returns:
            Nothing.
        """

        if widget_id := self.keys_widget_ids_mapping.get(key):
            if target_widget := self.query_one(widget_id):
                self.set_focus(target_widget)

    def action_copy_issue_url(self) -> None:
        """Copy to the clipboard the URL of the item currently selected in the search results."""
        if (table := self.search_results_table) and table.current_work_item_key:
            if url := build_external_url_for_issue(table.current_work_item_key):
                self.app.copy_to_clipboard(url)
                self.notify('Work item URL copied!')

    def action_copy_issue_key(self) -> None:
        """Copy to the clipboard the key of the item currently selected in the search results."""
        if (table := self.search_results_table) and table.current_work_item_key:
            self.app.copy_to_clipboard(self.search_results_table.current_work_item_key)
            self.notify('Work item Key copied!')

    def action_create_git_branch(self) -> None:
        """Opens up a modal screen to allow the user to create Git branches."""
        if (table := self.search_results_table) and table.current_work_item_key:
            self.run_worker(self._open_git_screen(table.current_work_item_key))

    async def _open_git_screen(self, work_item_key: str) -> None:
        await self.app.push_screen(GitScreen(work_item_key))

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
            if response.success and response.result:
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
                if response.result:
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
            issue_id_or_key=selected_work_item_key,
        )
        if not response.success or not response.result:
            self.notify(
                'Unable to find the selected work item', title='Find Work Item', severity='error'
            )
            return

        result: JiraIssueSearchResponse = response.result
        work_item: JiraIssue = result.issues[0]

        # step 2: populate information tab
        self.issue_info_container.issue = work_item

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

    async def request_text_search(self, value: str):
        value = value or ''
        if (value := value.strip()) and len(value) >= max(
            FULL_TEXT_SEARCH_DEFAULT_MINIMUM_TERM_LENGTH,
            int(CONFIGURATION.get().full_text_search_minimum_term_length),
        ):
            self.run_worker(self.action_search(search_term=value))
        else:
            self.notify('Nothing to search')

    async def action_find_by_text(self) -> None:
        """Opens a screen to allow the user to enter a term to search items by text."""
        await self.app.push_screen(TextSearchScreen(), self.request_text_search)

    async def _focus_item_after_startup(self, position: int) -> None:
        """Focuses and opens a work item at the specified position after startup search completes.

        Args:
            position: the 1-based position of the work item in the search results to focus and open.

        Returns:
            Nothing.
        """
        import asyncio

        # Get the search results table
        table = self.search_results_table

        # Wait for the table to be populated with results (with timeout)
        max_attempts = 50  # 5 seconds total
        attempt = 0
        row_count = 0

        while attempt < max_attempts:
            await self.app.animator.wait_for_idle()
            await asyncio.sleep(0.1)
            row_count = len(table.rows)
            if row_count > 0:
                break
            attempt += 1

        # Check if we timed out waiting for results
        if row_count == 0:
            self.notify(
                'Search results are empty or still loading.',
                severity='warning',
                title='Focus Work Item',
            )
            return

        # Check if the position is valid
        if position < 1 or position > row_count:
            self.notify(
                f'Position {position} is out of range. Search results contain {row_count} item(s).',
                severity='warning',
                title='Focus Work Item',
            )
            return

        # Convert 1-based position to 0-based index
        row_index = position - 1

        # Get the row key at this position
        row_keys = list(table.rows)
        row_key = row_keys[row_index]

        # Extract the work item key from the row
        row_key_value = str(row_key.value)
        work_item_key = None
        if '#' in row_key_value:
            _, work_item_key = row_key_value.split('#')

        # Move cursor to this row
        table.move_cursor(row=row_index)

        # Give a moment for the cursor to move
        await asyncio.sleep(0.1)
        await self.app.animator.wait_for_idle()

        # Trigger the row selection action (simulates pressing Enter)
        # This will fire the on_data_table_row_selected event which calls fetch_issue
        table.action_select_cursor()

        # Wait for the issue to be fetched and rendered
        await asyncio.sleep(0.3)
        await self.app.animator.wait_for_idle()

        # Shift focus to the issue info container so user can interact with the issue
        self.issue_info_container.focus()
