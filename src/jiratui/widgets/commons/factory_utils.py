"""This module provides a Factory Pattern implementation for creating mode-aware Jira field
widgets.

Instead of exposing complex widget initialization logic directly to callers, the `WidgetBuilder` class encapsulates
all the complexity of instantiating widgets with correct parameters for CREATE and UPDATE modes.

The module consists of three key classes:

- `FieldMetadata`: Normalizes and parses raw Jira field metadata
- `AllowedValuesParser`: Extracts Select options from allowed values
- `WidgetBuilder`: Factory for creating mode-aware widgets with a single method call
"""

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

    **Purpose**: Jira's field metadata is deeply nested and uses inconsistent naming conventions. `FieldMetadata`
    extracts and normalizes the properties needed to instantiate widgets, hiding that complexity.

    **Simplifies Complex Jira Metadata**

    ```python
    # Raw Jira metadata (complex)
    raw = {
        'fieldId': 'customfield_10001',
        'name': 'Story Points',
        'schema': {
            'type': 'number',
            'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:float',
        },
        'operations': ['set', 'edit'],
        # ... many more properties
    }

    # FieldMetadata simplification
    metadata = FieldMetadata(raw)
    print(metadata.field_id)  # 'customfield_10001'
    print(metadata.supports_update)  # True (because 'set' or 'edit' in operations)
    ```
    """

    def __init__(self, raw_metadata: dict):
        """Initializes from raw Jira field metadata.

        Args:
            raw_metadata: Dictionary from Jira's create or edit metadata
        """

        self.raw = raw_metadata
        self.field_id: str = raw_metadata.get('fieldId', '')
        """Internal identifier (e.g., "project", "customfield_10001")"""
        self.name: str = raw_metadata.get('name', '')
        """Display name for the field (used as widget title)"""
        self.key: str = raw_metadata.get('key', '')
        """Jira API field key for update operations"""
        self.required: bool = raw_metadata.get('required', False)
        """Whether the field is mandatory"""
        self.schema: dict = raw_metadata.get('schema', {})
        self.custom_type: str | None = self.schema.get('custom')
        """Custom field type identifier (if applicable)"""
        self.schema_type: str = self.schema.get('type', '')
        """Field data type (e.g., "string", "date", "user")"""
        self.allowed_values: list[dict] = raw_metadata.get('allowedValues', [])
        self.has_default: bool = raw_metadata.get('hasDefaultValue', False)
        self.default_value: dict | None = raw_metadata.get('defaultValue')
        self.operations: list[str] = raw_metadata.get('operations', [])
        """Supported operations: set, add, edit, remove"""

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

    **Purpose**: Jira stores allowed values in various formats. This utility standardizes extraction into Select
    widget-compatible (`display_name`, `id`) tuples.
    """

    @staticmethod
    def parse_options(allowed_values: list[dict]) -> list[tuple[str, str]]:
        """Converts Jira's allowed values format to `Textual.Select` widget options.

        Args:
            allowed_values: list of value dictionaries from Jira metadata.

        Returns:
            List of (display_name, id) tuples for Select widget

        Example:
        # Jira's issue type allowed values
        allowed = [
            {'id': '10001', 'name': 'Bug'},
            {'id': '10002', 'name': 'Story'}
        ]

        options = AllowedValuesParser.parse_options(allowed)
        # Result: [('Bug', '10001'), ('Story', '10002')]
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
    """WidgetBuilder is a static factory class that creates mode-aware widgets. Each method follows the same pattern:

    - Receives `FieldMode`, `FieldMetadata`, and optional `current_value`
    - Handles CREATE mode — Creates fresh widgets with placeholders and default values
    - Handles UPDATE mode — Populates widgets with current values and enables change tracking
    - Returns The appropriate widget instance, fully configured
    """

    @staticmethod
    def build_user_picker(
        mode: FieldMode, metadata: FieldMetadata, current_value: dict = None
    ) -> Widget:
        """Builds a SingleUserPickerWidget for single user selection with autocomplete.

        Creates an autocomplete-enabled widget that allows users to select a single
        assignee, reporter, or other user field. The widget searches Jira users by
        display name and email address as the user types. Selection requires the user's
        account ID, which is stored internally while the display name is shown to the
        user. In UPDATE mode, the widget displays the currently assigned user and tracks
        changes.

        Args:
            mode: Either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: Field metadata parsed from Jira's create/edit metadata. Used to
                determine if the field is required and for display naming.
            current_value: The current user value in UPDATE mode as a dict containing
                the user object from Jira (typically includes 'accountId', 'displayName',
                'emailAddress'). Ignored in CREATE mode. Defaults to None.

        Returns:
            A configured SingleUserPickerWidget instance with autocomplete enabled.
            The widget searches users in real-time as the user types. Minimum 2 characters
            required to trigger search.

        Example:
        # Assignee field in CREATE mode
        widget = WidgetBuilder.build_user_picker(
            FieldMode.CREATE,
            FieldMetadata({'fieldId': 'assignee', 'name': 'Assignee'})
        )

        # Assignee field in UPDATE mode with current user
        widget = WidgetBuilder.build_user_picker(
            FieldMode.UPDATE,
            metadata,
            current_value={
                'accountId': 'abc123xyz',
                'displayName': 'John Doe',
                'emailAddress': 'john.doe@example.com'
            }
        )
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
        """Builds a NumericInputWidget for numeric input fields (int, float, decimal).

        Creates a numeric input widget that validates input and converts between string
        and numeric formats. Supports both integer and floating-point numbers. In UPDATE
        mode, the widget tracks changes and enables partial updates.

        Args:
            mode: Either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: Field metadata parsed from Jira's create/edit metadata.
            current_value: The current numeric value (UPDATE mode only). Can be a float,
                int, or None. Ignored in CREATE mode. Defaults to None.

        Returns:
            A configured NumericInputWidget instance with input validation enabled.

        Example:
        # Story Points field (common in Agile boards)
        widget = WidgetBuilder.build_numeric(
            FieldMode.CREATE,
            FieldMetadata({'fieldId': 'story_points', 'name': 'Story Points'})
        )
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
        """Builds a SelectionWidget for single-select dropdown fields.

        Creates a dropdown widget that allows users to select exactly one value from a list of options. Options can be
        provided directly or extracted from the field's allowed values in metadata. In CREATE mode, an optional
        default/initial value can be set. In UPDATE mode, the widget displays the current value and tracks changes.

        Args:
            mode: Either [FieldMode.CREATE](#jiratui.widgets.commons.base.FieldMode.CREATE) or
            [FieldMode.UPDATE](#jiratui.widgets.commons.base.FieldMode.UPDATE).
            metadata: Field metadata parsed from Jira's create/edit metadata. Used to extract allowed values if options
            are not explicitly provided.
            options: List of `(display_name, id)` tuples representing dropdown choices. If `None`, allowed values are
            extracted from metadata.allowed_values. Each tuple's second element is the value sent to Jira. Defaults to
            `None`.
            initial_value: The default/initial selection in CREATE mode. If provided, this option will be pre-selected
            when the widget is first displayed. Ignored in UPDATE mode. Defaults to `None`.
            current_value: The current selected value in UPDATE mode (typically an ID). Ignored in CREATE mode. Defaults
            to `None`.

        Returns:
            A configured SelectionWidget instance with type-to-search functionality.
            Users can type to quickly filter and select options.

        Raises:
            ValueError: If options are neither provided nor available in metadata.

        Example:
        # Issue type selection with explicit options
        options = [
            ("Bug", "10001"),
            ("Story", "10002"),
            ("Task", "10003")
        ]
        widget = WidgetBuilder.build_selection(
            FieldMode.CREATE,
            metadata,
            options=options,
            initial_value="10002"  # Pre-select Story
        )

        # Priority selection extracted from metadata
        widget = WidgetBuilder.build_selection(
            FieldMode.UPDATE,
            metadata,
            current_value="High"
        )
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
        """Builds a DateInputWidget for date picker fields.

        Creates a date input widget that enforces ISO 8601 date format (YYYY-MM-DD).
        The widget includes date validation and optional required field enforcement.
        In UPDATE mode, the widget is pre-populated with the current date and tracks changes.

        Args:
            mode: Either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: Field metadata parsed from Jira's create/edit metadata.
            current_value: The current date value in ISO format, e.g. '2026-05-24' (UPDATE mode only). Ignored in
            CREATE mode. Defaults to None.

        Returns:
            A configured DateInputWidget instance. If the field is required in UPDATE mode, the widget will not accept
            empty values.
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
        """Builds a [DateTimeInputWidget](#jiratui.widgets.commons.widgets.DateTimeInputWidget)  for date and time picker fields.

        Creates a datetime input widget that enforces ISO 8601 datetime format (`YYYY-MM-DDTHH:MM:SS` format). The
        widget includes both date and time validation with a masked input interface for easy data entry. In UPDATE mode,
        the widget is pre-populated with the current datetime and tracks changes.

        Args:
            mode: Either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: Field metadata parsed from Jira's create/edit metadata.
            current_value: The current datetime value in ISO 8601 format,
                e.g. '2026-05-24T14:30:00' (UPDATE mode only). Ignored in CREATE mode.
                Defaults to None.

        Returns:
            A configured DateTimeInputWidget instance with masked input for date and time components. If the field is
            required in UPDATE mode, the widget will not accept empty values.

        Example:
        # Due date field with time component
        widget = WidgetBuilder.build_datetime(
            FieldMode.UPDATE,
            metadata,
            current_value="2026-05-24T14:30:00"
        )
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
        """Builds a [TextInputWidget](#jiratui.widgets.commons.widgets.TextInputWidget) for single-line text fields.

        Creates a text input widget configured for the specified mode. In CREATE mode, the widget displays a helpful
        placeholder. In UPDATE mode, the widget is pre-populated with the current value and tracks changes for partial
        updates.

        Args:
            mode: either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: field metadata parsed from Jira's create/edit metadata. Used to extract the field ID, API key,
            display name, and required status.
            current_value: the current value of the field (UPDATE mode only). Ignored when mode is CREATE. Defaults to
            None.

        Returns:
            A configured TextInputWidget instance. The widget will be marked as required if metadata.required is True.

        Example:
        # CREATE mode - empty field ready for input
        widget = WidgetBuilder.build_text(
            FieldMode.CREATE, FieldMetadata({'fieldId': 'summary', 'name': 'Summary', 'required': True})
        )

        # UPDATE mode - pre-populated with current value
        widget = WidgetBuilder.build_text(FieldMode.UPDATE, metadata, current_value="Current summary text")
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
        """Builds a [URLWidget](#jiratui.widgets.commons.widgets.URLWidget) for URL input fields with automatic
        protocol handling.

        Creates a URL input widget that intelligently handles URL formatting. If the
        user enters a URL without a protocol (e.g., 'example.com'), the widget
        automatically prepends 'https://' when focus is lost.

        Args:
            mode: either `FieldMode.CREATE` or `FieldMode.UPDATE`.
            metadata: field metadata parsed from Jira's create/edit metadata.
            current_value: the current URL value (UPDATE mode only). Ignored in CREATE mode. Defaults to None.

        Returns:
            A configured URLWidget instance with automatic protocol handling enabled.

        Example:
        # User enters 'example.com' → becomes 'https://example.com'
        widget = WidgetBuilder.build_url(FieldMode.CREATE, metadata)
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
        """Builds a [LabelsWidget](#jiratui.widgets.commons.widgets.LabelsWidget) for comma-separated label/tag input.

        Creates a widget for entering and managing work item labels. Users type labels
        separated by commas; the widget converts them to the list format required by
        Jira's API. Supports both CREATE mode (empty) and UPDATE mode (pre-populated
        with existing labels).

        Args:
            mode: Either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: Field metadata parsed from Jira's create/edit metadata.
            current_value: The current list of labels (UPDATE mode only). If provided,
                labels will be pre-populated in the widget. Defaults to an empty list.

        Returns:
            A configured LabelsWidget instance.

        Example:
        # User enters: "bug, performance, backend"
        # Widget converts to: ["bug", "performance", "backend"] for Jira
        widget = WidgetBuilder.build_labels(
            FieldMode.UPDATE,
            metadata,
            current_value=["existing-label"]
        )
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
        """Builds a MultiSelectWidget for multi-select checkbox fields.

        Creates a multi-select dropdown widget that allows users to select multiple
        values from a list of options via checkboxes. Values are selected by checking
        boxes in a dropdown menu. In CREATE mode, the widget starts empty. In UPDATE
        mode, the widget is pre-populated with all currently selected values and tracks
        which selections have been added, removed, or modified.

        Args:
            mode: Either FieldMode.CREATE or FieldMode.UPDATE.
            metadata: Field metadata parsed from Jira's create/edit metadata. Used to
                extract allowed values and determine if the field is required.
            current_value: List of currently selected value IDs (UPDATE mode only).
                Each item in the list should correspond to one of the available options.
                If provided, these options will be pre-checked in the widget. Ignored in
                CREATE mode. Defaults to an empty list if not provided.

        Returns:
            A configured MultiSelectWidget instance with checkbox-based selection.
            The dropdown displays all available options with checkboxes; users check
            or uncheck to modify their selection.

        Example:
        # Component selection in CREATE mode
        widget = WidgetBuilder.build_multicheckboxes(
            FieldMode.CREATE,
            FieldMetadata({
                'fieldId': 'components',
                'name': 'Components',
                'allowedValues': [
                    {'id': 'comp-1', 'name': 'Frontend'},
                    {'id': 'comp-2', 'name': 'Backend'},
                    {'id': 'comp-3', 'name': 'Database'}
                ]
            })
        )

        # Component selection in UPDATE mode with current selections
        widget = WidgetBuilder.build_multicheckboxes(
            FieldMode.UPDATE,
            metadata,
            current_value=['comp-1', 'comp-3']  # Frontend and Database selected
        )
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
    will build an instance of [ReadOnlyADFMarkdownTextAreaWidget](#jiratui.widgets.commons.adf.ReadOnlyADFMarkdownTextAreaWidget).

    2. if the value is a `str` and contains text we assume that the field stores the value as plain text. In this case
    this method will build an instance of [ReadOnlyPlainTextTextAreaWidget](#jiratui.widgets.commons.widgets.ReadOnlyPlainTextTextAreaWidget).

    This function creates a read-only textarea widget suitable for displaying field values that contain formatted
    text. The widget type is automatically determined based on the content format: if the content is in Atlassian
    Document Format (ADF) (JSON-like structure), a
    [ReadOnlyADFMarkdownTextAreaWidget](#jiratui.widgets.commons.adf.ReadOnlyADFMarkdownTextAreaWidget) is created for
    rendering the rich text as Markdown. Otherwise, a
    [ReadOnlyPlainTextTextAreaWidget](#jiratui.widgets.commons.widgets.ReadOnlyPlainTextTextAreaWidget) is created for
    plain text display.

    This method is typically used for displaying description, comment, or other rich-text fields in read-only mode
    without allowing user modification.

    Args:
        jira_field_key: the Jira field's key (as found in the edit metadata of the Jira issue) that can be used for
        updating the field.
        field_name: the name of the field as found in the edit metadata of the Jira issue.
        required: indicates whether the field is required or not. This is used for setting the style of the widget.
        content: the actual content of the issue's field. This can be an ADF dict or string.

    Returns:
        An instance of `ReadOnlyADFMarkdownTextAreaWidget` or `ReadOnlyPlainTextTextAreaWidget`.

    Example:
    ```python
    # Display plain text description
    widget = WidgetBuilder.build_read_only_rich_text_widget(
        jira_field_key='description',
        field_name='Description',
        required=True,
        content='This is a plain text description.',
    )

    # Display ADF-formatted description (rich text)
    adf_content = '{"version": 1, "type": "doc", "content": [...]}'
    widget = WidgetBuilder.build_read_only_rich_text_widget(
        jira_field_key='description', field_name='Description', content=adf_content
    )
    ```
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
