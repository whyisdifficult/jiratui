from textual.reactive import Reactive, reactive
from textual.widgets import Input
from textual_autocomplete import AutoComplete, DropdownItem, TargetState
import logging

from jiratui.api_controller.controller import APIController

logger = logging.getLogger(__name__)

class JiraUserInput(Input):
    """An input field for selecting a Jira user.

    This widget holds the Jira user's account id that is used to identify the user. This is useful for operations
    that create/update work items' user fields, such as assignee, reporter, etc.
    """

    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self, *args, **kwargs):
        border_subtitle: str | None = kwargs.pop('border_subtitle', None)
        jira_field_key: str | None = kwargs.pop('jira_field_key', None)
        border_title: str | None = kwargs.pop('border_title', None)
        super().__init__(*args, **kwargs)
        self.border_title = border_title or 'Jira User'
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

class UsersAutoComplete(AutoComplete):
    """AutoComplete for Jira users that fetches suggestions from Jira API.

    This widget fetches users suggestions dynamically as the user types. It requires an Input widget as the target;
    the target widget MUST provide a property to set the user's account id.
    """

    def __init__(self, target: Input, api_controller: APIController):
        """Initializes a UsersAutoComplete widget.

        Args:
            target: the Input widget to attach autocomplete to
            api_controller: APIController instance for fetching suggestions.
        """

        self._api_controller = api_controller
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''

        # initialize with empty candidates - will be populated dynamically
        super().__init__(
            target=target,
            candidates=self._get_candidates_sync,   # type:ignore
        )

    def _get_candidates_sync(self, target_state: TargetState) -> list[DropdownItem]:
        """Synchronous wrapper that returns cached suggestions."""

        # get the search string
        search_string = self.get_search_string(target_state)

        # if query changed, trigger async fetch
        if search_string and search_string != self._last_query:
            self._last_query = search_string
            # schedule async fetch - don't await here since this must be sync
            self.call_later(self._fetch_suggestions, search_string)
        return self._cached_suggestions

    async def _fetch_suggestions(self, query: str) -> None:
        """Fetch users suggestions from Jira API asynchronously."""

        if not query:
            self._cached_suggestions = []
            return

        try:
            self._cached_suggestions = []
            response = await self._api_controller.search_users(email_or_name=query)
            # API controller returns APIControllerResponse with result containing suggestions list
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
            logger.error(f'Error fetching Jira users with the given query: {query} - {e}', exc_info=True)
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
        if '|' in value:
            value = value.split('|', 1)[0]
        super().apply_completion(value, state)
        self.target.account_id = self.option_list.highlighted_option.id
