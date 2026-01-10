from enum import Enum
import logging
from typing import Any

from textual.reactive import Reactive, reactive
from textual.widgets import Input, Select
from textual_autocomplete import AutoComplete, DropdownItem, TargetState

logger = logging.getLogger(__name__)


class FieldMode(Enum):
    """Enum to distinguish between field creation and update contexts."""

    CREATE = 'create'
    UPDATE = 'update'


class BaseFieldWidget:
    """
    Base mixin for common field widget patterns.

    Provides:
    - Required field indication via border_subtitle
    - Standard CSS class management
    - Mode-aware behavior

    Note: This is a mixin, not a standalone widget. It should be combined with
    Textual widget classes via multiple inheritance.
    """

    def setup_base_field(
        self,
        mode: FieldMode,
        field_id: str,
        title: str | None = None,
        required: bool = False,
        compact: bool = True,
    ) -> None:
        """
        Initialize common field properties.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: The field identifier (Jira field key)
            title: Display title for the field (defaults to field_id)
            required: Whether the field is required
            compact: Whether to use compact mode
        """
        self.mode = mode  # type: ignore[attr-defined]
        self.field_id = field_id  # type: ignore[attr-defined]
        self.border_title = title or field_id  # type: ignore[attr-defined]
        self._required = required  # type: ignore[attr-defined]

        if required:
            self.border_subtitle = '(*)'  # type: ignore[attr-defined]
            if hasattr(self, 'add_class'):
                self.add_class('required')  # type: ignore[attr-defined]

    @property
    def required(self) -> bool:
        """Check if this field is required."""
        return getattr(self, '_required', False)  # type: ignore[attr-defined]

    def mark_required(self) -> None:
        """Mark this field as required by adding subtitle and CSS class."""
        self._required = True  # type: ignore[attr-defined]
        self.border_subtitle = '(*)'  # type: ignore[attr-defined]
        if hasattr(self, 'add_class'):
            self.add_class('required')  # type: ignore[attr-defined]


class BaseUpdateFieldWidget:
    """
    Base mixin for UPDATE mode widgets with change tracking.

    Provides:
    - Original value storage
    - Change detection via value_has_changed property
    - Update capability management

    This is used for widgets in the work_item_details context where
    we need to track changes from the original Jira value.
    """

    def setup_update_field(
        self,
        jira_field_key: str,
        original_value: Any = None,
        field_supports_update: bool = True,
    ) -> None:
        """
        Initialize UPDATE mode specific properties.

        Args:
            jira_field_key: The Jira API field key
            original_value: The original value from Jira
            field_supports_update: Whether Jira allows updating this field
        """
        self.jira_field_key = jira_field_key  # type: ignore[attr-defined]
        self._original_value = original_value  # type: ignore[attr-defined]
        self._field_supports_update = field_supports_update  # type: ignore[attr-defined]

        if hasattr(self, 'disabled'):
            self.disabled = not field_supports_update  # type: ignore[attr-defined]

    @property
    def original_value(self) -> Any:
        """Retrieves the original value of the work item's field as retrieved from the API."""
        return self._original_value

    @property
    def value_has_changed(self) -> bool:
        """
        Determines if the current value differs from the original value.

        Must be implemented by subclasses based on their specific value types.
        """
        raise NotImplementedError('Subclasses must implement value_has_changed')


class ValidationUtils:
    """Shared validation utilities for field widgets."""

    @staticmethod
    def is_empty_or_whitespace(value: str | None) -> bool:
        """Check if a string value is None, empty, or only whitespace."""
        if value is None:
            return True
        if value == '':
            return True
        if value.strip() == '':
            return True
        return False

    @staticmethod
    def values_differ(original: Any, current: Any, ignore_whitespace: bool = True) -> bool:
        """
        Compare two values for difference.

        Args:
            original: The original value
            current: The current value
            ignore_whitespace: Whether to strip whitespace before comparison
        """
        if ignore_whitespace and isinstance(original, str) and isinstance(current, str):
            return original.strip() != current.strip()
        return original != current


class UserPickerWidget(Select, BaseFieldWidget, BaseUpdateFieldWidget):
    """
    Unified user picker widget that works in both CREATE and UPDATE modes.
    """

    # Reactive property for CREATE mode user population
    users: Reactive[dict | None] = reactive(None, always_update=True)
    """A dictionary with 2 keys: users: list and selection: str | None"""

    # Reactive property for UPDATE mode to track whether field can be updated
    update_enabled: Reactive[bool] = reactive(True)

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        title: str | None = None,
        required: bool = False,
        # CREATE mode parameters
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """
        Initialize a UserPickerWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            original_value: Original value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """
        # Initialize Select with common parameters
        # Note: Always allow_blank=True initially because options are populated later
        # via the reactive 'users' property (CREATE mode) or set_options (UPDATE mode)
        super().__init__(
            options=[],
            prompt='Select a user',
            id=field_id,
            type_to_search=True,
            compact=True,
            allow_blank=True,  # Always allow blank since options populated later
        )

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            title=title,
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=field_id,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
            # Store pending value for UPDATE mode (set after options loaded)
            self.pending_value = original_value
            # Set initial update_enabled state
            self.update_enabled = field_supports_update
        else:
            # CREATE mode specific setup
            self.add_class('create-work-item-user-picker')

    def watch_update_enabled(self, enabled: bool) -> None:
        """Watch for changes to update_enabled reactive property."""
        self.disabled = not enabled

    def watch_users(self, users: dict | None = None) -> None:
        """
        Watch for changes to the users reactive property (CREATE mode).

        This is the pattern used by CREATE mode widgets to populate options.
        Expects a dict with 'users' (list of user objects) and optional 'selection'.
        """
        if self.mode != FieldMode.CREATE:
            return

        self.clear()
        if users and (items := users.get('users', []) or []):
            options = [(item.display_name, item.account_id) for item in items]
            self.set_options(options)
            if selection := users.get('selection'):
                for option in options:
                    if option[1] == selection:
                        self.value = option[1]
                        break

    def get_value_for_update(self) -> dict | None:
        """
        Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            A dictionary with the accountId, or None if no value selected
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if self.value and str(self.value).strip():
            return {'accountId': str(self.value).strip()}
        return None

    @property
    def value_has_changed(self) -> bool:
        """
        Determines if the current value differs from the original value (UPDATE mode).

        Returns:
            True if value has changed, False otherwise
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        current_value = str(self.value).strip() if self.value else None
        original_value = self.original_value

        # No original value - changed if we now have a value
        if not original_value:
            return bool(current_value)

        # Had original value, now cleared
        if not current_value:
            return True

        # Both exist - compare them
        return original_value != current_value


class ProjectSelectionWidget(Select, BaseFieldWidget, BaseUpdateFieldWidget):
    """
    Unified project selection widget that works in both CREATE and UPDATE modes.
    """

    projects: Reactive[dict | None] = reactive(None, init=False, always_update=True)

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        title: str | None = None,
        required: bool = False,
        prompt: str | None = None,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """
        Initialize a ProjectSelectionWidget.

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
            title=title or 'Project',
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=field_id,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
        else:
            # CREATE mode specific setup
            self.add_class('create-work-item-project-selector')

    def watch_projects(self, projects: dict | None = None) -> None:
        """
        Watch for changes to the projects reactive property (CREATE mode).

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
        """Get the current selection value."""
        if self.value == Select.BLANK or self.value is None:
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
    """
    Unified issue type selection widget that works in both CREATE and UPDATE modes.
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        options: list[tuple[str, str]],
        title: str | None = None,
        required: bool = False,
        prompt: str | None = None,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """
        Initialize an IssueTypeSelectionWidget.

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
            title=title or 'Issue Type',
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=field_id,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
            if original_value:
                self.value = original_value
        else:
            # CREATE mode specific setup
            self.add_class('create-work-item-issuetype-selector')

    @property
    def selection(self) -> str | None:
        """Get the current selection value."""
        if self.value == Select.BLANK or self.value is None:
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

    This widget works in both CREATE and UPDATE modes, fetching label suggestions
    dynamically as the user types.
    """

    def __init__(
        self,
        target: Input,
        api_controller,
        required: bool = False,
        title: str | None = None,
    ):
        """
        Initialize a LabelsAutoComplete widget.

        Args:
            target: The Input widget to attach autocomplete to
            api_controller: APIController instance for fetching suggestions
            required: Whether the field is required
            title: Display title for the field (defaults to 'labels')
        """
        self.api_controller = api_controller
        self._stored_title = title or 'labels'
        self._required = required
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''

        # Initialize with empty candidates - will be populated dynamically
        super().__init__(
            target=target,
            candidates=self._get_candidates_sync,
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
            response = await self.api_controller.get_label_suggestions(query=query)

            # API controller returns APIControllerResponse with result containing suggestions list
            if response and response.success and response.result:
                suggestions = response.result

                # Update cached suggestions
                self._cached_suggestions = [
                    DropdownItem(main=suggestion) for suggestion in suggestions
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
