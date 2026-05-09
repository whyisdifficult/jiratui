"""ADF TextArea Widget - Handles Atlassian Document Format conversion and rendering."""

import logging

from textual.widgets import Markdown

from jiratui.utils.adf import convert_adf_to_markdown
from jiratui.widgets.commons.base import (
    BaseFieldWidget,
    FieldMode,
)

logger = logging.getLogger(__name__)


class ADFTextAreaWidget(Markdown, BaseFieldWidget):
    """Read-only Markdown widget that handles Atlassian Document Format (ADF) conversion.

    This widget automatically converts ADF JSON to Markdown and renders it with formatting.
    It is read-only and displays rich text content with proper rendering (bold, italics, links, etc.).

    Features:
    - Automatic ADF to Markdown conversion on initialization
    - Rich text rendering (not editable plain text)
    - Read-only display
    - Compact field layout

    Usage in UPDATE mode:

    ```python
    widget = ADFTextAreaWidget(
        mode=FieldMode.UPDATE,
        field_id='customfield_10745',
        jira_field_key='customfield_10745',
        title='HL Solution',
        original_value={'type': 'doc', 'content': [...]},  # ADF dict
    )
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
        original_value: dict | None = None,
    ):
        """Initializes an ADFTextAreaWidget.

        Args:
            mode: the field mode (CREATE or UPDATE)
            field_id: field identifier, e.g., 'customfield_10745'.
            jira_field_key: the key of the field that it is used for updating the field value in the API; e.g., 'customfield_10745'
            title: display title for the field.
            required: whether the field is required.
            original_value: the original value from Jira. It expects an ADF dict.
        """

        # the Markdown text that we want to display; convert ADF to Markdown if needed
        self.__markdown_text = self._convert_to_markdown(original_value)

        # initialize Markdown widget with converted text
        super().__init__(markdown=self.__markdown_text, id=field_id)

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title or jira_field_key.replace('_', ' ').title(),
            required=required,
            compact=True,
        )

        # add CSS class for styling
        self.add_class('adf-textarea-readonly')

    @staticmethod
    def _convert_to_markdown(value: dict | str | None) -> str:
        """Converts ADF (Atlassian Document Format) to Markdown.

        Args:
            value: the value to convert - can be ADF dict, string, or None

        Returns:
            Markdown string representation
        """

        if value is None:
            return ''

        # if it's already a string, return it
        if isinstance(value, str):
            return value if value.strip() else ''

        # if it's a dict (ADF format), convert to Markdown
        if isinstance(value, dict):
            try:
                markdown = convert_adf_to_markdown(value)
                return markdown if markdown.strip() else ''
            except Exception as e:
                # Fallback to string representation if conversion fails
                logger.warning(f'Failed to convert ADF to markdown: {e}')
                return str(value)

        # fallback for any other type
        return str(value)

    @property
    def text_content(self) -> str:
        return self.__markdown_text
