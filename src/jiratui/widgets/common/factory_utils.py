from typing import Any

from textual.widget import Widget
from textual.widgets import Select

from jiratui.widgets.common.base_fields import FieldMode
from jiratui.widgets.common.constants import CustomFieldType
from jiratui.widgets.common.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    SelectionWidget,
    TextInputWidget,
    URLWidget,
)


class FieldMetadata:
    """
    Parsed field metadata from Jira create/edit metadata.

    This class extracts and normalizes the common properties needed
    to instantiate widgets, hiding the complexity of navigating the
    Jira metadata structure.
    """

    def __init__(self, raw_metadata: dict):
        """
        Initialize from raw Jira field metadata.

        Args:
            raw_metadata: Dictionary from Jira's create or edit metadata
        """
        self.raw = raw_metadata
        self.field_id: str = raw_metadata.get('fieldId', '')
        self.name: str = raw_metadata.get('name', '')
        self.key: str = raw_metadata.get('key', '')
        self.required: bool = raw_metadata.get('required', False)
        self.schema: dict = raw_metadata.get('schema', {})
        self.custom_type: str | None = self.schema.get('custom')
        self.schema_type: str = self.schema.get('type', '')
        self.allowed_values: list[dict] = raw_metadata.get('allowedValues', [])
        self.has_default: bool = raw_metadata.get('hasDefaultValue', False)
        self.default_value: dict | None = raw_metadata.get('defaultValue')
        self.operations: list[str] = raw_metadata.get('operations', [])

    @property
    def supports_update(self) -> bool:
        """Whether this field supports update operations."""
        return any(op in self.operations for op in ['set', 'add', 'edit', 'remove'])

    @property
    def is_custom_field(self) -> bool:
        """Whether this is a custom field (has schema.custom)."""
        return self.custom_type is not None

    def __repr__(self) -> str:
        return f'FieldMetadata(field_id={self.field_id!r}, name={self.name!r}, custom_type={self.custom_type!r})'


class AllowedValuesParser:
    """
    Parses Jira allowedValues into Select widget options.

    This handles the complexity of extracting display names and IDs
    from the various formats Jira uses for allowed values.
    """

    @staticmethod
    def parse_options(allowed_values: list[dict]) -> list[tuple[str, str]]:
        """
        Parse allowedValues into Select-compatible options.

        Args:
            allowed_values: List of value dictionaries from Jira metadata

        Returns:
            List of (display_name, id) tuples for Select widget
        """
        options: list[tuple[str, str]] = []
        # Handle None or empty allowed_values
        if not allowed_values:
            return options
        for value in allowed_values:
            # Try 'name' first, fall back to 'value'
            display_value = value.get('name') or value.get('value', '')
            value_id = value.get('id', '')
            if display_value and value_id:
                options.append((display_value, value_id))
        return options


class WidgetBuilder:
    """
    Factory methods for creating mode-aware widgets.

    This class provides simple builder functions that hide the complexity
    of instantiating widgets with the right parameters for CREATE vs UPDATE modes.
    """

    @staticmethod
    def build_user_picker(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: Any = None,
    ) -> Widget:
        """
        Build a UserPickerWidget for user selection fields.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current value (UPDATE mode only)

        Returns:
            UserPickerWidget instance
        """
        from jiratui.widgets.common.base_fields import UserPickerWidget

        if mode == FieldMode.CREATE:
            return UserPickerWidget(
                mode=mode,
                field_id=metadata.field_id,
                title=metadata.name,
                required=metadata.required,
            )
        else:
            # UPDATE mode - extract account ID from various formats
            account_id = None
            if current_value:
                if isinstance(current_value, dict):
                    account_id = current_value.get('accountId')
                elif isinstance(current_value, str):
                    # Handle composite format "internal_id:account-id"
                    account_id = (
                        current_value.split(':', 1)[1] if ':' in current_value else current_value
                    )

            return UserPickerWidget(
                mode=mode,
                field_id=metadata.field_id,
                title=metadata.name,
                original_value=account_id,
                field_supports_update=metadata.supports_update,
            )

    @staticmethod
    def build_numeric(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: float | None = None,
    ) -> Widget:
        """
        Build a NumericInputWidget for float/number fields.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current numeric value (UPDATE mode only)

        Returns:
            NumericInputWidget instance
        """
        if mode == FieldMode.CREATE:
            return NumericInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                title=metadata.name,
                required=metadata.required,
                placeholder=f'Enter value for {metadata.name}',
            )
        else:
            return NumericInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                title=metadata.name,
                original_value=current_value,
                field_supports_update=metadata.supports_update,
            )

    @staticmethod
    def build_selection(
        mode: FieldMode,
        metadata: FieldMetadata,
        options: list[tuple[str, str]],
        # CREATE mode parameters
        initial_value: Any = Select.BLANK,
        # UPDATE mode parameters
        current_value: str | None = None,
    ) -> Widget:
        """
        Build a SelectionWidget for dropdown selection fields.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            options: List of (display_name, id) tuples
            initial_value: Initial value (CREATE mode only)
            current_value: Current selected ID (UPDATE mode only)

        Returns:
            SelectionWidget instance
        """
        if mode == FieldMode.CREATE:
            # Determine allow_blank and initial value
            allow_blank = True
            if metadata.has_default and metadata.default_value:
                allow_blank = False
                initial_value = metadata.default_value.get('id', Select.BLANK)

            return SelectionWidget(
                mode=mode,
                field_id=metadata.field_id,
                options=options,
                title=metadata.name,
                required=metadata.required,
                initial_value=initial_value,
                allow_blank=allow_blank or (initial_value == Select.BLANK),
                prompt=f'Select {metadata.name}',
            )
        else:
            # UPDATE mode - extract ID from value
            value_id = None
            if current_value:
                if isinstance(current_value, dict):
                    value_id = current_value.get('id')
                elif isinstance(current_value, str):
                    value_id = current_value

            return SelectionWidget(
                mode=mode,
                field_id=metadata.field_id,
                options=options,
                title=metadata.name,
                original_value=value_id,
                field_supports_update=metadata.supports_update,
                allow_blank=not metadata.required,
                prompt=f'Select {metadata.name}',
            )

    @staticmethod
    def build_date(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: str | None = None,
    ) -> Widget:
        """
        Build a DateInputWidget for date picker fields.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current date value (UPDATE mode only)

        Returns:
            DateInputWidget instance
        """
        widget = DateInputWidget(
            mode=mode,
            field_id=metadata.field_id,
            title=metadata.name,
            required=metadata.required,
            original_value=current_value if mode == FieldMode.UPDATE else None,
            field_supports_update=metadata.supports_update if mode == FieldMode.UPDATE else True,
        )

        if mode == FieldMode.UPDATE and metadata.required:
            widget.valid_empty = False

        return widget

    @staticmethod
    def build_datetime(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: str | None = None,
    ) -> Widget:
        """
        Build a DateTimeInputWidget for datetime fields.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current datetime value (UPDATE mode only)

        Returns:
            DateTimeInputWidget instance
        """
        widget = DateTimeInputWidget(
            mode=mode,
            field_id=metadata.field_id,
            title=metadata.name,
            required=metadata.required,
            original_value=current_value if mode == FieldMode.UPDATE else None,
            field_supports_update=metadata.supports_update if mode == FieldMode.UPDATE else True,
        )

        if mode == FieldMode.UPDATE and metadata.required:
            widget.valid_empty = False

        return widget

    @staticmethod
    def build_text(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: str | None = None,
    ) -> Widget:
        """
        Build a TextInputWidget for text fields.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current text value (UPDATE mode only)

        Returns:
            TextInputWidget instance
        """
        if mode == FieldMode.CREATE:
            return TextInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                title=metadata.name,
                required=metadata.required,
                placeholder=f'Enter value for {metadata.name}...',
            )
        else:
            return TextInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                title=metadata.name,
                original_value=current_value or '',
                field_supports_update=metadata.supports_update,
            )

    @staticmethod
    def build_url(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: str | None = None,
    ) -> Widget:
        """
        Build a unified URLWidget for URL fields.

        Auto-adds 'https://' prefix when input loses focus if no protocol is present.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current URL value (UPDATE mode only)

        Returns:
            URLWidget instance for URL input
        """

        return URLWidget(
            mode=mode,
            field_id=metadata.field_id,
            title=metadata.name,
            required=metadata.required,
            original_value=current_value if mode == FieldMode.UPDATE else None,
            field_supports_update=metadata.supports_update if mode == FieldMode.UPDATE else True,
        )

    @staticmethod
    def build_labels(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: list[str] | None = None,
    ) -> Widget:
        """
        Build a LabelsWidget for comma-separated labels input.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current labels list (UPDATE mode only)

        Returns:
            LabelsWidget instance
        """

        return LabelsWidget(
            mode=mode,
            field_id=metadata.field_id,
            title=metadata.name,
            required=metadata.required,
            current_value=current_value or [],
            field_supports_update=metadata.supports_update,
        )

    @staticmethod
    def build_multicheckboxes(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: list[dict] | None = None,
    ) -> Widget:
        """
        Build a multi-checkbox widget.

        Args:
            mode: CREATE or UPDATE mode
            metadata: Parsed field metadata
            current_value: Current selected values (UPDATE mode only)

        Returns:
            Widget instance for multi-checkbox input
        """
        # Use MultiSelectWidget for both CREATE and UPDATE modes

        # Extract current value IDs for UPDATE mode
        current_ids = []
        if mode == FieldMode.UPDATE and current_value:
            for item in current_value:
                if isinstance(item, dict) and 'id' in item:
                    current_ids.append(str(item['id']))
                elif hasattr(item, 'id'):
                    current_ids.append(str(item.id))

        # Parse options from allowed values
        options = AllowedValuesParser.parse_options(metadata.allowed_values or [])

        return MultiSelectWidget(
            mode=mode,
            field_id=metadata.field_id,
            options=options,
            title=metadata.name,
            required=metadata.required,
            initial_value=current_ids if mode == FieldMode.CREATE else [],
            original_value=current_ids if mode == FieldMode.UPDATE else [],
            field_supports_update=metadata.supports_update if mode == FieldMode.UPDATE else True,
        )


def map_field_to_widget(
    mode: FieldMode,
    metadata: FieldMetadata,
    current_value: Any = None,
) -> Widget | None:
    """
    Map a field metadata to the appropriate widget based on its type.

    This is the main entry point for widget creation - it examines the field's
    schema and custom type, then delegates to the appropriate WidgetBuilder method.

    Args:
        mode: CREATE or UPDATE mode
        metadata: Parsed field metadata
        current_value: Current field value (for UPDATE mode)

    Returns:
        Widget instance, or None if the field type is not supported
    """
    builder = WidgetBuilder()

    # Handle custom fields
    if metadata.is_custom_field:
        custom_type = metadata.custom_type

        if custom_type == CustomFieldType.USER_PICKER.value:
            return builder.build_user_picker(mode, metadata, current_value)

        elif custom_type == CustomFieldType.FLOAT.value:
            return builder.build_numeric(mode, metadata, current_value)

        elif custom_type == CustomFieldType.SELECT.value:
            if metadata.allowed_values:
                options = AllowedValuesParser.parse_options(metadata.allowed_values)
                return builder.build_selection(mode, metadata, options, current_value=current_value)

        elif custom_type == CustomFieldType.DATE_PICKER.value:
            return builder.build_date(mode, metadata, current_value)

        elif custom_type == CustomFieldType.DATETIME.value:
            return builder.build_datetime(mode, metadata, current_value)

        elif custom_type == CustomFieldType.TEXT_FIELD.value:
            return builder.build_text(mode, metadata, current_value)

        elif custom_type == CustomFieldType.URL.value:
            return builder.build_url(mode, metadata, current_value)

        elif custom_type == CustomFieldType.LABELS.value:
            return builder.build_labels(mode, metadata, current_value)

        elif custom_type == CustomFieldType.MULTI_CHECKBOXES.value:
            return builder.build_multicheckboxes(mode, metadata, current_value)

    # Handle non-custom fields
    else:
        schema_type = metadata.schema_type.lower()

        if schema_type == 'number':
            return builder.build_numeric(mode, metadata, current_value)

        elif schema_type == 'date':
            return builder.build_date(mode, metadata, current_value)

        # Handle fields with allowedValues
        elif metadata.allowed_values:
            options = AllowedValuesParser.parse_options(metadata.allowed_values)
            return builder.build_selection(mode, metadata, options, current_value=current_value)

        # Handle labels array field (CREATE mode special case)
        elif (
            mode == FieldMode.CREATE
            and schema_type == 'array'
            and metadata.schema.get('items') == 'string'
            and metadata.field_id == 'labels'
        ):
            return builder.build_labels(mode, metadata, None)

    # Default fallback - text input
    return builder.build_text(mode, metadata, current_value)


def should_skip_field(
    field_id: str,
    skip_list: list[str],
) -> bool:
    """
    Check if a field should be skipped during widget creation.

    Args:
        field_id: The field ID to check
        skip_list: List of field IDs to skip

    Returns:
        True if field should be skipped, False otherwise
    """
    return field_id in skip_list
