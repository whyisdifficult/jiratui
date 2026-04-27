from enum import Enum
import logging
from typing import Any, Callable

from textual.reactive import Reactive, reactive
from textual.widgets import Input, Select
from textual_autocomplete import AutoComplete, DropdownItem, TargetState

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraUser, JQLAutocompleteSuggestion

logger = logging.getLogger(__name__)


class FieldMode(Enum):
    """Enum to distinguish between field creation and update contexts."""

    CREATE = 'create'
    UPDATE = 'update'


class BaseFieldWidget:
    """Base mixin for common field widget patterns.

    Provides:
    - Required field indication via border_subtitle
    - Standard CSS class management
    - Mode-aware behavior

    ```{Note}
    This is a mixin, not a standalone widget. It should be combined with Textual widget classes via multiple
    inheritance.
    ```
    """

    def setup_base_field(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str | None = None,
        title: str | None = None,
        required: bool = False,
        compact: bool = True,
    ) -> None:
        """Initializes common field properties.

        Args:
            mode: the field mode (CREATE or UPDATE)
            field_id: the field identifier (Jira field key).
            jira_field_key: the Jira API field key. This is the id that it is used for setting the value of the field
            in work items.
            the field when requesting updates (creation/update) via the API.
            title: display title for the field (defaults to field_id).
            required: whether the field is required.
            compact: whether to use Textual's compact mode.
        """

        self.mode = mode  # type:ignore[attr-defined]
        self.field_id = field_id  # type:ignore[attr-defined]
        self.border_title = title or field_id  # type:ignore[attr-defined]
        self._required = required  # type:ignore[attr-defined]
        self._jira_field_key = (
            jira_field_key  # the field's key used for creating/updating values via the API
        )

        if required:
            self.border_subtitle = '(*)'  # type: ignore[attr-defined]
            if hasattr(self, 'add_class'):
                self.add_class('required')  # type: ignore[attr-defined]

    @property
    def required(self) -> bool:
        """Checks if this field is required."""

        return getattr(self, '_required', False)  # type: ignore[attr-defined]

    def mark_required(self) -> None:
        """Marks this field as required by adding subtitle and CSS class."""

        self._required = True  # type:ignore[attr-defined]
        self.border_subtitle = '(*)'  # type:ignore[attr-defined]
        if hasattr(self, 'add_class'):
            self.add_class('required')  # type:ignore[attr-defined]

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key


class BaseUpdateFieldWidget:
    """Base mixin for UPDATE mode widgets with change tracking.

    Provides:
    - Original value storage
    - Change detection via value_has_changed property
    - Update capability management

    This is used for widgets in the `work_item_details` context where we need to track changes from the original Jira
    value.
    """

    def setup_update_field(
        self,
        jira_field_key: str,
        original_value: Any = None,
        field_supports_update: bool = True,
    ) -> None:
        """Initializes UPDATE mode specific properties.

        Args:
            jira_field_key: the Jira API field key. This is the id that it is used for setting the value of the field
            in work items.
            original_value: the original value from Jira.
            field_supports_update: whether Jira allows updating this field.
        """

        self._jira_field_key = jira_field_key  # type:ignore[attr-defined]
        self._original_value = original_value  # type:ignore[attr-defined]
        self._field_supports_update = field_supports_update  # type:ignore[attr-defined]

        if hasattr(self, 'disabled'):
            self.disabled = not field_supports_update  # type:ignore[attr-defined]

    @property
    def original_value(self) -> Any:
        """Retrieves the original value of the work item's field as retrieved from the API."""

        return self._original_value

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original value.

        Must be implemented by subclasses based on their specific value types.
        """

        raise NotImplementedError('Subclasses must implement value_has_changed')


class ValidationUtils:
    """Shared validation utilities for field widgets."""

    @staticmethod
    def is_empty_or_whitespace(value: str | None) -> bool:
        """Checks if a string value is None, empty, or only whitespace."""

        if value is None:
            return True
        if value == '':
            return True
        if value.strip() == '':
            return True
        return False

    @staticmethod
    def values_differ(original: Any, current: Any, ignore_whitespace: bool = True) -> bool:
        """Compares two values for difference.

        Args:
            original: the original value.
            current: the current value.
            ignore_whitespace: whether to strip whitespace before comparison.
        """

        if ignore_whitespace and isinstance(original, str) and isinstance(current, str):
            return original.strip() != current.strip()
        return original != current


class ProjectSelectionWidget(Select, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified project selection widget that works in both CREATE and UPDATE modes."""

    projects: Reactive[dict | None] = reactive(None, init=False, always_update=True)
    """A dictionary with 2 keys:

    projects: list
    selection: str | None
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        prompt: str | None = None,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a ProjectSelectionWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier
            title: Display title (defaults to field_id)
            required: Whether the field is required
            prompt: Custom prompt text (defaults based on required status)
            original_value: Original value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """
        # Determine prompt based on mode and required status
        if prompt is None:
            prompt = 'Select a project (*)' if required else 'Select a project'

        # Initialize Select
        # Note: allow_blank=True even for required fields during initialization
        # because options are populated asynchronously. Required validation
        # happens at save time, not during widget initialization.
        super().__init__(
            options=[],
            prompt=prompt,
            id=field_id,
            type_to_search=True,
            compact=True,
            allow_blank=True,
        )

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title or 'Project',
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.add_class('create-update-field-widget')
        else:
            # CREATE mode specific setup
            self.add_class('create-work-item-project-selector')

    def watch_projects(self, projects: dict | None = None) -> None:
        """Watches for changes to the projects reactive property (CREATE mode).

        Expects a dict with 'projects' (list of Project objects) and optional 'selection'.
        """

        if self.mode != FieldMode.CREATE:
            return

        self.clear()
        if projects and (items := projects.get('projects', []) or []):
            options = [(f'{item.name} ({item.key})', item.key) for item in items]
            self.set_options(options)
            if selection := projects.get('selection'):
                for option in options:
                    if option[1] == selection:
                        self.value = option[1]
                        break

    @property
    def selection(self) -> str | None:
        """Gets the current selection value."""
        if self.value == Select.NULL or self.value is None:
            return None
        return str(self.value)

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original (UPDATE mode only)."""
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        current_value = self.selection
        original_value = self.original_value

        if not original_value:
            return bool(current_value)

        if not current_value:
            return True

        return original_value != current_value

    def get_value_for_update(self) -> str | None:
        """Returns the value formatted for Jira API updates (UPDATE mode)."""
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        return self.selection


class IssueTypeSelectionWidget(Select, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified issue type selection widget that works in both CREATE and UPDATE modes."""

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        options: list[tuple[str, str]],
        title: str | None = None,
        required: bool = False,
        prompt: str | None = None,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes an IssueTypeSelectionWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier
            options: List of (display_name, value) tuples
            title: Display title (defaults to field_id)
            required: Whether the field is required
            prompt: Custom prompt text
            original_value: Original value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """

        # Determine prompt
        if prompt is None:
            prompt = 'Select an issue type (*)' if required else 'Select an issue type'

        # Initialize Select
        # Note: allow_blank=True even for required fields during initialization
        # because options may be populated asynchronously. Required validation
        # happens at save time, not during widget initialization.
        super().__init__(
            options=options,
            prompt=prompt,
            id=field_id,
            type_to_search=True,
            compact=True,
            allow_blank=True,
        )

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title or 'Issue Type',
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.add_class('create-update-field-widget')
            if original_value:
                self.value = original_value

    @property
    def selection(self) -> str | None:
        """Get the current selection value."""
        if self.value == Select.NULL or self.value is None:
            return None
        return str(self.value)

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original (UPDATE mode only)."""
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        current_value = self.selection
        original_value = self.original_value

        if not original_value:
            return bool(current_value)

        if not current_value:
            return True

        return original_value != current_value

    def get_value_for_update(self) -> str | None:
        """Returns the value formatted for Jira API updates (UPDATE mode)."""
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        return self.selection


class LabelsAutoComplete(AutoComplete):
    """AutoComplete for labels that fetches suggestions from Jira API.

    This widget works in both CREATE and UPDATE modes, fetching label suggestions dynamically as the user types.
    """

    def __init__(
        self,
        target: Input,
        api_controller,
        required: bool = False,
        title: str | None = None,
    ):
        """Initializes a `LabelsAutoComplete` widget.

        Args:
            target: the Input widget to attach autocomplete to
            api_controller: APIController instance for fetching suggestions
            required: whether the field is required
            title: display title for the field (defaults to 'labels')
        """

        self.api_controller = api_controller
        self._stored_title = title or 'labels'
        self._required = required
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''

        # Initialize with empty candidates - will be populated dynamically
        super().__init__(
            target=target,
            candidates=self._get_candidates_sync,  # type:ignore
        )

    def _get_candidates_sync(self, target_state: TargetState) -> list[DropdownItem]:
        """Synchronous wrapper that returns cached suggestions."""
        # Get the search string
        search_string = self.get_search_string(target_state)

        # If query changed, trigger async fetch
        if search_string and search_string != self._last_query:
            self._last_query = search_string
            # Schedule async fetch - don't await here since this must be sync
            self.call_later(self._fetch_suggestions, search_string)

        return self._cached_suggestions

    async def _fetch_suggestions(self, query: str) -> None:
        """Fetch label suggestions from Jira API asynchronously."""
        if not query:
            self._cached_suggestions = []
            return

        try:
            response = await self.api_controller.get_jql_autocomplete_suggestions(
                field_name='labels',
                field_value=query,
            )
            # API controller returns APIControllerResponse with result containing suggestions list
            if response and response.success and response.result:
                suggestions: list[JQLAutocompleteSuggestion] = response.result
                # Update cached suggestions
                self._cached_suggestions = [
                    DropdownItem(main=suggestion.value) for suggestion in suggestions
                ]
                # Trigger dropdown re-evaluation to show the suggestions
                self._handle_target_update()
            else:
                self._cached_suggestions = []
        except Exception as e:
            logger.error(f'Error fetching label suggestions: {e}', exc_info=True)
            self._cached_suggestions = []

    def get_search_string(self, target_state: TargetState) -> str:
        """Get the string to search within - just the last word for comma-separated labels."""
        # target_state is a TargetState object with .text attribute
        value = target_state.text if hasattr(target_state, 'text') else str(target_state)
        words = value.split(',')
        return words[-1].strip()

    def should_show_dropdown(self, search_string: str) -> bool:
        if self.option_list.option_count == 1:
            first_option = self.option_list.get_option_at_index(0).prompt
            from rich.text import Text

            text_from_option = (
                first_option.plain if isinstance(first_option, Text) else first_option
            )
            should_show = text_from_option != search_string
            return should_show
        else:
            return True

    def apply_completion(self, value: str, state: TargetState) -> None:
        """Apply the selected completion to the input."""
        current_value = state.text
        # Split by comma and strip whitespace from each part
        words = [word.strip() for word in current_value.split(',')]

        # Replace the last word with the selected value
        words[-1] = value

        # Rejoin with commas and add trailing space for next entry
        new_value = ', '.join(words) + ', '
        self.target.value = new_value
        self.target.cursor_position = len(new_value)


class MultiUserPickerAutoComplete(AutoComplete):
    """AutoComplete for selecting multiple users.

    This widget works in both CREATE and UPDATE modes, fetching users suggestions dynamically as the user types.

    ````{important}
    The target Input widget will display a comma-separated list of names. However, the widget needs to keep track of
    the account ids of every user. To do that the target Input widget MUST implement a method called

    ```python
    add_user(account_id='', name='')
    ```

    This will be used for storing the users selected in the target Input widget.
    ````
    """

    MIN_QUERY_TERM_LENGTH = 2
    """The minimum length of the query used for searching users by email/display name."""

    def __init__(
        self,
        target: Input,
        api_controller: APIController,
        required: bool = False,
        title: str | None = None,
        user_search_function: Callable | None = None,
    ):
        """Initializes a `MultiUserPickerAutoComplete` widget.

        Args:
            target: the Input widget to attach autocomplete to
            api_controller: APIController instance for fetching suggestions
            required: whether the field is required
            title: display title for the field (defaults to 'Users')

        Raises:
            NotImplemented: if the target Input widget does not implement the required `add_user` method.
        """

        self._api_controller = api_controller
        self._stored_title = title or 'Users'
        self._required = required
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''
        # the function used for fetching suggestions (Jira users) based on the input query provided by the user
        self._user_search_function = user_search_function or self._search

        # initialize with empty candidates - will be populated dynamically
        super().__init__(
            target=target,
            candidates=self._get_users,  # type:ignore
        )

        if not (add_user_callable := getattr(self.target, 'add_user', None)) or not callable(
            add_user_callable
        ):
            raise NotImplementedError(
                f'Class {self.target.__class__.__name__} MUST implement add_user(account_id, name)'
            )

    async def _search(self, query: str) -> APIControllerResponse:
        # the default function to search and filter users based on a query term
        return await self._api_controller.find_users_for_picker(query)

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

    async def _search_users(self, query: str) -> None:
        """Searches Jira users asynchronously.

        Args:
            query: the query term to use. This will be used for finding users by display name and/or email. The query
            term MUST be at least `MIN_QUERY_TERM_LENGTH` characters long to trigger the search.

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
                user: JiraUser
                for user in response.result:
                    self._cached_suggestions.append(
                        DropdownItem(main=user.display_name, id=user.account_id)
                    )
                # trigger dropdown re-evaluation to show the suggestions
                self._handle_target_update()
        except Exception as e:
            logger.error(f'Error fetching users suggestions: {e}', exc_info=True)
            self._cached_suggestions = []

    def get_search_string(self, target_state: TargetState) -> str:
        """Gets the string to search within - just the last user's name for comma-separated users names."""

        # target_state is a TargetState object with .text attribute
        value = target_state.text if hasattr(target_state, 'text') else str(target_state)
        words = value.split(',')
        return words[-1].strip()

    def should_show_dropdown(self, search_string: str) -> bool:
        if self.option_list.option_count == 1:
            first_option = self.option_list.get_option_at_index(0).prompt
            from rich.text import Text

            text_from_option = (
                first_option.plain if isinstance(first_option, Text) else first_option
            )
            return text_from_option != search_string
        else:
            return True

    def apply_completion(self, value: str, state: TargetState) -> None:
        """Applies the selected completion to the input."""

        # get the id of the selected option; this is the user's account id
        highlighted_option_id = self.option_list.highlighted_option.id
        # remove possible email address in the value
        value = value.split('|', 1)[0]
        # current_value = state.text
        # split by comma and strip whitespace from each part
        # words = [word.strip() for word in current_value.split(',')]
        # replace the last word with the selected value
        # words[-1] = value
        # rejoin with commas and add trailing space for next entry
        # new_value = ', '.join(words) + ', '
        # self.target.value = new_value
        # self.target.cursor_position = len(new_value)
        self.target.add_user(account_id=highlighted_option_id, name=value)  # type:ignore[attr-defined]


class MultiIssuePickerAutoComplete(AutoComplete):
    """AutoComplete for selecting multiple work items by key.

    This widget works in both CREATE and UPDATE modes, fetching issues suggestions dynamically as the user types.

    ````{important}
    The target Input widget will display a comma-separated list of issues keys. However, the widget needs to keep
    track of the keys of every selected issue. To do that the target Input widget MUST implement a method called

    ```python
    update_issues_data(issue_key='')
    ```

    This will be used for storing the keys selected in the target Input widget.
    ````
    """

    MIN_QUERY_TERM_LENGTH = 3
    """The minimum length of the query used for searching issues by query term."""

    def __init__(
        self,
        target: Input,
        api_controller: APIController,
        required: bool = False,
        title: str | None = None,
        issue_search_function: Callable | None = None,
    ):
        """Initializes a `MultiIssuePickerAutoComplete` widget.

        Args:
            target: the Input widget to which the autocomplete will be applied.
            api_controller: APIController instance for fetching suggestions
            required: whether the field is required
            title: display title for the field (defaults to 'Issues')

        Raises:
            NotImplemented: if the target Input widget does not implement the required `update_issues_data` method.
        """

        self._api_controller = api_controller
        self._stored_title = title or 'Issues'
        self._required = required
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''
        # the function used for fetching suggestions (Jira issues) based on the input query provided by the user
        self._issue_search_function = issue_search_function or self._search

        # Initialize with empty candidates - will be populated dynamically
        super().__init__(
            target=target,
            candidates=self._get_issues,  # type:ignore
        )

        if not (
            update_issues_data_callable := getattr(self.target, 'update_issues_data', None)
        ) or not callable(update_issues_data_callable):
            raise NotImplementedError(
                f'Class {self.target.__class__.__name__} MUST implement update_issues_data(issue_key)'
            )

    async def _search(self, query: str) -> APIControllerResponse:
        # the default function to search and filter issues based on a query term
        return await self._api_controller.issue_picker(query)

    def _get_issues(self, target_state: TargetState) -> list[DropdownItem]:
        """Synchronous wrapper that returns cached suggestions."""

        # get the search string
        search_string = self.get_search_string(target_state)
        # if query changed, trigger async fetch
        if search_string and search_string != self._last_query:
            self._last_query = search_string
            # Schedule async fetch - don't await here since this must be sync
            self.call_later(self._search_issues, search_string)
        return self._cached_suggestions

    async def _search_issues(self, query: str) -> None:
        """Searches Jira issues asynchronously.

        Args:
            query: the query term to use. This will be used for finding issues by key or summary. The query
            term MUST be at least `MIN_QUERY_TERM_LENGTH` characters long to trigger the search.

        Returns:
            None
        """

        if not query or len(query) < self.MIN_QUERY_TERM_LENGTH:
            self._cached_suggestions = []
            return

        try:
            self._cached_suggestions = []
            response: APIControllerResponse = await self._issue_search_function(query)
            if response and response.success and response.result:
                # update cached suggestions
                self._cached_suggestions = []
                for issue in response.result:
                    self._cached_suggestions.append(
                        DropdownItem(main=f'{issue.key}|{issue.summary[:30]}...', id=issue.key)
                    )
                # trigger dropdown re-evaluation to show the suggestions
                self._handle_target_update()
        except Exception as e:
            logger.error(f'Error fetching issues suggestions: {e}', exc_info=True)
            self._cached_suggestions = []

    def get_search_string(self, target_state: TargetState) -> str:
        """Gets the string to search within - just the last key for comma-separated keys."""
        # target_state is a TargetState object with .text attribute
        value = target_state.text if hasattr(target_state, 'text') else str(target_state)
        words = value.split(',')
        return words[-1].strip()

    def should_show_dropdown(self, search_string: str) -> bool:
        if self.option_list.option_count == 1:
            first_option = self.option_list.get_option_at_index(0).prompt
            from rich.text import Text

            text_from_option = (
                first_option.plain if isinstance(first_option, Text) else first_option
            )
            return text_from_option != search_string
        else:
            return True

    def apply_completion(self, value: str, state: TargetState) -> None:
        """Applies the selected completion to the input."""

        # get the id of the selected option; this is an issue's key
        highlighted_option_id = self.option_list.highlighted_option.id
        # remove the summary of the issue and keep the key only to make the input values shorter
        value = value.split('|', 1)[0]
        current_value = state.text
        # split by comma and strip whitespace from each part
        words = [word.strip() for word in current_value.split(',')]
        # replace the last word with the selected value
        words[-1] = value
        # rejoin with commas and add trailing space for next entry
        new_value = ', '.join(words) + ', '
        self.target.value = new_value
        self.target.cursor_position = len(new_value)
        self.target.update_issues_data(issue_key=highlighted_option_id)  # type:ignore[attr-defined]
