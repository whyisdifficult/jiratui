from typing import cast

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import Reactive, reactive
from textual.widgets import DataTable, Input

from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.utils.styling import get_style_for_work_item_status, get_style_for_work_item_type
from jiratui.utils.urls import build_external_url_for_issue


class DataTableSearchInput(Input):
    """An input field that allows users to perform searches in the currently active search results page.

    The feature to search within search results pages is controlled by these settings:

    - `search_results_page_filtering_enabled`
    - `search_results_page_filtering_minimum_term_length`
    """

    BINDINGS = [Binding('escape', 'hide', 'Hide search input', show=False)]

    total: Reactive[int | None] = reactive(None)
    """Keeps track of the total number of records after filtering them based on the input value."""

    def __init__(
        self,
        placeholder: str | None = None,
        border_title: str | None = None,
        hide: bool | None = True,
    ):
        super().__init__(id='searchable-datatable-input-field')
        self.placeholder = placeholder or 'Type to filter items in the current page...'
        self.border_title = border_title or 'Filter'
        self.styles.display = 'none' if hide else 'block'

    def action_hide(self) -> None:
        # hide the input widget
        self.styles.display = 'none'
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        # reset the results to the initial result set
        screen.search_results_table.search_results = (
            screen.search_results_table.get_initial_results_set()
        )
        # give focus back to the data table
        screen.search_results_table.focus()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if action == 'hide' and not CONFIGURATION.get().search_results_page_filtering_enabled:
            return False
        return True

    def watch_total(self, value: int | None = None) -> None:
        if value is not None:
            self.border_subtitle = f'Found: {value}'
        else:
            self.border_subtitle = None

    @on(Input.Changed)
    async def on_input_changed(self, event: Input.Changed) -> None:
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        cleaned = event.value.strip() if event.value else None
        if not cleaned or (
            len(cleaned) < CONFIGURATION.get().search_results_page_filtering_minimum_term_length
        ):
            screen.search_results_table.search_results = (
                screen.search_results_table.get_initial_results_set()
            )
            self.total = 0
        else:
            cleaned = cleaned.lower()
            if (initial_results_set := screen.search_results_table.get_initial_results_set()) and (
                issues := initial_results_set.issues
            ):
                filtered: list[JiraIssue] = [
                    record for record in issues if cleaned in record.summary.lower()
                ]
                screen.search_results_table.search_results = JiraIssueSearchResponse(
                    issues=filtered
                )
                self.total = len(filtered)


class IssuesSearchResultsTable(DataTable):
    """The widgets that displays the results of a search."""

    search_results: Reactive[JiraIssueSearchResponse | None] = reactive(None, always_update=True)

    BINDINGS = [
        Binding(
            key='/',
            action='filter',
            description='Filter in Page',
            tooltip='Filter the results of the current page',
        ),
        Binding('escape', 'hide', 'Hide search input', show=False),
        Binding(
            key='alt+left',
            action='previous_issues_page',
            description='Previous Page',
            show=True,
            key_display='alt+left',
        ),
        Binding(
            key='alt+right',
            action='next_issues_page',
            description='Next Page',
            show=True,
            key_display='alt+right',
        ),
        Binding(
            key='ctrl+o',
            action='open_issue_in_browser',
            description='Open in Browser',
            show=True,
            key_display='^o',
        ),
    ]

    def __init__(self):
        super().__init__(id='search_results', cursor_type='row')
        # stores the Jira's next page's token by page number
        # e.g.: {1: 'token-a', 2: 'token-b'}
        # to fetch the results page
        #   1: we need to use the token 'token-a'
        #   2: we need to use the token 'token-b'
        self.token_by_page: dict[int, str] = {}
        self.page: int = 0
        self.current_work_item_key: str | None = None
        self._initial_results_set: JiraIssueSearchResponse | None = None

    def set_initial_results_set(self, data: JiraIssueSearchResponse | None = None):
        self._initial_results_set = data

    def get_initial_results_set(self) -> JiraIssueSearchResponse | None:
        return self._initial_results_set

    def watch_search_results(self, response: JiraIssueSearchResponse | None = None) -> None:
        if response is None:
            return

        # clear the existing data
        self.clear(columns=True)

        # update next search tokens
        if response.next_page_token:
            # there is a token to fetch the next page
            self.token_by_page[self.page + 1] = response.next_page_token

        # set the columns
        self.add_columns(*['#', 'Key', 'Status', 'Type', 'Summary'])
        # build the rows
        for index, issue in enumerate(response.issues):
            issue_summary = issue.cleaned_summary(
                CONFIGURATION.get().search_results_truncate_work_item_summary
            )

            style_status = ''
            if CONFIGURATION.get().search_results_style_work_item_status:
                style_status = get_style_for_work_item_status(issue.status.name.lower())

            style_work_type = ''
            if CONFIGURATION.get().search_results_style_work_item_type:
                style_work_type = get_style_for_work_item_type(issue.issue_type.name.lower())

            self.add_row(
                *[
                    index + 1,
                    issue.key,
                    Text(issue.status.name, style=style_status),
                    Text(issue.work_item_type_name, style=style_work_type),
                    Text(issue_summary),
                ],
                key=f'{issue.id}#{issue.key}',
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Fetches the details of the currently-selected item."""
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        _, work_item_key = event.row_key.value.split('#')
        self.current_work_item_key = work_item_key
        # use exclusive=True to make sure that if the user selects another work item before the worker finishes
        # retrieving the data of the previously selected the correct data is fetched
        # the exclusive flag tells Textual to cancel all previous workers before starting the new one.
        self.run_worker(screen.fetch_issue(work_item_key), exclusive=True)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Stores the key of the currently-selected item."""
        _, self.current_work_item_key = event.row_key.value.split('#')

    def action_open_issue_in_browser(self) -> None:
        """Opens the currently-selected item in the default browser."""
        if self.current_work_item_key:
            self.notify('Opening Work Item in the browser...')
            self.app.open_url(build_external_url_for_issue(self.current_work_item_key))

    def action_filter(self) -> None:
        if not CONFIGURATION.get().search_results_page_filtering_enabled:
            return
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        widget = screen.search_results_filter_input
        widget.styles.display = 'block'
        widget.focus(True)
        widget.total = 0
        widget.value = ''

    def action_hide(self) -> None:
        if not CONFIGURATION.get().search_results_page_filtering_enabled:
            return
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        widget = screen.search_results_filter_input
        # hide the input widget
        widget.styles.display = 'none'
        # reset the results to the initial result set
        self.search_results = self.get_initial_results_set()
        # give focus back to the data table
        self.focus()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if action == 'filter' and not CONFIGURATION.get().search_results_page_filtering_enabled:
            return False
        if action == 'hide' and not CONFIGURATION.get().search_results_page_filtering_enabled:
            return False
        return True


class SearchResultsContainer(Container):
    pagination: Reactive[dict | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = 'Work Items'
        self.config = CONFIGURATION.get()

    def watch_pagination(self, response: dict) -> None:
        if response:
            total_results = response.get('total', 0)
            total_pages = total_results // self.config.search_results_per_page
            if (total_results % self.config.search_results_per_page) > 0:
                total_pages += 1
            current_page_number = max(1, response.get('current_page_number'))
            self.border_subtitle = (
                f'Page {current_page_number} of {total_pages} (total: {total_results})'
            )
