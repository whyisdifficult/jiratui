"""ADF TextArea Widget - Handles Atlassian Document Format conversion and rendering."""

import logging

from textual.widgets import Markdown

from jiratui.widgets.common.base_fields import (
    BaseFieldWidget,
    FieldMode,
)

logger = logging.getLogger('jiratui')


class ADFTextAreaWidget(Markdown, BaseFieldWidget):
    """
    Read-only Markdown widget that handles Atlassian Document Format (ADF) conversion.

    This widget automatically converts ADF JSON to Markdown and renders it with formatting.
    It is read-only and displays rich text content with proper rendering (bold, italics, links, etc.).

    Features:
    - Automatic ADF to Markdown conversion on initialization
    - Rich text rendering (not editable plain text)
    - Read-only display
    - Compact field layout

    Usage in UPDATE mode:
        widget = ADFTextAreaWidget(
            mode=FieldMode.UPDATE,
            field_id="customfield_10745",
            title="HL Solution",
            original_value={'type': 'doc', 'content': [...]},  # ADF dict
        )
    """

    def __init__(
        self,
        mode: FieldMode,
        field_id: str,
        title: str | None = None,
        required: bool = False,
        # UPDATE mode parameters
        original_value: dict | str | None = None,
        field_supports_update: bool = True,
    ):
        """
        Initialize an ADFTextAreaWidget.

        Args:
            mode: The field mode (CREATE or UPDATE)
            field_id: Field identifier (e.g., 'customfield_10745')
            title: Display title for the field
            required: Whether the field is required
            original_value: Original value from Jira - can be ADF dict, string, or None
            field_supports_update: Whether field can be updated (ignored - always read-only)
        """
        # Convert ADF to Markdown if needed
        markdown_text = self._convert_to_markdown(original_value)

        # Initialize Markdown widget with converted text
        super().__init__(
            markdown=markdown_text,
            id=field_id,
        )

        # Setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            title=title or 'Text Area',
            required=required,
            compact=True,
        )

        # Add CSS class for styling
        self.add_class('adf-textarea-readonly')

    def _convert_to_markdown(self, value: dict | str | None) -> str:
        """
        Convert ADF (Atlassian Document Format) to Markdown.

        Args:
            value: The value to convert - can be ADF dict, string, or None

        Returns:
            Markdown string representation
        """
        if value is None:
            return '_No content_'

        # If it's already a string, return it
        if isinstance(value, str):
            return value if value.strip() else '_No content_'

        # If it's a dict (ADF format), convert to markdown
        if isinstance(value, dict):
            try:
                from jiratui.utils.adf2md.adf2md import adf2md

                markdown = adf2md(value)
                return markdown if markdown.strip() else '_No content_'
            except Exception as e:
                # Fallback to string representation if conversion fails
                logger.warning(f'Failed to convert ADF to markdown: {e}')
                return str(value)

        # Fallback for any other type
        return str(value)
