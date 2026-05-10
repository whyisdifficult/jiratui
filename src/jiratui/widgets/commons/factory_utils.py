from typing import Any

from textual.widget import Widget
from textual.widgets import Select

from jiratui.config import CONFIGURATION
from jiratui.widgets.commons import FieldMode
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    ReadOnlyPlainTextTextAreaWidget,
    SelectionWidget,
    SingleUserPickerWidget,
    TextInputWidget,
    URLWidget,
)


class FieldMetadata:
    """Parsed field metadata from Jira create/edit metadata.

    This class extracts and normalizes the common properties needed to instantiate widgets, hiding the complexity of
    navigating the Jira metadata structure.
    """

    def __init__(self, raw_metadata: dict):
        """Initializes from raw Jira field metadata.

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
        return f'FieldMetadata(field_id={self.field_id!r}, key={self.key!r}, name={self.name!r}, custom_type={self.custom_type!r})'


class AllowedValuesParser:
    """Parses the `allowedValues` field found in a Jira field's metadata dictionary into Select widget options.

    This handles the complexity of extracting display names and IDs from the various formats Jira uses for allowed
    values.
    """

    @staticmethod
    def parse_options(allowed_values: list[dict]) -> list[tuple[str, str]]:
        """Parses `allowedValues` into Select-compatible options.

        Args:
            allowed_values: list of value dictionaries from Jira metadata.

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
    """Factory methods for creating mode-aware widgets.

    This class provides simple builder functions that hide the complexity of instantiating widgets with the right
    parameters for CREATE vs UPDATE modes.
    """

    @staticmethod
    def build_user_picker(
        mode: FieldMode, metadata: FieldMetadata, current_value: dict = None
    ) -> Widget:
        """Builds a `SingleUserPickerWidget` for user selection fields.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            A SingleUserPickerWidget instance.

        Example:
        build_user_picker(FieldMode.UPDATE, FieldMetadata(), current_value={'accountId': '123', 'displayName': 'Bart'})
        """

        if mode == FieldMode.CREATE:
            return SingleUserPickerWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
                title=metadata.name,
                required=metadata.required,
            )
        else:
            # UPDATE mode
            original_value: dict | None = None
            if current_value:
                name = current_value.get('displayName', current_value.get('name', ''))
                if current_value.get('accountId') and name and (cleaned_name := name.strip()):
                    original_value = {
                        'account_id': current_value.get('accountId'),
                        'name': cleaned_name,
                    }
                else:
                    raise ValueError('Missing required accountId and/or displayName or name')
            return SingleUserPickerWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
                title=metadata.name,
                original_value=original_value,
                supports_update=metadata.supports_update,
                required=metadata.required,
            )

    @staticmethod
    def build_numeric(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: float | None = None,
    ) -> Widget:
        """Builds a `NumericInputWidget` for float/number fields.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            A instance of NumericInputWidget.
        """

        if mode == FieldMode.CREATE:
            return NumericInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
                title=metadata.name,
                required=metadata.required,
                placeholder=f'Enter value for {metadata.name}',
            )
        else:
            return NumericInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
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
        initial_value: Any = Select.NULL,
        # UPDATE mode parameters
        current_value: str | None = None,
    ) -> Widget:
        """Builds a `SelectionWidget` for dropdown selection fields.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            options: List of (display_name, id) tuples
            initial_value: Initial value (CREATE mode only)
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            SelectionWidget instance
        """

        if mode == FieldMode.CREATE:
            # Determine allow_blank and initial value
            allow_blank = True
            if metadata.has_default and metadata.default_value:
                allow_blank = False
                initial_value = metadata.default_value.get('id', Select.NULL)

            return SelectionWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
                options=options,
                title=metadata.name,
                required=metadata.required,
                initial_value=initial_value,
                allow_blank=allow_blank or (initial_value == Select.NULL),
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
                jira_field_key=metadata.key,
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
        """Builds a `DateInputWidget` for date picker fields.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            DateInputWidget instance
        """
        widget = DateInputWidget(
            mode=mode,
            field_id=metadata.field_id,
            jira_field_key=metadata.key,
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
        """Builds a `DateTimeInputWidget` for datetime fields.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            DateTimeInputWidget instance
        """
        widget = DateTimeInputWidget(
            mode=mode,
            field_id=metadata.field_id,
            jira_field_key=metadata.key,
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
        """Builds a `TextInputWidget` for text fields.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            TextInputWidget instance
        """
        if mode == FieldMode.CREATE:
            return TextInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
                title=metadata.name,
                required=metadata.required,
                placeholder=f'Enter value for {metadata.name}...',
            )
        else:
            return TextInputWidget(
                mode=mode,
                field_id=metadata.field_id,
                jira_field_key=metadata.key,
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
        """Builds a unified `URLWidget` for URL fields.

        Auto-adds 'https://' prefix when input loses focus if no protocol is present.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            URLWidget instance for URL input
        """

        return URLWidget(
            mode=mode,
            field_id=metadata.field_id,
            jira_field_key=metadata.key,
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
        """Builds a `LabelsWidget` for comma-separated labels input.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            LabelsWidget instance
        """

        return LabelsWidget(
            mode=mode,
            field_id=metadata.field_id,
            jira_field_key=metadata.key,
            title=metadata.name,
            required=metadata.required,
            original_value=current_value or [],
            supports_update=metadata.supports_update,
        )

    @staticmethod
    def build_multicheckboxes(
        mode: FieldMode,
        metadata: FieldMetadata,
        # UPDATE mode parameters
        current_value: list[dict] | None = None,
    ) -> Widget:
        """Builds a `MultiSelectWidget` widget.

        This uses MultiSelectWidget for both CREATE and UPDATE modes.

        Args:
            mode: either CREATE or UPDATE mode.
            metadata: the field's metadata.
            current_value: the current value of the work item's field associated to this widget. This is only relevant
            when the mode is `FieldMode.UPDATE`.

        Returns:
            Widget instance for multi-checkbox input
        """

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
            jira_field_key=metadata.key,
            options=options,
            title=metadata.name,
            required=metadata.required,
            initial_value=current_ids if mode == FieldMode.CREATE else [],
            original_value=current_ids if mode == FieldMode.UPDATE else [],
            field_supports_update=metadata.supports_update if mode == FieldMode.UPDATE else True,
        )


def build_read_only_rich_text_widget(
    jira_field_key: str,
    field_name: str,
    required: bool = False,
    content: str | dict | None = None,
) -> ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget:
    """A factory method that builds a widget for displaying the content of a textarea field in read-only mode.

    Some Jira issue's fields can contain long rich text. Jira stores these values as either ADF
    (Atlassian Document Format), when using theJira CLoud Platform, or as plain text, when using the Jira DC Platform.

    JiraTUI will display these fields as either a Markdown widget or a TextArea widget according to these rules:

    1. if the value is a `dict` and contains text we assume that the field stores text as ADF. In this case this method
    will build an instance of `ADFTextAreaWidget`.

    2. if the value is a `str` and contains text we assume that the field stores the value as plain text. In this case
    this method will build an instance of `TextAreaWidget`.

    Args:
        jira_field_key: the Jira field's key (as found in the edit metadata of the Jira issue) that can be used for
        updating the field.
        field_name: the name of the field as found in the edit metadata of the Jira issue.
        required: indicates whether the field is required or not. This is used for setting the style of the widget.
        content: the actual content of the issue's field. This can be an ADF dict or string.

    Returns:
        An instance of `ADFTextAreaWidget` or `TextAreaWidget`.
    """

    if _adf_support_enabled():
        return ReadOnlyADFMarkdownTextAreaWidget(
            field_id=jira_field_key,
            jira_field_key=jira_field_key,
            title=field_name,
            required=required,
            original_value=content,  # type:ignore[arg-type]
        )
    return ReadOnlyPlainTextTextAreaWidget(
        field_id=jira_field_key,
        jira_field_key=jira_field_key,
        title=field_name,
        required=required,
        original_value=content or '',  # type:ignore[arg-type]
    )


def _adf_support_enabled() -> bool:
    return CONFIGURATION.get().cloud and CONFIGURATION.get().jira_api_version == 3
