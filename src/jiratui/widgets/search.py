from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import Reactive, reactive
from textual.widgets import DataTable

from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssueSearchResponse
from jiratui.utils.styling import get_style_for_work_item_status, get_style_for_work_item_type


class IssuesSearchResultsTable(DataTable):
    search_results: Reactive[JiraIssueSearchResponse | None] = reactive(None, always_update=True)

    BINDINGS = [
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

    def watch_search_results(self, response: JiraIssueSearchResponse | None = None) -> None:
        if response is None:
            return

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
                key=str(issue.id),
            )

        # focus the table with the current results page
        self.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        # use exclusive=True to make sure that if the user selects another work item before the worker finishes
        # retrieving the data of the previously selected the correct data is fetched
        # the exclusive flag tells Textual to cancel all previous workers before starting the new one.
        self.run_worker(screen.fetch_issue(event.row_key.value), exclusive=True)


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
