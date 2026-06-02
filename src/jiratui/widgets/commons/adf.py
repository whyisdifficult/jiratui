"""ADF TextArea Widget - Handles Atlassian Document Format conversion and rendering."""

from dataclasses import dataclass
import hashlib
import logging

from textual.binding import Binding
from textual.message import Message
from textual.widgets import Markdown, TextArea

from jiratui.utils.adf import convert_adf_to_markdown, convert_markdown_to_adf
from jiratui.widgets.commons import BaseFieldWidget, BaseUpdateFieldWidget, FieldMode

logger = logging.getLogger(__name__)


class ReadOnlyADFMarkdownTextAreaWidget(Markdown):
    """Read-only Markdown widget that handles [Atlassian Document Format (ADF)](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
    conversion.

    This widget automatically converts ADF JSON to Markdown and renders it with formatting.
    It is read-only and displays rich text content with proper rendering (bold, italics, links, etc.).

    The widget can be used when we want to display fields that support ADF. Jira Cloud Platform API v3 uses such
    fields.

    Use it in the Info tab or to display comment's content or to display fields in the read-only work item details
    screen.

    **Features**:
    - Automatic ADF to Markdown conversion on initialization
    - Rich text rendering (not editable Markdown)
    - Read-only display

    **Usage**:

    ```python
    widget = ReadOnlyADFTextAreaWidget(
        field_id='customfield_10745',
        jira_field_key='customfield_10745',
        title='HL Solution',
        required=True,
        original_value={'type': 'doc', 'content': [...]},  # ADF dict
    )
    ```
    """

    def __init__(
        self,
        field_id: str,
        jira_field_key: str,
        title: str | None = None,
        required: bool = False,
        original_value: dict | None = None,
    ):
        """Initializes a [ReadOnlyADFMarkdownTextAreaWidget](#jiratui.widgets.commons.adf.ReadOnlyADFMarkdownTextAreaWidget).

        Args:
            field_id: field identifier, e.g., 'customfield_10745'.
            jira_field_key: the key of the field that it is used for updating the field value in the API; e.g.,
            'customfield_10745'.
            title: display title for the field.
            required: whether the field is required.
            original_value: the original value from Jira. It expects an ADF dict.
        """

        # the Markdown text that we want to display; convert ADF to Markdown if needed
        self.__markdown_text = self._convert_to_markdown(original_value)

        # initialize Markdown widget with converted text
        super().__init__(markdown=self.__markdown_text, id=field_id)

        self.field_id = field_id
        self._jira_field_key = jira_field_key
        self.border_title = title or jira_field_key.replace('_', ' ').title()
        self._required = required
        self.__title = title or jira_field_key.replace('_', ' ').title()

        if self._required:
            self.border_subtitle = '(*)'
            if hasattr(self, 'add_class'):
                self.add_class('required')

        # add CSS class for styling
        self.add_class('adf-textarea-readonly')

    @property
    def required(self) -> bool:
        """Checks if this field is required."""

        return self._required

    def mark_required(self) -> None:
        """Marks this field as required by adding subtitle and CSS class."""

        self._required = True
        self.border_subtitle = '(*)'
        self.add_class('required')

    @property
    def jira_field_key(self) -> str | None:
        return self._jira_field_key

    @staticmethod
    def _convert_to_markdown(value: dict | None) -> str:
        """Converts ADF (Atlassian Document Format) to Markdown.

        Args:
            value: the value to convert - expects an ADF dict.

        Returns:
            Markdown string representation.
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
        """Retrieves the Markdown representation of this ADF value being displayed in this widget."""
        return self.__markdown_text

    @property
    def field_title(self) -> str:
        return self.__title


class ADFMarkdownTextAreaWidget(TextArea, BaseFieldWidget, BaseUpdateFieldWidget):
    """Unified Markdown-based textarea widget for fields that support ADF and that supports CREATE and UPDATE modes.

    **Features**:

    - Multi-line text input for fields with textarea custom type.
    - ADF-to-Markdown and Markdown-toADF conversion.
    - Mode-aware behavior (CREATE vs UPDATE)
    - Change tracking for UPDATE mode
    - Required field support

    **Usage in CREATE mode**:

    ```python
    widget = ADFMarkdownTextAreaWidget(
        mode=FieldMode.CREATE,
        jira_field_key='customfield_12345',
        field_id='customfield_12345',
        title='Description',
        required=False,
    )
    # Get value:
    widget.text
    ```

    **Usage in UPDATE mode**:

    ```python
    widget = ADFMarkdownTextAreaWidget(
        mode=FieldMode.UPDATE,
        jira_field_key='customfield_12345',
        field_id='customfield_12345',
        title='Custom Field A',
        original_value='Original text',
        field_supports_update=True,
    )
    # Check changes:
    widget.value_has_changed
    # Get value for API updates:
    widget.get_value_for_update()
    # Get value for API creation operations:
    widget.get_value_for_create()
    ```
    """

    BINDINGS = [
        Binding('ctrl+e', 'edit_content', 'Edit', show=True, key_display='^e'),
    ]

    @dataclass
    class EditContent(Message):
        """A message sent when the content of the field is edited."""

        content: str

    def __init__(
        self,
        mode: FieldMode,
        jira_field_key: str,
        field_id: str,
        title: str | None = None,
        required: bool = False,
        # UPDATE mode parameters
        original_value: dict | None = None,
        field_supports_update: bool = True,
    ):
        """Initializes a [ADFMarkdownTextAreaWidget](#jiratui.widgets.commons.adf.ADFMarkdownTextAreaWidget).

        Args:
            mode: the field mode (CREATE or UPDATE)
            jira_field_key: the key of the field that it is used for updating the field value in the API.
            field_id: field identifier.
            title: display title.
            required: whether the field is required (mainly for CREATE mode)
            original_value: original ADF value from Jira (UPDATE mode only)
            field_supports_update: whether field can be updated (UPDATE mode only)
        """

        markdown = ''
        if original_value is not None:
            if not isinstance(original_value, dict):
                raise ValueError('original_value must be a dict')

            try:
                markdown = convert_adf_to_markdown(original_value)
            except Exception:
                # fallback to string representation. Not ideal but we need to show this to the user.
                markdown = str(original_value)

        # initialize TextArea
        super().__init__(text=markdown, id=field_id, language='markdown', tab_behavior='indent')

        # setup base field properties
        self.setup_base_field(
            mode=mode,
            field_id=field_id,
            jira_field_key=jira_field_key,
            title=title or jira_field_key.replace('_', ' ').title(),
            required=required,
            compact=True,
        )

        # mode-specific setup
        if mode == FieldMode.UPDATE:
            self.setup_update_field(
                jira_field_key=jira_field_key,
                original_value=original_value,
                field_supports_update=field_supports_update,
            )
        self.add_class('create-work-item-description')

    def action_edit_content(self):
        self.post_message(self.EditContent(content=self.text))

    def get_value_for_update(self) -> dict | None:
        """Returns the value formatted for Jira API updates (UPDATE mode).

        Returns:
            An ADF dict or None if the MD-to-ADF conversion fails.
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('get_value_for_update() only valid in UPDATE mode')

        text = self.text.strip() if self.text else ''
        try:
            return convert_markdown_to_adf(text)
        except Exception:
            # fallback to a single paragraph
            return {
                'content': [
                    {
                        'content': [
                            {
                                'type': 'text',
                                'text': text,
                            }
                        ],
                        'type': 'paragraph',
                    }
                ],
                'type': 'doc',
                'version': 1,
            }

    def get_value_for_create(self) -> dict | None:
        """Returns the value formatted for Jira API creation (CREATE mode).

        Returns:
            An ADF dict or None if the MD-to-ADF conversion fails.
        """
        if self.mode != FieldMode.CREATE:
            raise ValueError('get_value_for_create() only valid in CREATE mode')

        text = self.text.strip() if self.text else ''
        try:
            return convert_markdown_to_adf(text)
        except Exception:
            # fallback to a single paragraph
            return {
                'content': [
                    {
                        'content': [
                            {
                                'type': 'text',
                                'text': text,
                            }
                        ],
                        'type': 'paragraph',
                    }
                ],
                'type': 'doc',
                'version': 1,
            }

    @property
    def original_value(self) -> dict:
        """Get the original description from Jira."""
        return self._original_value

    @property
    def value_has_changed(self) -> bool:
        """Determines if the current value differs from the original value (UPDATE mode).

        The current value is a Markdown text but the original value is an ADF dict. We need to convert the ADF to
        Markdown and compare the strings.

        Returns:
            True if value has changed, False otherwise.
        """

        if self.mode != FieldMode.UPDATE:
            raise ValueError('value_has_changed only valid in UPDATE mode')

        original_as_markdown: str | None = None
        if self.original_value is not None:
            original_as_markdown = convert_adf_to_markdown(self.original_value)

        current = self.text.strip() if self.text else ''

        # empty to empty - no change
        if not original_as_markdown and not current:
            return False

        # empty to value or value to empty - changed
        if not original_as_markdown or not current:
            return True

        # both exist - compare them
        hash1 = hashlib.sha256(original_as_markdown.encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(current.encode('utf-8')).hexdigest()
        return hash1 != hash2

    def set_original_value(self, value: dict) -> None:
        """Sets the original value for change tracking (UPDATE mode).

        Args:
            value: The original description text from Jira
        """
        if self.mode != FieldMode.UPDATE:
            raise ValueError('set_original_value() only valid in UPDATE mode')

        self._original_value = value

    @property
    def value_is_empty(self) -> bool:
        text = self.text.strip() if self.text else ''
        return False if text else True
