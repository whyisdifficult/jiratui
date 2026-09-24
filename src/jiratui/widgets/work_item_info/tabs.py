from dataclasses import dataclass

from textual.binding import Binding
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import TabbedContent, TabPane, Tabs

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.utils.ui_actions import Actionable, UIAction
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.widgets import (
    EmptyTextAreaStaticWidget,
    ReadOnlyPlainTextTextAreaWidget,
)


class InfoTabbedContent(Actionable, TabbedContent, inherit_bindings=False):  # type:ignore[call-arg]
    """Custom TabbedContent with key bindings for editing, viewing and copying the content of the currently active
    pane/tab.

    This widget expects a single `TextAreaTabPane` as a child. The widget contains the text of a Jira's textarea
    (custom) field, e.g. the description and environment fields.
    """

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.EDIT_CONTENT,
        SupportedActions.VIEW_CONTENT,
        SupportedActions.COPY_CONTENT,
        SupportedActions.NEXT_TAB,
        SupportedActions.PREVIOUS_TAB,
    ]:
        data = key_bindings.get(supported_action_id.value, {})
        ACTIONS.append(
            UIAction(
                action=supported_action_id.value,
                keys=data.get('keys', []),
                show=data.get('show', False),
                description=data.get('description'),
                tooltip=data.get('tooltip', ''),
            )
        )

    BINDINGS = [
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ]

    class DisplayContent(Message):
        def __init__(self, content: str, title: str | None = None):
            super().__init__()
            self.content = content
            """The text content the user wants to view. If the field's value is ADF then this is the Markdown version of
            it; otherwise, this is the plain text version."""
            self.title = title

    @dataclass
    class EditContent(Message):
        """A message sent when the user wants to edit the text content of the textarea in the currently active
        TabPane."""

        jira_field_key: str
        """The key of the Jira field whose text content the user wants to edit."""
        content: str
        """The text content the user wants to edit. If the field's value is ADF then this is the Markdown version of
        it."""
        raw_content: str | dict | None = None
        """The raw content of the field. This can be either ADF or plain text."""
        title: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def action_next_tab(self) -> None:
        tabs = self.query_one(Tabs)
        if tabs.has_focus:
            tabs.action_next_tab()

    def action_previous_tab(self) -> None:
        tabs = self.query_one(Tabs)
        if tabs.has_focus:
            tabs.action_previous_tab()

    def _get_textarea_widget(
        self,
    ) -> (
        ReadOnlyADFMarkdownTextAreaWidget
        | ReadOnlyPlainTextTextAreaWidget
        | EmptyTextAreaStaticWidget
        | None
    ):
        """Tales the currently active TabPane and returns the textarea-based widget in the pane."""

        if (active_pane := self.active_pane) is None:
            return None
        try:
            return active_pane.query_one(ReadOnlyADFMarkdownTextAreaWidget)
        except NoMatches:
            try:
                return active_pane.query_one(ReadOnlyPlainTextTextAreaWidget)
            except NoMatches:
                try:
                    return active_pane.query_one(EmptyTextAreaStaticWidget)
                except NoMatches:
                    return None

    def action_edit_content(self) -> None:
        """Sends an `InfoTabbedContent.EditContent` message to the parent to edit the content of the active pane's
        widget."""

        widget: (
            ReadOnlyADFMarkdownTextAreaWidget
            | ReadOnlyPlainTextTextAreaWidget
            | EmptyTextAreaStaticWidget
            | None
        ) = self._get_textarea_widget()
        if widget is not None:
            if isinstance(widget, EmptyTextAreaStaticWidget):
                jira_field_key = widget.id
                content_to_edit = ''
                title = widget.name
                raw_content: str | dict = ''
            else:
                jira_field_key = widget.jira_field_key
                content_to_edit = widget.text_content
                title = widget.field_title
                raw_content = widget.original_value
            self.post_message(
                self.EditContent(
                    jira_field_key=jira_field_key,
                    content=content_to_edit,
                    raw_content=raw_content,
                    title=title,
                )
            )

    def action_view_content(self) -> None:
        """Sends an `InfoTabbedContent.DisplayContent` message to the parent to view the content of the active
        pane's widget."""

        widget: (
            ReadOnlyADFMarkdownTextAreaWidget
            | ReadOnlyPlainTextTextAreaWidget
            | EmptyTextAreaStaticWidget
            | None
        ) = self._get_textarea_widget()
        if widget is not None:
            if isinstance(widget, EmptyTextAreaStaticWidget):
                key = self.key_bindings.get(SupportedActions.EDIT_CONTENT.value).get('keys', [])[0]
                self.notify(f'The field {widget.name} has no content. Press "{key}" to edit it.')
            else:
                self.post_message(self.DisplayContent(widget.text_content, widget.field_title))

    def action_copy_content(self) -> None:
        """Copy to the clipboard the content of the field."""

        widget: (
            ReadOnlyADFMarkdownTextAreaWidget
            | ReadOnlyPlainTextTextAreaWidget
            | EmptyTextAreaStaticWidget
            | None
        ) = self._get_textarea_widget()
        if widget is not None:
            if isinstance(widget, EmptyTextAreaStaticWidget):
                key = self.key_bindings.get(SupportedActions.EDIT_CONTENT.value).get('keys', [])[0]
                self.notify(f'The field {widget.name} has no content. Press "{key}" to edit it.')
            else:
                self.app.copy_to_clipboard(widget.text_content.strip())
                self.notify('Content copied!')


class TextAreaTabPane(TabPane):
    """A custom TabPane that contains the text content of a Jira's textarea (custom) field including the description
    and environment fields.

    This `TextAreaTabPane` widget expects 2 child widgets:

    - an optional `WebLinksCollapsible` widget that contains the links found in the text content.
    - an instance of `ReadOnlyADFMarkdownTextAreaWidget` or `ReadOnlyPlainTextTextAreaWidget` or
    `EmptyTextAreaStaticWidget` that contains the actual text content of a Jira's textarea (custom) field.
    """

    def __init__(self, title: str, widget_id: str, **kwargs):
        super().__init__(title=title, id=widget_id, **kwargs)
