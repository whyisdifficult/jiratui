from typing import cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, ItemGrid
from textual.reactive import Reactive, reactive
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Static, Button, Rule

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.utils.styling import get_style_for_work_item_status, get_style_for_work_item_type
from jiratui.utils.urls import build_external_url_for_issue

class ConfirmDeleteItemScreen(ModalScreen[bool]):
    """A modal screen that allows the user to confirm deleting an item."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Screen')]

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = f'Delete Work Item {self._work_item_key}'
        with vertical:
            yield Static(
                Text(
                    f'Warning: deleting the work item with key {self._work_item_key} will also delete all its subtasks!',
                     style='italic orange'
                )
            )
            yield Rule()
            with ItemGrid(classes='delete-work-item-grid-buttons'):
                yield Button('Delete', variant='success', id='delete-work-item-button')
                yield Button('Cancel', variant='error', id='delete-work-item-button-cancel')

    @on(Button.Pressed, '#delete-work-item-button')
    def delete_item(self) -> None:
        if self._work_item_key:
            self.dismiss(True)

    @on(Button.Pressed, '#delete-work-item-button-cancel')
    def cancel_deleting_item(self) -> None:
        self.dismiss(False)

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
                    record
                    for record in issues
                    if (
                        cleaned in record.summary.lower()
                        or cleaned in record.key.lower()
                        or cleaned in record.parent_key
                    )
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
            key='.',
            action='filter',
            description='Filter',
            tooltip='Filter the results of the current page',
        ),
        Binding('escape', 'hide', 'Hide search input', show=False),
        Binding(
            key='alt+left',
            action='previous_issues_page',
            description='Previous',
            show=True,
            key_display='alt+left',
            tooltip='Previous page',
        ),
        Binding(
            key='alt+right',
            action='next_issues_page',
            description='Next',
            show=True,
            key_display='alt+right',
            tooltip='Next page',
        ),
        Binding(
            key='ctrl+o',
            action='open_issue_in_browser',
            description='Browse',
            show=True,
            key_display='^o',
            tooltip='Open item in the browser',
        ),
        Binding(
            key='d',
            action='delete_work_item',
            description='Delete Issue',
            show=True,
            key_display='d',
            tooltip='Delete the work item currently highlighted.',
        ),
    ]

    SMALLEST_MAXIMUM_WIDTH_FOR_SUMMARY_COLUMN = 30

    def __init__(self):
        super().__init__(id='search_results', cursor_type='row')
        # stores the next page's token by page number
        # e.g.: {2: 'token-a', 3: 'token-b'}
        # to fetch the results page
        #   2: we need to use the token 'token-a'
        #   3: we need to use the token 'token-b'
        self.token_by_page: dict[int, str] = {}
        self.page = 1
        self.current_work_item_key: str | None = None
        self._initial_results_set: JiraIssueSearchResponse | None = None

    def set_initial_results_set(self, data: JiraIssueSearchResponse | None = None):
        self._initial_results_set = data

    def get_initial_results_set(self) -> JiraIssueSearchResponse | None:
        return self._initial_results_set

    def watch_search_results(self, response: JiraIssueSearchResponse | None = None) -> None:
        """Watches the content of a reactive attribute that contains the details of the work item selected by the user.

        Args:
            response: an instance of `JiraIssueSearchResponse` with the work item selected by the user.

        Returns:
            None
        """
        if response is None:
            return

        # clear the existing data
        self.clear(columns=True)

        maximum_summary_column_width = max(
            self.SMALLEST_MAXIMUM_WIDTH_FOR_SUMMARY_COLUMN,
            self.parent.container_size.width - 42,  # type:ignore[attr-defined]
        )

        # update next search tokens
        if response.next_page_token:
            # there is a token to fetch the next page
            self.token_by_page[self.page + 1] = response.next_page_token

        # set the columns
        self.add_columns(*['#', 'Key', 'Parent', 'Status', 'Type', 'Summary'])
        # build the rows
        for index, issue in enumerate(response.issues):
            issue_summary = issue.cleaned_summary(
                CONFIGURATION.get().search_results_truncate_work_item_summary
                or maximum_summary_column_width
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
                    issue.parent_key,
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

    def action_delete_work_item(self) -> None:
        """Deletes the currently-selected item."""

        if self.current_work_item_key:
            self.run_worker(self._open_work_item_deletion_screen(self.current_work_item_key), exclusive=True)

    async def _open_work_item_deletion_screen(self, work_item_key: str) -> None:
        """Opens a modal screen to let the user decided whether to delete the work item or not.

        Args:
            work_item_key: key of the work item to delete.

        Returns:
            None
        """

        await self.app.push_screen(ConfirmDeleteItemScreen(work_item_key), callback=self._delete_work_item)

    async def _delete_work_item(self, delete_item: bool = False) -> None:
        """Deletes the currently-selected item.

        Args:
            delete_item: if `True` the user confirmed deleting the item in the modal screen; otherwise the user
            canceled the operation.

        Returns:
            None.
        """

        if delete_item and self.current_work_item_key:
            response: APIControllerResponse = await self.app.api.delete_work_item(self.current_work_item_key)
            if response.success:
                self.notify(f'{self.current_work_item_key} deleted successfully', title='Delete Work Item')
            else:
                self.notify(
                    f'Failed to delete the item {self.current_work_item_key}.',
                    title='Delete Work Item',
                    severity='error',
                )
                if response.error:
                    self.notify(
                        response.error,
                        title='Delete Work Item',
                        severity='error',
                    )

    def action_filter(self) -> None:
        if not CONFIGURATION.get().search_results_page_filtering_enabled:
            return
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        widget = screen.search_results_filter_input
        widget.styles.display = 'block'
        widget.focus(True)
        widget.total = 0
        widget.value = ''
        self.refresh_bindings()

    def action_hide(self) -> None:
        if not CONFIGURATION.get().search_results_page_filtering_enabled:
            return
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        # hide the input widget
        screen.search_results_filter_input.styles.display = 'none'
        # reset the results to the initial result set
        self.search_results = self.get_initial_results_set()
        # give focus back to the data table
        self.focus()
        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if action == 'filter' and not CONFIGURATION.get().search_results_page_filtering_enabled:
            return False
        if action == 'hide' and not CONFIGURATION.get().search_results_page_filtering_enabled:
            return False
        if action == 'previous_issues_page':
            if self.page > 1:
                return True
            return False
        if action == 'next_issues_page':
            if self.token_by_page.get(self.page + 1):
                return True
            if self.page > 0:
                return True
            return False
        return True

    async def action_previous_issues_page(self):
        if self.page > 1:
            next_page_token = self.token_by_page.get(self.page - 1)
            self.page -= 1
            screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
            await screen.search_issues(next_page_token, page=self.page)
            self.refresh_bindings()

    async def action_next_issues_page(self):
        next_page_token = self.token_by_page.get(self.page + 1)
        self.page += 1
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        await screen.search_issues(next_page_token, page=self.page)
        self.refresh_bindings()

class SearchResultsContainer(Container):
    pagination: Reactive[dict | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = 'Work Items'
        self.config = CONFIGURATION.get()

    def watch_pagination(self, response: dict) -> None:
        if response:
            current_page_number = max(1, response.get('current_page_number'))
            if (total_results := response.get('total', 0)) is not None:
                total_pages = total_results // self.config.search_results_per_page
                if (total_results % self.config.search_results_per_page) > 0:
                    total_pages += 1
                self.border_subtitle = (
                    f'Page {current_page_number} of {total_pages} (total: {total_results})'
                )
            else:
                self.border_subtitle = f'Page {current_page_number}'
