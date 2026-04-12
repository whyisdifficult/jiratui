"""Unified widgets for work item field handling.

Widgets included:
- DateInputWidget: Date input with validation
- DateTimeInputWidget: DateTime input with validation
- TextInputWidget: Text input with change tracking
- LabelsWidget: Comma-separated labels input
- URLWidget: URL input with auto-prefix
- NumericInputWidget: Numeric/float input with validation
- SelectionWidget: Single selection dropdown
- DescriptionWidget: TextArea input field for managing the description of work items during creation and update
operations.
- MultiSelectWidget: Multi-select with checkboxes
- SprintWidget: Text input field for providing the ID of a sprint using a shorter layout.
- EpicLinkWidget: Text input field for providing the key of an Epic issue using a shorter layout.
- MultiUserPickerWidget: Comma-separated list of users' display names.
- MultiIssuePickerWidget Comma-separated list of issues' keys.

All widgets work in both CREATE and UPDATE modes by extending base classes from base.py.
"""

from typing import Any

from dateutil.parser import isoparse  # type:ignore[import-untyped]
from textual.events import Key
from textual.validation import Number, ValidationResult
from textual.widgets import Input, MaskedInput, Select, SelectionList, TextArea
from textual.widgets.selection_list import Selection

from jiratui.widgets.base import DateInput
from jiratui.widgets.commons.base import (
    BaseFieldWidget,
    BaseUpdateFieldWidget,
    FieldMode,
    ValidationUtils,
)

# ============================================================================
# Date and DateTime Widgets
# ============================================================================


class DateInputWidget(DateInput, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified date input widget that works in both CREATE and UPDATE modes.

    This widget extends `DateInput` (`MaskedInput` with template '9999-99-99') and adds mode-aware behavior for create
    vs. update contexts.

    Usage in CREATE mode:
    ```python
    widget = DateInputWidget(
        mode=FieldMode.CREATE,
        field_id='duedate',
        jira_field_key='duedate',
        title='Due Date',
        required=False,
    )
    # Widget is ready to use, collects ISO date string from
    widget.value
    ```

    Usage in UPDATE mode:
    ```python
    widget = DateInputWidget(
        mode=FieldMode.UPDATE,
        field_id='duedate',
        jira_field_key='duedate',
        title='Due Date',
        original_value='2025-12-23',
        field_supports_update=True,
    )
    # Check changes with widget.value_has_changed
    # Get value for API with
    widget.get_value_for_update()
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a `DateInputWidget`.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            original_value: Original date value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """

        # Initialize DateInput (which is a MaskedInput)
        # valid_empty depends on mode and required flag
        # In CREATE mode: True if field is optional (not required)
        # In UPDATE mode: Always True (fields can be cleared)
        valid_empty = not required if mode == FieldMode.CREATE else True
        super().__init__(widget_id=field_id, valid_empty=valid_empty)

        # Setup base field properties
        # Pass required flag to setup_base_field for border_subtitle and CSS class
        # The validate() override prevents background highlighting for optional empty fields
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required if mode == FieldMode.CREATE else False,
            compact=True,
        )
        # self.add_class('input-date')

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            # Set initial value if provided
            if original_value:
                self.value = original_value

    def validate(self, value: str) -> ValidationResult | None:
        """Override validation to allow empty values when valid_empty is True.

        MaskedInput validates against the template even when valid_empty=True,
        which causes empty fields with placeholder characters to be marked as invalid.
        This override allows empty values to pass validation without triggering the
        template validation.

        Args:
            value: The value to validate

        Returns:
            ValidationResult indicating whether validation succeeded
        """

        def set_classes() -> None:
            """Set classes for valid flag."""
            valid = self._valid
            self.set_class(not valid, '-invalid')
            self.set_class(valid, '-valid')

        # If this field allows empty values and the value is effectively empty
        # (only contains placeholders like _ and -), mark as valid
        if self.valid_empty:
            stripped = value.replace('_', '').replace('-', '').strip()
            if not stripped:
                self._valid = True
                set_classes()
                return None

        # Otherwise, use parent's validation (which includes template validation)
        return super().validate(value)

    def get_value_for_update(self) -> str | None:
        """
        Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            A date value in ISO format (YYYY-MM-DD), or None if empty or invalid
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if self.value and self.value.strip():
            try:
                # Parse and return as ISO date string
                return str(isoparse(self.value).date())
            except ValueError:
                return None
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

        original = self.original_value if self.original_value else ''
        current = self.value.strip() if self.value else ''

        # Empty to empty - no change
        if not original and not current:
            return False

        # Empty to value or value to empty - changed
        if not original or not current:
            return True

        # Both exist - compare them
        return original != current


class DateTimeInputWidget(MaskedInput, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified datetime input widget that works in both CREATE and UPDATE modes.

    Uses `MaskedInput` with template '9999-99-99 99:99:99' for datetime entry.

    Usage in CREATE mode:
    ```python
    widget = DateTimeInputWidget(
        mode=FieldMode.CREATE,
        field_id='customfield_10001',
        jira_field_key='customfield_10001',
        title='Event Time',
        required=False,
    )
    ```

    Usage in UPDATE mode:
    ```python
    widget = DateTimeInputWidget(
        mode=FieldMode.UPDATE,
        field_id='customfield_10001',
        jira_field_key='customfield_10001',
        title='Event Time',
        original_value='2025-12-23 13:45:10',
        field_supports_update=True,
    )
    # Check changes with
    widget.value_has_changed
    # Get value for API with
    widget.get_value_for_update()
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a DateTimeInputWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            original_value: Original datetime value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """
        # Initialize MaskedInput with datetime template
        super().__init__(
            id=field_id,
            template='9999-99-99 99:99:99',
            placeholder='2025-12-23 13:45:10',
        )

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required,
            compact=False,  # DateTime typically not compact
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
            # Set initial value if provided
            if original_value:
                self.value = original_value
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-datetime-input')

    def get_value_for_update(self) -> str | None:
        """Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            A datetime value in ISO format, or None if empty or invalid
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if self.value and self.value.strip():
            try:
                # Parse and return as ISO format datetime string
                return isoparse(self.value).isoformat()
            except ValueError:
                return None
        return None

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original value (UPDATE mode).

        Returns:
            True if value has changed, False otherwise
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        original = self.original_value if self.original_value else ''
        current = self.value.strip() if self.value else ''

        # Empty to empty - no change
        if not original and not current:
            return False

        # Empty to value or value to empty - changed
        if not original or not current:
            return True

        # Both exist - compare them
        return original != current


# ============================================================================
# Text and String Widgets
# ============================================================================


class TextInputWidget(Input, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified text input widget that works in both CREATE and UPDATE modes.

    Extends Textual's Input widget with mode-aware behavior and change tracking.

    Usage in CREATE mode:
    ```python
    widget = TextInputWidget(
        mode=FieldMode.CREATE,
        field_id='customfield_10002',
        jira_field_key='customfield_10002',
        title='Custom Text Field',
        required=True,
    )
    ```

    Usage in UPDATE mode:
    ```python
    widget = TextInputWidget(
        mode=FieldMode.UPDATE,
        field_id='customfield_10002',
        jira_field_key='customfield_10002',
        title='Custom Text Field',
        original_value='original text',
        field_supports_update=True,
    )
    # Check changes
    widget.value_has_changed
    # Get value for API
    widget.get_value_for_update()
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        placeholder: str = 'some string...',
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a TextInputWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            placeholder: Placeholder text for the input
            original_value: Original text value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """

        # initialize Input
        super().__init__(id=field_id, placeholder=placeholder)

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value or '',
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
            # set initial value if provided
            if original_value:
                self.value = original_value
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-generic-input-field')

    def get_value_for_update(self) -> str:
        """Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            The string value
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        return self.value

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original value (UPDATE mode).

        Returns:
            True if value has changed, False otherwise
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        # Use ValidationUtils for consistent comparison
        original = self.original_value if self.original_value else ''
        current = self.value if self.value else ''

        # Handle empty values consistently
        if ValidationUtils.is_empty_or_whitespace(
            original
        ) and ValidationUtils.is_empty_or_whitespace(current):
            return False

        # If one is empty and the other isn't, it changed
        if ValidationUtils.is_empty_or_whitespace(
            original
        ) or ValidationUtils.is_empty_or_whitespace(current):
            return True

        # Both have values - compare with whitespace stripping
        return ValidationUtils.values_differ(original, current, ignore_whitespace=True)


class LabelsWidget(Input):
    """Unified labels input widget that works in both CREATE and UPDATE modes.

    This widget handles comma-separated label input and provides proper formatting
    for Jira API (list of strings).

    Schema detection:
        custom_type == CustomFieldType.LABELS.value
        OR
        schema.type == "array" AND schema.items == "string" AND field_id == "labels"

    Usage in CREATE mode:
    ```python
    widget = LabelsWidget(
        mode=FieldMode.CREATE,
        field_id='labels',
        jira_field_key='labels',
        title='Labels',
        required=False,
    )
    # User enters: "bug, frontend, urgent"
    get_value_for_create() == ['bug', 'frontend', 'urgent']
    ```

    Usage in UPDATE mode:
    ```python
    widget = LabelsWidget(
        mode=FieldMode.UPDATE,
        field_id="customfield_10001",
        jira_field_key="customfield_10001",
        title="Tags",
        original_value=["backend", "api"],
        supports_update=True
    )
    # Displays: "backend, api"
    # User changes to: "backend, database"
    get_value_for_update() returns: ["backend", "database"]
    value_has_changed == True
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        original_value: list[str] | None = None,
        supports_update: bool = True,
        **kwargs,
    ):
        """Initializes the labels widget.

        Args:
            mode: CREATE or UPDATE mode
            field_id: Jira field ID (e.g., "labels" or "customfield_10001")
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            title: Display title for the field
            required: Whether the field is required
            original_value: Original labels for UPDATE mode (list of strings)
            supports_update: Whether field can be updated (UPDATE mode only)
            **kwargs: Additional arguments passed to Input
        """

        # store mode and original value
        self.mode = mode
        self._original_value = original_value if mode == FieldMode.UPDATE else None
        self._supports_update = supports_update if mode == FieldMode.UPDATE else True
        self.field_id = field_id

        # initialize Input widget
        Input.__init__(
            self,
            placeholder='Enter labels (comma-separated)',
            id=field_id,
            **kwargs,
        )

        # set border title
        self.border_title = title or 'Labels'

        # mode-specific setup
        self._jira_field_key = jira_field_key
        if self.mode == FieldMode.UPDATE:
            self.add_class('issue_details_input_field')
            # Disable if field doesn't support updates
            self.disabled = not supports_update
            # Set initial value from original_value (list -> comma-separated string)
            if original_value:
                self.value = ','.join(original_value)
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-generic-input-field')

        # Add required indicator
        if required:
            self.border_subtitle = '(*)'
            self.add_class('required')

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @property
    def original_value(self) -> list[str]:
        """Get the original labels from Jira."""
        return self._original_value or []

    def get_value_for_create(self) -> list[str]:
        """Returns labels formatted for Jira API create requests (CREATE mode).

        Returns:
            List of label strings (leading/trailing whitespace stripped,
            internal spaces removed, empty labels filtered out)
        """

        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        if not self.value or not self.value.strip():
            return []

        # split by comma, strip whitespace, remove internal spaces, filter empty strings
        return [label.strip().replace(' ', '') for label in self.value.split(',') if label.strip()]

    def get_value_for_update(self) -> list[str]:
        """Returns labels formatted for Jira API update requests (UPDATE mode).

        Returns:
            List of label strings (leading/trailing whitespace stripped,
            internal spaces removed, empty labels filtered out)
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if not self.value or not self.value.strip():
            return []

        # Split by comma, strip whitespace, remove internal spaces, filter empty strings
        return [label.strip().replace(' ', '') for label in self.value.split(',') if label.strip()]

    @property
    def value_has_changed(self) -> bool:
        """Determines if labels have changed from original value (UPDATE mode).

        Uses set comparison to ignore order and whitespace differences.
        Comparison is case-insensitive (treats "Backend" and "backend" as same),
        but original casing is preserved when sending to Jira API.

        Returns:
            True if labels have changed, False otherwise
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        original_labels = self.original_value if self.original_value else []
        current_labels = self.get_value_for_update()

        # Both empty - no change
        if not original_labels and not current_labels:
            return False

        # One empty, one not - changed
        if bool(original_labels) != bool(current_labels):
            return True

        # Compare as sets (case-insensitive, order-independent)
        # Use lowercase for comparison to treat "Backend" and "backend" as same
        original_set = {label.lower() for label in original_labels}
        current_set = {label.lower() for label in current_labels}

        return original_set != current_set


class URLWidget(Input, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified URL input widget supporting both CREATE and UPDATE modes.

    Auto-adds 'https://' prefix on blur if not present.
    Handles URL field creation and updates via Jira API.
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        placeholder: str = 'https://example.com',
        original_value: str | None = None,
        field_supports_update: bool = True,
        **kwargs: Any,
    ) -> None:
        self.mode = mode
        self._original_value = original_value or ''
        self._supports_update = field_supports_update
        self.field_id = field_id

        # initialize Input widget
        super().__init__(
            placeholder=placeholder,
            id=field_id,
            **kwargs,
        )

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required,
            compact=True,
        )

        # mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value or '',
                field_supports_update=field_supports_update,
            )
            self.add_class('update-field')
            # set initial value if provided
            if original_value:
                self.value = original_value
            if not field_supports_update:
                self.disabled = True
        else:
            # CREATE mode specific CSS
            self.add_class('create-field')

    @property
    def original_value(self) -> str:
        """Get the original value from Jira."""
        return self._original_value

    def on_input_blurred(self, event: Input.Changed) -> None:
        """Auto-add https:// prefix if not present."""
        if self.mode == FieldMode.UPDATE and not self._supports_update:
            return

        value = self.value.strip()
        if value and 'http' not in value:
            self.value = f'https://{value}'

    def get_value_for_create(self) -> str:
        """Get value for create work item request."""
        if self.mode != FieldMode.CREATE:
            msg = 'get_value_for_create() can only be called in CREATE mode'
            raise ValueError(msg)
        return self.value.strip()

    def get_value_for_update(self) -> str:
        """Get value for update work item request."""
        if self.mode != FieldMode.UPDATE:
            msg = 'get_value_for_update() can only be called in UPDATE mode'
            raise ValueError(msg)
        return self.value.strip()

    @property
    def value_has_changed(self) -> bool:
        """Check if the value has changed from original."""
        if self.mode != FieldMode.UPDATE:
            msg = 'value_has_changed can only be checked in UPDATE mode'
            raise ValueError(msg)

        original = self.original_value.strip()
        current = self.value.strip()

        # Both empty - no change
        if not original and not current:
            return False

        # Compare stripped values
        return original != current


class EpicLinkWidget(Input, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified Input widget for specifying the key of an (Epic) issue supporting both CREATE and UPDATE modes."""

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        original_value: str | None = None,
        field_supports_update: bool = True,
        **kwargs: Any,
    ) -> None:
        self.mode = mode
        self._original_value = original_value or ''
        self._supports_update = field_supports_update
        self.field_id = field_id

        # initialize Input widget
        super().__init__(placeholder='E.g. ABC-123', id=field_id, **kwargs)

        # set border title with required indicator
        self.border_title = f'{title} [red]*[/red]' if required else title

        # mode-specific setup
        self._jira_field_key = jira_field_key
        if mode == FieldMode.CREATE:
            self.add_class('create-work-item-generic-input-field', 'issue_key')
        elif mode == FieldMode.UPDATE:
            self.add_class('issue_details_input_field', ' issue_key')
            if original_value:
                self.value = original_value
            if not field_supports_update:
                self.disabled = True

    @property
    def original_value(self) -> str:
        """Get the original value from Jira."""
        return self._original_value

    def get_value_for_create(self) -> str:
        """Get value for create work item request."""
        if self.mode != FieldMode.CREATE:
            msg = 'get_value_for_create() can only be called in CREATE mode'
            raise ValueError(msg)
        return self.value.strip()

    def get_value_for_update(self) -> str:
        """Get value for update work item request."""
        if self.mode != FieldMode.UPDATE:
            msg = 'get_value_for_update() can only be called in UPDATE mode'
            raise ValueError(msg)
        return self.value.strip()

    @property
    def value_has_changed(self) -> bool:
        """Check if the value has changed from original."""
        if self.mode != FieldMode.UPDATE:
            msg = 'value_has_changed can only be checked in UPDATE mode'
            raise ValueError(msg)

        original = self.original_value.strip()
        current = self.value.strip()

        # Both empty - no change
        if not original and not current:
            return False

        # Compare stripped values
        return original != current


class SprintWidget(Input, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified Input widget for specifying the ID of a Sprint supporting both CREATE and UPDATE modes."""

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        placeholder='Sprint ID, e.g. 123',
        original_value: str | None = None,
        field_supports_update: bool = True,
        **kwargs: Any,
    ) -> None:
        self.mode = mode
        self._original_value = original_value or ''
        self._supports_update = field_supports_update
        self.field_id = field_id

        # initialize Input widget
        super().__init__(id=field_id, placeholder=placeholder, **kwargs)

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required,
            compact=True,
        )

        # Mode-specific setup
        self.styles.width = 20
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value or '',
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
            # set initial value if provided
            if original_value:
                self.value = original_value
            if not field_supports_update:
                self.disabled = True
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-generic-input-field')

    @property
    def original_value(self) -> str:
        """Get the original value from Jira."""
        return self._original_value

    def get_value_for_create(self) -> str:
        """Get value for create work item request."""
        if self.mode != FieldMode.CREATE:
            msg = 'get_value_for_create() can only be called in CREATE mode'
            raise ValueError(msg)
        return self.value.strip()

    def get_value_for_update(self) -> str:
        """Get value for update work item request."""
        if self.mode != FieldMode.UPDATE:
            msg = 'get_value_for_update() can only be called in UPDATE mode'
            raise ValueError(msg)
        return self.value.strip()

    @property
    def value_has_changed(self) -> bool:
        """Check if the value has changed from original."""
        if self.mode != FieldMode.UPDATE:
            msg = 'value_has_changed can only be checked in UPDATE mode'
            raise ValueError(msg)

        original = self.original_value.strip()
        current = self.value.strip()

        # Both empty - no change
        if not original and not current:
            return False

        # Compare stripped values
        return original != current


class MultiUserPickerWidget(Input):
    """Unified users' display names input widget that works in both CREATE and UPDATE modes.

    This widget handles comma-separated users' names input and provides proper formatting for Jira API (list of strings).

    Schema detection:
        custom_type == CustomFieldType.MULTI_USER_PICKER.value

    Usage in CREATE mode:
    ```python
    widget = MultiUserPickerWidget(
        mode=FieldMode.CREATE,
        field_id='approvers',
        jira_field_key='approvers',
        title='Approvers',
        required=False,
    )
    # User enters: "bart, homer, lisa"
    get_value_for_create() == ['123', '456', '789']
    ```

    Usage in UPDATE mode:
    ```python
    widget = MultiUserPickerWidget(
        mode=FieldMode.UPDATE,
        field_id="approvers",
        jira_field_key="approvers",
        title="Approvers",
        original_value=[{"name": "bart", "id": "123"}, {"name": "homer", "id": "456"}],
        supports_update=True
    )
    widget.update_users_data("123", "bart")
    widget.update_users_data("456", "homer")
    # Displays: "bart, homer"
    # User changes to: "bart, lisa"
    get_value_for_update() returns: ["123", "789"]
    value_has_changed == True
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        original_value: list[dict] | None = None,
        supports_update: bool = True,
        **kwargs,
    ):
        """Initializes the widget.

        Args:
            mode: CREATE or UPDATE mode
            field_id: Jira field ID (e.g., "labels" or "customfield_10001")
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            title: Display title for the field
            required: Whether the field is required
            original_value: Original users for UPDATE mode (list of dictionaries with the id and name of a user)
            supports_update: Whether field can be updated (UPDATE mode only)
            **kwargs: Additional arguments passed to Input
        """

        # store mode and original value
        self.mode = mode
        self._original_value: list[dict] | None = (
            original_value if mode == FieldMode.UPDATE else None
        )
        self._supports_update = supports_update if mode == FieldMode.UPDATE else True
        self.field_id = field_id
        # keeps track of the users' account ids and their names
        # example: {'123': 'Bart'}
        self._users: dict[str, str] = {}

        # initialize Input widget
        Input.__init__(
            self,
            placeholder='Type in user name or email...',
            id=field_id,
            **kwargs,
        )

        # set border title
        self.border_title = title or 'Users'

        # mode-specific setup
        self._jira_field_key = jira_field_key
        if self.mode == FieldMode.UPDATE:
            self.add_class('issue_details_input_field')
            # disable if field doesn't support updates
            self.disabled = not supports_update
            # set initial value from original_value (list -> comma-separated string)
            if self._original_value:
                self.value = ','.join([user.get('name') for user in self._original_value])
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-generic-input-field')

        # Add required indicator
        if required:
            self.border_subtitle = '(*)'
            self.add_class('required')

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @property
    def original_value(self) -> list[dict]:
        """Gets the original labels from Jira."""
        return self._original_value or []

    def get_value_for_create(self) -> list[dict]:
        """Returns users account ids formatted for Jira API create requests (CREATE mode).

        The attribute `self._users` may contain account ids of users that are not among the ones displayed by the
        Input widget. This can happen when the user deletes a user's name form the input. To make sure this widget
        always return the account ids of the final list of users we need to process the ids in `self._users` based on
        their names.

        Example:
        ```python
        self._users = {'123': 'Bart', '456': 'Homer'}
        self.value = 'Bart'
        result = get_value_for_create()
        [{'id': '123'}]
        ```

        Returns:
            A list of dictionaries with the id of a user's account.
        """

        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        if not self.value or not self.value.strip():
            return []

        # split by comma, remove internal spaces, filter empty strings
        values = {name.strip() for name in self.value.split(',') if name.strip()}
        return [
            {'id': user_account_id}
            for user_account_id, user_display_name in self._users.items()
            if user_display_name in values
        ]

    def get_value_for_update(self) -> list[dict]:
        """Returns users account ids formatted for Jira API update requests (UPDATE mode).

        The attribute `self._users` may contain account ids of users that are not among the ones displayed by the
        Input widget. This can happen when the user deletes a user's name form the input. To make sure this widget
        always return the account ids of the final list of users we need to process the ids in `self._users` based on
        their names.

        Example:
        ```python
        self._users = {'123': 'Bart', '456': 'Homer'}
        self.value = 'Bart'
        result = get_value_for_update()
        [{'id': '123'}]
        ```

        Returns:
            A list of dictionaries with the id of a user's account.
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if not self.value or not self.value.strip():
            return []

        # split by comma, remove internal spaces, filter empty strings
        values = {name.strip() for name in self.value.split(',') if name.strip()}
        return [
            {'id': user_account_id}
            for user_account_id, user_display_name in self._users.items()
            if user_display_name in values
        ]

    @property
    def value_has_changed(self) -> bool:
        """Determines if names have changed from original value (UPDATE mode).

        Uses set comparison to ignore order and whitespace differences.
        Comparison is case-insensitive (treats "Backend" and "backend" as same), but original casing is preserved when
        sending to Jira API.

        Returns:
            True if names have changed, False otherwise.
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        original_users: list[dict] = self.original_value if self.original_value else []
        current_users: list[dict] = self.get_value_for_update()

        # Both empty - no change
        if not original_users and not current_users:
            return False

        # One empty, one not - changed
        if bool(original_users) != bool(current_users):
            return True

        # Compare as sets (case-insensitive, order-independent)
        original_set = {user.get('id') for user in original_users}
        current_set = {user.get('id') for user in current_users}
        return original_set != current_set

    def update_users_data(self, account_id: str, name: str) -> None:
        if account_id and name:
            self._users[account_id] = name


class MultiIssuePickerWidget(Input):
    """Unified issues' keys input widget that works in both CREATE and UPDATE modes.

    This widget handles comma-separated issue key input and provides proper formatting
    for Jira API (list of strings).

    Schema detection:
        schema.type == "array" AND schema.items == "issuelinks" AND field_id == "issuelinks"

    Usage in CREATE mode:
    ```python
    widget = MultiIssuePickerWidget(
        mode=FieldMode.CREATE,
        field_id='issuelinks',
        jira_field_key='issuelinks',
        title='Issues Links',
        required=False,
    )
    # User enters: "issue-1, issue-2, issue-2"
    get_value_for_create() == ['issue-1', 'issue-2', 'issue-3']
    ```

    Usage in UPDATE mode:
    ```python
    widget = MultiIssuePickerWidget(
        mode=FieldMode.UPDATE,
        field_id="issuelinks",
        jira_field_key="issuelinks",
        title="Issues Links",
        original_value=["issue-1", "issue-2"],
        supports_update=True
    )
    # Displays: "issue-1, issue-2"
    # User changes to: "issue-1, issue-3"
    get_value_for_update() returns: ["issue-1", "issue-3"]
    value_has_changed == True
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        original_value: list[str] | None = None,
        supports_update: bool = True,
        **kwargs,
    ):
        """Initializes the widget.

        Args:
            mode: CREATE or UPDATE mode
            field_id: Jira field ID (e.g., "labels" or "customfield_10001")
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            title: Display title for the field
            required: Whether the field is required
            original_value: Original labels for UPDATE mode (list of strings)
            supports_update: Whether field can be updated (UPDATE mode only)
            **kwargs: Additional arguments passed to Input
        """

        # store mode and original value
        self.mode = mode
        self._original_value = original_value if mode == FieldMode.UPDATE else None
        self._supports_update = supports_update if mode == FieldMode.UPDATE else True
        self.field_id = field_id
        # keeps track of the keys selected by the user
        self._issues_keys: set[str] = set()

        # initialize Input widget
        Input.__init__(
            self,
            placeholder='Type in issue key/title...',
            id=field_id,
            **kwargs,
        )

        # set border title
        self.border_title = title or 'Linked Issues'

        # mode-specific setup
        self._jira_field_key = jira_field_key
        if self.mode == FieldMode.UPDATE:
            self.add_class('issue_details_input_field')
            # Disable if field doesn't support updates
            self.disabled = not supports_update
            # Set initial value from original_value (list -> comma-separated string)
            if original_value:
                self.value = ','.join(original_value)
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-generic-input-field')

        # Add required indicator
        if required:
            self.border_subtitle = '(*)'
            self.add_class('required')

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @property
    def original_value(self) -> list[str]:
        """Gets the original labels from Jira."""
        return self._original_value or []

    def get_value_for_create(self) -> list[str]:
        """Returns issue keys formatted for Jira API create requests (CREATE mode).

        Returns:
            A list of issue keys strings (leading/trailing whitespace stripped, empty keys filtered out)
        """

        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        if not self.value or not self.value.strip():
            return []

        # split by comma, remove internal spaces, filter empty strings
        values = {label.strip() for label in self.value.split(',') if label.strip()}
        return [issue_key for issue_key in self._issues_keys if issue_key in values]

    def get_value_for_update(self) -> list[str]:
        """Returns issue keys formatted for Jira API update requests (UPDATE mode).

        Returns:
            A list of issue keys strings (leading/trailing whitespace stripped, empty labels filtered out)
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if not self.value or not self.value.strip():
            return []

        # split by comma and filter empty strings
        values = {label.strip() for label in self.value.split(',') if label.strip()}
        return [issue_key for issue_key in self._issues_keys if issue_key in values]

    @property
    def value_has_changed(self) -> bool:
        """Determines if issues keys have changed from original value (UPDATE mode).

        Uses set comparison to ignore order and whitespace differences.
        Comparison is case-insensitive (treats "Backend" and "backend" as same), but original casing is preserved when
        sending to Jira API.

        Returns:
            True if the issues keys have changed, False otherwise.
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        original_issues_keys = self.original_value if self.original_value else []
        current_issues_keys = self.get_value_for_update()

        # both empty - no change
        if not original_issues_keys and not current_issues_keys:
            return False

        # one empty, one not - changed
        if bool(original_issues_keys) != bool(current_issues_keys):
            return True

        # compare as sets (case-insensitive, order-independent)
        # Use lowercase for comparison to treat "Backend" and "backend" as same
        original_set = {label.lower() for label in original_issues_keys}
        current_set = {label.lower() for label in current_issues_keys}
        return original_set != current_set

    def update_issues_data(self, issue_key: str) -> None:
        if issue_key:
            self._issues_keys.add(issue_key)


# ============================================================================
# Numeric and Selection Widgets
# ============================================================================


class NumericInputWidget(Input, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified numeric/float input widget that works in both CREATE and UPDATE modes.

    Features:
    - Numeric validation via Textual's Number validator
    - Mode-aware behavior (CREATE vs UPDATE)
    - Change tracking for UPDATE mode
    - Proper formatting for Jira API
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        # CREATE mode parameters
        placeholder: str = '123.45',
        # UPDATE mode parameters
        original_value: float | None = None,
        field_supports_update: bool = True,
    ):
        """
        Initialize a NumericInputWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            placeholder: Placeholder text for the input
            original_value: Original value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
        """
        # Initialize Input with numeric validation and common parameters
        # Number validator should allow empty if field is not required
        # Set valid_empty=True for non-required fields to prevent red highlighting on empty values
        super().__init__(
            id=field_id,
            placeholder=placeholder,
            validators=[Number()] if required else [],
            valid_empty=not required,  # Allow empty values when field is not required
            type='number' if mode == FieldMode.UPDATE else 'text',
        )

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            # Convert original_value to string for display in Input widget
            str_value = str(original_value) if original_value is not None else ''
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
            self.value = str_value
            self.add_class('issue_details_input_field')
        else:
            # CREATE mode specific setup
            self.add_class('create-work-item-float-input')

    def get_value_for_update(self) -> float | None:
        """
        Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            A float value, or None if the field has no value or invalid format
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        # Check if value exists and is not empty string (empty Input has value="")
        if self.value and self.value.strip():
            try:
                return float(self.value)
            except ValueError:
                return None
        return None

    def get_value_for_create(self) -> float | None:
        """
        Returns the value formatted for Jira API creation (CREATE mode).

        Returns:
            A float value, or None if the field has no value or invalid format
        """
        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        if self.value and self.value.strip():
            try:
                return float(self.value)
            except ValueError:
                return None
        return None

    def on_key(self, event: Key) -> None:
        """
        Handle key press events to restrict input to numeric characters and decimal point.

        Only allows:
        - Digits (0-9)
        - Decimal point (.) - but only one
        - Backspace, Delete, Arrow keys, Home, End (for editing)
        - Minus sign (-) at the beginning for negative numbers

        Args:
            event: The key event
        """
        # Allow control keys for navigation and editing
        control_keys = {
            'backspace',
            'delete',
            'left',
            'right',
            'home',
            'end',
            'tab',
            'escape',
            'enter',
            'up',
            'down',
        }

        if event.key in control_keys:
            return

        # Allow digits
        if event.character and event.character.isdigit():
            return

        # Allow decimal point if there isn't one already
        if event.character == '.':
            if '.' not in self.value:
                return
            else:
                # Already has a decimal point, prevent this key
                event.prevent_default()
                return

        # Allow minus sign only at the beginning
        if event.character == '-':
            if not self.value or self.cursor_position == 0:
                return
            else:
                # Minus sign not at beginning, prevent
                event.prevent_default()
                return

        # All other characters are not allowed
        event.prevent_default()

    @property
    def value_has_changed(self) -> bool:
        """
        Determines if the current value differs from the original value (UPDATE mode).

        Returns:
            True if value has changed, False otherwise
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        # Original value is None or empty
        if self.original_value is None:
            # Changed if current value is not empty
            return bool(self.value and self.value.strip())

        # Current value is empty or whitespace - this is a change from a numeric value
        if ValidationUtils.is_empty_or_whitespace(self.value):
            return True

        # Both exist - compare numeric values
        try:
            current_float = float(self.value)
            return self.original_value != current_float
        except (ValueError, TypeError):
            # Invalid current value is considered a change
            return True


class SelectionWidget(Select, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified selection widget that works in both CREATE and UPDATE modes.

    Features:
    - Dropdown selection from allowed values
    - Mode-aware behavior (CREATE vs UPDATE)
    - Change tracking for UPDATE mode
    - Proper formatting for Jira API
    - Support for required/optional fields

    Usage in CREATE mode:
    ```python
    widget = SelectionWidget(
        mode=FieldMode.CREATE,
        field_id='customfield_10002',
        jira_field_key='customfield_10002',
        title='Priority',
        options=[('High', '1'), ('Medium', '2'), ('Low', '3')],
        required=True,
        allow_blank=False,
    )
    # Get value (returns the id)
    widget.value
    ```

    Usage in UPDATE mode:
    ```python
    widget = SelectionWidget(
        mode=FieldMode.UPDATE,
        field_id='customfield_10002',
        jira_field_key='customfield_10002',
        title='Priority',
        options=[('High', '1'), ('Medium', '2'), ('Low', '3')],
        original_value='2',
        field_supports_update=True,
        allow_blank=True,
    )
    # Check changes
    widget.value_has_changed
    # Get value for API
    widget.get_value_for_update()
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        options: list[tuple[str, str]],
        title: str | None = None,
        required: bool = False,
        # CREATE mode parameters
        initial_value: Any = Select.NULL,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
        # Common parameters
        allow_blank: bool = True,
        prompt: str | None = None,
    ):
        """Initializes a SelectionWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            options: List of (display_name, value) tuples for the dropdown
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            initial_value: Initial selected value (CREATE mode only)
            original_value: Original value from Jira (UPDATE mode only)
            field_supports_update: Whether field can be updated (UPDATE mode only)
            allow_blank: Whether to allow blank/empty selection
            prompt: Prompt text for the dropdown
        """

        # Determine the appropriate prompt
        display_prompt = prompt or f'Select {title or field_id}'

        # Initialize Select with common parameters
        super().__init__(
            options=options,
            prompt=display_prompt,
            id=field_id,
            allow_blank=allow_blank,
            compact=True,
            type_to_search=True,
        )

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
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
            # Set initial value for UPDATE mode
            if original_value is not None:
                self.value = original_value
            self.add_class('create-work-item-generic-selector')
        else:
            # CREATE mode specific setup
            if initial_value != Select.NULL:
                self.value = initial_value
            self.add_class('create-work-item-generic-selector')

    def get_value_for_update(self) -> dict | None:
        """
        Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            A dictionary with the id of the selected option, or None if no selection
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        if self.selection is None:
            return None
        return {'id': self.selection}

    def get_value_for_create(self) -> dict | None:
        """
        Returns the value formatted for Jira API creation (CREATE mode).

        Returns:
            A dictionary with the id of the selected option, or None if no selection
        """
        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        if self.value and self.value != Select.NULL:
            return {'id': self.value}
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

        # No original value
        if not self.original_value:
            # Changed if we now have a selection
            return bool(self.selection)

        # Had original value, now no selection
        if not self.selection:
            return True

        # Both exist - compare them
        return self.original_value != self.selection


class DescriptionWidget(TextArea, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified description textarea widget that works in both CREATE and UPDATE modes.

    Features:
    - Multi-line text input for descriptions
    - Mode-aware behavior (CREATE vs UPDATE)
    - Change tracking for UPDATE mode
    - Required field support

    Usage in CREATE mode:
        widget = DescriptionWidget(
            mode=FieldMode.CREATE,
            field_id="description",
            title="Description",
            required=False
        )
        # Get value: widget.text

    Usage in UPDATE mode:
        widget = DescriptionWidget(
            mode=FieldMode.UPDATE,
            field_id="description",
            title="Description",
            original_value="Original description text",
            field_supports_update=True
        )
        # Check changes: widget.value_has_changed
        # Get value for API: widget.get_value_for_update()
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str = 'description',
        title: str | None = None,
        required: bool = False,
        # UPDATE mode parameters
        original_value: str | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a DescriptionWidget.

        Args:
            mode: the field mode (CREATE or UPDATE)
            field_id: field identifier (defaults to 'description')
            title: display title (defaults to 'Description')
            required: whether the field is required (mainly for CREATE mode)
            original_value: original description text from Jira (UPDATE mode only)
            field_supports_update: whether field can be updated (UPDATE mode only)
        """

        # initialize TextArea
        super().__init__(text=original_value or '', id=field_id)

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key='description',
            title=title or 'Description',
            required=required,
            compact=True,
        )

        # Mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key='description',
                original_value=original_value or '',
                field_supports_update=field_supports_update,
            )
            self.add_class('issue_details_input_field')
        else:
            # CREATE mode specific CSS
            self.add_class('create-work-item-description')

    def get_value_for_update(self) -> str | None:
        """Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            The description text, or None if empty
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        text = self.text.strip() if self.text else ''
        return text if text else None

    def get_value_for_create(self) -> str | None:
        """Returns the value formatted for Jira API creation (CREATE mode).

        Returns:
            The description text, or None if empty
        """
        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        text = self.text.strip() if self.text else ''
        return text if text else None

    @property
    def original_value(self) -> str:
        """Get the original description from Jira."""
        return self._original_value or ''

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original value (UPDATE mode).

        Returns:
            True if value has changed, False otherwise
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        original = self.original_value.strip()
        current = self.text.strip() if self.text else ''

        # Empty to empty - no change
        if not original and not current:
            return False

        # Empty to value or value to empty - changed
        if not original or not current:
            return True

        # Both exist - compare them
        return original != current

    def set_original_value(self, value: str) -> None:
        """Sets the original value for change tracking (UPDATE mode).

        Args:
            value: The original description text from Jira
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('set_original_value() only valid in UPDATE mode')

        self._original_value = value


class MultiSelectWidget(SelectionList[str], BaseFieldWidget, BaseUpdateFieldWidget):
    """Multi-select widget using Textual's native SelectionList for array fields.

    This widget handles array fields (like components) that allow multiple selections.
    Uses Textual's `SelectionList` widget for inline multi-select with checkboxes.

    Features:
    - Native Textual SelectionList with checkboxes
    - Mode-aware behavior (CREATE vs UPDATE)
    - Change tracking for UPDATE mode
    - Proper formatting for Jira API

    Usage in UPDATE mode:
    ```python
    widget = MultiSelectWidget(
        mode=FieldMode.UPDATE,
        field_id='components',
        jira_field_key='components',
        title='Components',
        options=[('Backend', '10001'), ('Frontend', '10002')],
        original_value=['10001'],
        field_supports_update=True,
    )
    # Check changes
    widget.value_has_changed
    # Get value for API
    widget.get_value_for_update()
    ```
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        jira_field_key: str,
        options: list[tuple[str, str]],
        title: str | None = None,
        required: bool = False,
        # CREATE mode parameters
        initial_value: list[str] | None = None,
        # UPDATE mode parameters
        original_value: list[str] | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a MultiSelectWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (Jira field key)
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            options: List of (display_name, value) tuples for checkboxes
            title: Display title (defaults to field_id)
            required: Whether the field is required (mainly for CREATE mode)
            initial_value: Initial selected values as list of IDs (CREATE mode)
            original_value: Original values from Jira as list of IDs (UPDATE mode)
            field_supports_update: Whether field can be updated (UPDATE mode)
        """

        # Convert options to Selection objects
        selections = [
            Selection(display_name, value, initial_state=False) for display_name, value in options
        ]

        # initialize SelectionList
        super().__init__(*selections, id=field_id)

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title,
            required=required,
            compact=False,  # SelectionList needs vertical space
        )

        # Store original value for change tracking
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value or [],
                field_supports_update=field_supports_update,
            )
            # Pre-select original values
            if original_value:
                for value_id in original_value:
                    self.select(value_id)
        else:
            # CREATE mode
            if initial_value:
                for value_id in initial_value:
                    self.select(value_id)

    def get_value_for_update(self) -> list[dict] | None:
        """Returns the value formatted for Jira API updates (UPDATE and CREATE modes).

        Returns:
            A list of dicts with IDs of selected options, or empty list if no selection
        """

        if self.mode not in (FieldMode.UPDATE, FieldMode.CREATE):
            raise ValueError('get_value_for_update() only valid in UPDATE or CREATE mode')

        selected = self.selected
        if not selected:
            return []
        return [{'id': item_id} for item_id in selected]

    def get_value_for_create(self) -> list[dict] | None:
        """Returns the value formatted for Jira API creation (CREATE mode).

        Returns:
            A list of dicts with IDs of selected options, or None if no selection
        """

        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        selected = self.selected
        if not selected:
            return None
        return [{'id': item_id} for item_id in selected]

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current selection differs from the original value (UPDATE mode).

        Returns:
            True if selection has changed, False otherwise
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        current_selected = set(self.selected)
        original_selected = set(self.original_value or [])

        return current_selected != original_selected
