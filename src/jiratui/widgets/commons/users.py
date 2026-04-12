import logging
from typing import Callable

from textual.reactive import Reactive, reactive
from textual.widgets import Input
from textual_autocomplete import AutoComplete, DropdownItem, TargetState

from jiratui.api_controller.controller import APIController, APIControllerResponse

logger = logging.getLogger(__name__)


# TODO consider moving this to src/jiratui/widgets/commons/widgets.py
class JiraUserInput(Input):
    """An input field for selecting a single Jira user.

    This widget holds the Jira user's account id that is used to identify the user. This is useful for operations
    that create/update work items' user fields, such as assignee, reporter, etc.
    """

    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self, *args, **kwargs):
        border_subtitle: str | None = kwargs.pop('border_subtitle', None)
        jira_field_key: str | None = kwargs.pop('jira_field_key', None)
        border_title: str | None = kwargs.pop('border_title', None)
        required: bool | None = kwargs.pop('required', False)
        super().__init__(*args, **kwargs)
        self.border_title = border_title or 'Jira User'
        if required:
            self.border_subtitle = '(*)'
            self.add_class(*['required'])
        if border_subtitle:
            self.border_subtitle = border_subtitle
        self.jira_field_key = jira_field_key
        """The id used by Jira to identify this field in the edit-metadata or to update its value in a work item."""
        self._account_id: str | None = None
        """The account id of the currently selected Jira user."""
        self._update_is_enabled: bool = False
        """Indicates whether the work item allows editing/updating this field."""

    @property
    def account_id(self) -> str | None:
        return self._account_id if self.value and self.value.strip() else None

    @account_id.setter
    def account_id(self, account_id: str | None):
        self._account_id = account_id

    @property
    def update_is_enabled(self) -> bool:
        return self._update_is_enabled

    @update_is_enabled.setter
    def update_is_enabled(self, value: bool):
        self._update_is_enabled = value

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled

    def clear(self):
        super().clear()
        self.account_id = None

    def set_value(self, account_id: str | None, value: str | None) -> None:
        self.value = value if value else ''
        self.account_id = account_id


# TODO consider moving this to src/jiratui/widgets/commons/base.py
class UsersAutoComplete(AutoComplete):
    """AutoComplete for Jira users that searches users using the Jira API.

    This widget fetches users dynamically as the user types. It requires an `Input` widget as the target;
    the target widget MUST provide a property to set the user's account id, `account_id`.

    This is useful for filtering users by name or email addresses, e.g. when searching for possible reporters.
    """

    MIN_QUERY_TERM_LENGTH = 3
    """The minimum length of the query used for searching users by email/display name."""

    def __init__(
        self,
        target: Input,
        api_controller: APIController,
        user_search_function: Callable | None = None,
        id: str | None = None,  # noqa:A002
    ):
        """Initializes a UsersAutoComplete widget.

        Args:
            target: the Input widget to attach autocomplete to
            api_controller: APIController instance for fetching suggestions.
            user_search_function: an async callable that searches and filters users based on a query term.
            id: the id for this widget.
        """

        self._api_controller: APIController = api_controller
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''
        self._user_search_function = user_search_function or self._search

        # initialize with empty candidates - will be populated dynamically
        super().__init__(
            id=id,
            target=target,
            candidates=self._get_users,  # type:ignore
        )

    def _get_users(self, target_state: TargetState) -> list[DropdownItem]:
        """Synchronous wrapper that returns cached suggestions."""

        # get the search string
        search_string = self.get_search_string(target_state)

        # if query changed, trigger async fetch
        if search_string and search_string != self._last_query:
            self._last_query = search_string
            # schedule async fetch - don't await here since this must be sync
            self.call_later(self._search_users, search_string)
        return self._cached_suggestions

    async def _search(self, query: str) -> APIControllerResponse:
        # the default function to search and filter users based on a query term
        return await self._api_controller.search_users(email_or_name=query)

    async def _search_users(self, query: str) -> None:
        """Search Jira users asynchronously.

        If the auto complete field is initialized with a project id then this method searches for Jira users using a
        combination of the project id and the search query. This allows to search for users assignable to issues in a
        given project.

        Args:
            query: the query term to use. This will be used for finding users by display name and/or email.

        Returns:
            None
        """

        if not query or len(query) < self.MIN_QUERY_TERM_LENGTH:
            self._cached_suggestions = []
            return

        try:
            self._cached_suggestions = []
            response: APIControllerResponse = await self._user_search_function(query)
            if response and response.success and response.result:
                # update cached suggestions
                self._cached_suggestions = []
                for user in response.result:
                    main = user.display_name
                    if user.email:
                        main = f'{main}|{user.email}'
                    self._cached_suggestions.append(DropdownItem(main=main, id=user.account_id))

                # trigger dropdown re-evaluation to show the suggestions
                self._handle_target_update()
        except Exception as e:
            logger.error(
                f'Error fetching Jira users with the given query: {query} - {e}', exc_info=True
            )
            self._cached_suggestions = []

    def should_show_dropdown(self, search_string: str) -> bool:
        if self.option_list.option_count == 1:
            first_option = self.option_list.get_option_at_index(0).prompt
            from rich.text import Text

            text_from_option = (
                first_option.plain if isinstance(first_option, Text) else first_option
            )
            return text_from_option != search_string
        return True

    def apply_completion(self, value: str, state: TargetState) -> None:
        # split name from email
        value = value.split('|', 1)[0]
        super().apply_completion(value, state)
        self.target.account_id = self.option_list.highlighted_option.id  # type:ignore[attr-defined]
