from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ItemGrid, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Label, MarkdownViewer, Static, TextArea

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.utils.mentions import build_mention_token
from jiratui.utils.text import char_at_location_matches
from jiratui.utils.ui_actions import Actionable, UIAction
from jiratui.widgets.commons import FieldMode
from jiratui.widgets.commons.adf import ADFMarkdownTextAreaWidget
from jiratui.widgets.commons.users import JiraUserInput, UserMentionAutoComplete
from jiratui.widgets.commons.widgets import PlainTextTextAreaWidget, UserMentionOverlay


class EditTextContentScreen(Actionable, Screen[dict]):
    """A modal screen that displays a TextArea editor to allow users to edit Plain Text/Markdown content."""

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.SAVE_CONTENT,
        SupportedActions.OPEN_USER_MENTION_PICKER,
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

    BINDINGS = [  # type:ignore[assignment]
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ] + [Binding('escape', 'app.pop_screen', 'Close')]

    def __init__(
        self, jira_field_key: str, title: str | None = None, raw_content: str | dict | None = None
    ):
        super().__init__()
        self.__raw_content: str | dict | None = raw_content
        self.__jira_field_key = jira_field_key
        self.title = title or ''
        # used for user mentions in textarea widgets
        self._mention_overlay_open: bool = False
        self._mention_trigger_location: tuple[int, int] | None = None

    @property
    def _adf_support_enabled(self) -> bool:
        # determines if the application is connecting to a Jira API instance that supports ADF
        return self.app.config.cloud and self.app.config.jira_api_version == 3  # type:ignore[attr-defined]

    @property
    def user_mention_overlay_container(self) -> Vertical:
        return self.query_one('#user-mention-overlay-container', Vertical)

    @property
    def textarea(self) -> ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget:
        if self._adf_support_enabled:
            return self.query_one(ADFMarkdownTextAreaWidget)
        return self.query_one(PlainTextTextAreaWidget)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Vertical(
                id='user-mention-overlay-container'
            )  # a container for searching and mentioning users
            if self._adf_support_enabled:
                yield ADFMarkdownTextAreaWidget(
                    mode=FieldMode.UPDATE,
                    jira_field_key=self.__jira_field_key,
                    field_id=self.__jira_field_key,
                    title=self.title,
                    original_value=cast(dict, self.__raw_content)
                    if self.__raw_content is not None
                    else None,
                )
            else:
                yield PlainTextTextAreaWidget(
                    mode=FieldMode.UPDATE,
                    jira_field_key=self.__jira_field_key,
                    field_id=self.__jira_field_key,
                    title=self.title,
                    original_value=cast(str, self.__raw_content)
                    if self.__raw_content is not None
                    else None,
                )
            with ItemGrid(classes='edit-grid-buttons'):
                yield Button(
                    'Save',
                    variant='success',
                    id='edit-description-button-save',
                    classes='save-cancel-buttons',
                )
                yield Button(
                    'Cancel',
                    variant='error',
                    id='edit-description-button-quit',
                    classes='save-cancel-buttons',
                )
            yield Static()
        yield Footer(compact=True, show_command_palette=False)

    def on_mount(self):
        self.user_mention_overlay_container.styles.display = 'none'
        self.post_message(TextArea.Changed(self.textarea))

    def save_button(self) -> Button:
        return self.query_one('#edit-description-button-save', Button)

    @on(Button.Pressed, '#edit-description-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})

    @on(Button.Pressed, '#edit-description-button-save')
    def handle_save(self) -> None:
        self.dismiss(
            {'content': self.textarea.text.strip(), 'jira_field_key': self.__jira_field_key}
        )

    def action_save_content(self) -> None:
        self.handle_save()

    # methods to implement user mentions in textarea widgets

    @on(UserMentionOverlay.Cancelled)
    async def _on_mention_cancelled(self, message: UserMentionOverlay.Cancelled) -> None:
        message.stop()
        await self._close_mention_picker()
        if textarea := self.textarea:
            textarea.focus()

    @on(UserMentionAutoComplete.UserSelected)
    async def _on_mention_user_selected(
        self, message: UserMentionAutoComplete.UserSelected
    ) -> None:
        message.stop()
        if textarea := self.textarea:
            location = self._mention_trigger_location
            token = build_mention_token(message.display_name, message.account_id)
            if location is not None and self._char_at_is_trigger(location):
                end = (location[0], location[1] + 1)
                textarea.replace(token, location, end)
                textarea.move_cursor((location[0], location[1] + len(token)))
            else:
                textarea.insert(token)
            await self._close_mention_picker()
            textarea.focus()

    @on(ADFMarkdownTextAreaWidget.MentionRequested)
    async def _on_mention_requested(
        self, message: ADFMarkdownTextAreaWidget.MentionRequested
    ) -> None:
        message.stop()
        if self._adf_support_enabled:
            await self._open_user_mention_picker(trigger_location=message.location)

    def action_open_user_mention_picker(self) -> None:
        if self._adf_support_enabled:
            # only show the user-picker overlay when a TabPane's textarea is focused
            if (textarea := self.textarea) and textarea.has_focus:
                self.run_worker(self._open_user_mention_picker())

    async def _open_user_mention_picker(
        self, trigger_location: tuple[int, int] | None = None
    ) -> None:
        if self._mention_overlay_open:
            return
        self._mention_overlay_open = True
        self._mention_trigger_location = trigger_location
        user_input = JiraUserInput(id='mention-user-input', border_title='User')
        overlay_container = self.user_mention_overlay_container
        overlay_container.styles.display = 'block'
        await overlay_container.mount_all(
            [
                UserMentionOverlay(
                    Label('Search a user to mention. Enter selects, Esc cancels.', classes='tip'),
                    user_input,
                    id='mention-overlay',
                ),
                UserMentionAutoComplete(
                    user_input,
                    cast('JiraApp', self.app).api,  # type:ignore[name-defined] # noqa: F821
                    id='mention-autocomplete',
                    user_search_function=self._search_users_for_mention,
                ),
            ]
        )
        user_input.focus()

    async def _search_users_for_mention(self, query: str) -> APIControllerResponse:
        api = cast('JiraApp', self.app).api  # type:ignore[name-defined] # noqa: F821
        return await api.search_users(email_or_name=query)

    async def _close_mention_picker(self) -> None:
        self._mention_overlay_open = False
        self._mention_trigger_location = None
        self.user_mention_overlay_container.styles.display = 'none'
        for widget in list(self.query(UserMentionAutoComplete)):
            await widget.remove()
        for item in list(self.query(UserMentionOverlay)):
            await item.remove()

    def _char_at_is_trigger(self, location: tuple[int, int]) -> bool:
        row, column = location
        return char_at_location_matches(self.textarea, row, column, '@')


class DisplayTextContentScreen(ModalScreen):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]

    def __init__(self, content: str, title: str | None = None):
        super().__init__()
        self.__content = content
        self.title = title

    def compose(self) -> ComposeResult:
        # see https://github.com/Textualize/textual/issues/3817
        yield MarkdownViewer(self.__content)
