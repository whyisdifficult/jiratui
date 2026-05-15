from textual.binding import Binding
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static, TabbedContent, TabPane

from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.widgets import ReadOnlyPlainTextTextAreaWidget


class InfoTabbedContent(TabbedContent):
    """Custom TabbedContent with key bindings for editing, viewing and copying the content of the currently active
    pane/tab."""

    BINDINGS = [
        Binding(
            key='ctrl+e', action='edit_content', description='Edit', show=True, key_display='^e'
        ),
        Binding(key='v', action='view_content', description='View', key_display='v'),
        Binding(key='c', action='copy_content', description='Copy', key_display='c'),
    ]

    class DisplayContent(Message):
        def __init__(self, content: str, title: str | None = None):
            super().__init__()
            self.content = content
            self.title = title

    class EditContent(Message):
        def __init__(
            self, jira_field_key: str, content: str | None = None, title: str | None = None
        ):
            super().__init__()
            self.content = content or ''
            self.jira_field_key = jira_field_key
            self.title = title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_textarea_widget(
        self,
    ) -> ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget | Static | None:
        if (active_pane := self.active_pane) is None:
            return None
        try:
            return active_pane.query_one(ReadOnlyADFMarkdownTextAreaWidget)
        except NoMatches:
            try:
                return active_pane.query_one(ReadOnlyPlainTextTextAreaWidget)
            except NoMatches:
                try:
                    return active_pane.query_one(Static)
                except NoMatches:
                    return None

    def action_edit_content(self) -> None:
        """Sends an `InfoTabbedContent.EditContent` message to the parent to edit the content of the active pane's
        widget."""

        widget: (
            ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget | Static | None
        ) = self._get_textarea_widget()
        if widget is not None:
            if isinstance(widget, Static):
                content_to_edit = ''
                jira_field_key = widget.id
                title = widget.name
            else:
                content_to_edit = widget.text_content
                jira_field_key = widget.jira_field_key
                title = widget.field_title
            self.post_message(self.EditContent(jira_field_key, content_to_edit, title))

    def action_view_content(self) -> None:
        """Sends an `InfoTabbedContent.DisplayContent` message to the parent to view the content of the active
        pane's widget."""

        widget: (
            ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget | Static | None
        ) = self._get_textarea_widget()
        if widget is not None:
            if isinstance(widget, Static):
                self.notify(f'The field {widget.name} has no content. Press "^e" to edit it.')
            else:
                self.post_message(self.DisplayContent(widget.text_content, widget.field_title))

    def action_copy_content(self) -> None:
        """Copy to the clipboard the content of the field."""

        widget: (
            ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget | Static | None
        ) = self._get_textarea_widget()
        if widget is not None:
            if isinstance(widget, Static):
                self.notify(f'The field {widget.name} has no content. Press "^e" to edit it.')
            else:
                self.app.copy_to_clipboard(widget.text_content.strip())
                self.notify('Content copied!')


class TextAreaTabPane(TabPane):
    """A custom TabPane that contains either ReadOnlyADFMarkdownTextAreaWidget or ReadOnlyPlainTextTextAreaWidget as
    its child."""

    def __init__(self, title: str, widget_id: str, **kwargs):
        super().__init__(title=title, id=widget_id, **kwargs)
