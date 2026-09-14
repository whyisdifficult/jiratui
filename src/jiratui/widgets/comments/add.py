"""
The screen also provides an `@` mention picker: typing `@` at a word boundary (or the `ctrl+@` binding)
opens a small overlay that live-searches Jira users and inserts a mention *token* (`@[Name](accountId)`) at
the cursor. Tokens are expanded to ADF `Mention` nodes on submit by
[expand_mention_tokens](#jiratui.utils.mentions.expand_mention_tokens);
see [proposals/0001](https://github.com/whyisdifficult/jiratui/issues/125).
"""

from typing import cast

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ItemGrid, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Label, Static, TextArea
from textual_autocomplete import TargetState

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.utils.mentions import build_mention_token
from jiratui.utils.ui_actions import Actionable, UIAction
from jiratui.widgets.commons.users import JiraUserInput, UsersAutoComplete
from jiratui.widgets.commons.widgets import TextAreaWithUserMention


class MentionAutoComplete(UsersAutoComplete):
    """A [UsersAutoComplete](#jiratui.widgets.commons.users.UsersAutoComplete) that announces the picked user.

    The base class stores the selected user's account id on the target input but does not emit a message; this
    subclass posts a [UserSelected](#jiratui.widgets.comments.add.MentionAutoComplete.UserSelected) message so
    the screen can build and insert the mention token.
    """

    class UserSelected(Message):
        """Posted when a user is chosen from the mention autocomplete dropdown."""

        def __init__(self, account_id: str, display_name: str) -> None:
            self.account_id = account_id
            self.display_name = display_name
            super().__init__()

    def apply_completion(self, value: str, state: TargetState) -> None:
        super().apply_completion(value, state)
        account_id: str | None = getattr(self.target, 'account_id', None)
        display_name = (self.target.value or '').split('|', 1)[0].strip()
        if account_id and display_name:
            self.post_message(self.UserSelected(account_id=account_id, display_name=display_name))


class MentionOverlay(Vertical):
    """The inline overlay that hosts the mention search input.

    It is an ancestor of the search `Input`, so its `escape` binding takes precedence over the screen's
    `escape` binding and cancels the picker instead of closing the whole screen.
    """

    BINDINGS = [Binding('escape', 'cancel', 'Cancel', show=False)]

    class Cancelled(Message):
        """Posted when the user cancels the mention picker."""

    def action_cancel(self) -> None:
        self.post_message(self.Cancelled())


class AddCommentScreen(Actionable, Screen[str]):
    """A modal screen that allows users to add a comment to a work item.

    The screen does not add the comment to the work item. Instead, it returns the comment's text to the caller via the
    `dismiss()` call and the caller will proceed to add the comment via the API.

    **See Also**:
    - [Add Comment Screen Design](#components-add-comment-screen)
    - [Use Case: Add Comment](#use-case-add-comment)
    - [Architecture](#architecture-work-item-comments-classes)
    """

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
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

    def __init__(self, work_item_key: str | None = None):
        super().__init__()
        self.__work_item_key = work_item_key
        self.title = f'Add comment to the work item {self.__work_item_key}'
        self._mention_overlay_open: bool = False
        self._mention_trigger_location: tuple[int, int] | None = None

    @property
    def comment_textarea(self) -> TextAreaWithUserMention:
        return self.query_one(TextAreaWithUserMention)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-comment-button-save', expect_type=Button)

    @property
    def overlay_container(self) -> Vertical:
        return self.query_one('#user-mention-overlay-container', Vertical)

    def compose(self) -> ComposeResult:
        with Vertical(id='add-comment-screen-vertical') as vc:
            vc.border_title = self.title
            yield Static(
                Text(
                    'Tip: tab works as indentation control. Use Escape or shift+tab to focus/unfocus elements in the screen.'
                ),
                classes='tip',
            )
            textarea = TextAreaWithUserMention.code_editor(
                '', language='markdown', show_line_numbers=False, compact=True
            )
            textarea.border_title = 'Comment'
            textarea.border_subtitle = 'Markdown Enabled'
            yield textarea
            yield Vertical(id='user-mention-overlay-container')
            with ItemGrid(classes='add-comment-grid-buttons'):
                yield Button('Save', variant='success', id='add-comment-button-save', disabled=True)
                yield Button('Cancel', variant='error', id='add-comment-button-quit')

    def on_mount(self) -> None:
        self.overlay_container.styles.display = 'none'

    @on(TextArea.Changed, 'TextArea')
    def validate_comment(self):
        value = self.comment_textarea.text
        self.save_button.disabled = False if (value and value.strip()) else True

    @on(Button.Pressed, '#add-comment-button-save')
    def handle_save(self) -> None:
        self.dismiss(self.comment_textarea.text.strip() or '')

    @on(Button.Pressed, '#add-comment-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss('')

    # logic related to user mentions
    @property
    def _adf_support_enabled(self) -> bool:
        return self.app.config.cloud and self.app.config.jira_api_version == 3  # type:ignore[attr-defined]

    @on(MentionOverlay.Cancelled)
    async def _on_mention_cancelled(self, message: MentionOverlay.Cancelled) -> None:
        message.stop()
        await self._close_mention_picker()
        self.comment_textarea.focus()

    @on(MentionAutoComplete.UserSelected)
    async def _on_mention_user_selected(self, message: MentionAutoComplete.UserSelected) -> None:
        message.stop()
        token = build_mention_token(message.display_name, message.account_id)
        textarea = self.comment_textarea
        location = self._mention_trigger_location
        if location is not None and self._char_at_is_trigger(location):
            end = (location[0], location[1] + 1)
            textarea.replace(token, location, end)
            textarea.move_cursor((location[0], location[1] + len(token)))
        else:
            textarea.insert(token)
        await self._close_mention_picker()
        textarea.focus()

    @on(TextAreaWithUserMention.MentionRequested)
    async def _on_mention_requested(
        self, message: TextAreaWithUserMention.MentionRequested
    ) -> None:
        message.stop()
        await self._open_user_mention_picker(trigger_location=message.location)

    def action_open_user_mention_picker(self) -> None:
        self.run_worker(self._open_user_mention_picker())

    def _user_mentions_enabled(self) -> bool:
        """Mentions are only supported on Jira Cloud with API v3 (where comments are submitted as ADF)."""
        return self._adf_support_enabled

    async def _search_users_for_mention(self, query: str) -> APIControllerResponse:
        api = cast('JiraApp', self.app).api  # type:ignore[name-defined] # noqa: F821
        if self.__work_item_key:
            return await api.search_users_assignable_to_issue(
                issue_key=self.__work_item_key, query=query
            )
        return await api.search_users(email_or_name=query)

    async def _open_user_mention_picker(
        self, trigger_location: tuple[int, int] | None = None
    ) -> None:
        if self._mention_overlay_open or not self._user_mentions_enabled():
            return
        self._mention_overlay_open = True
        self._mention_trigger_location = trigger_location
        user_input = JiraUserInput(id='mention-user-input', border_title='User')
        overlay_container = self.overlay_container
        overlay_container.styles.display = 'block'
        await overlay_container.mount_all(
            [
                MentionOverlay(
                    Label('Search a user to mention. Enter selects, Esc cancels.', classes='tip'),
                    user_input,
                    id='mention-overlay',
                ),
                MentionAutoComplete(
                    user_input,
                    cast('JiraApp', self.app).api,  # type:ignore[name-defined] # noqa: F821
                    id='mention-autocomplete',
                    user_search_function=self._search_users_for_mention,
                ),
            ]
        )
        user_input.focus()

    async def _close_mention_picker(self) -> None:
        self._mention_overlay_open = False
        self._mention_trigger_location = None
        self.overlay_container.styles.display = 'none'
        for selector in ('#mention-autocomplete', '#mention-overlay'):
            for widget in list(self.query(selector)):
                await widget.remove()

    def _char_at_is_trigger(self, location: tuple[int, int]) -> bool:
        row, column = location
        try:
            return self.comment_textarea.document[row][column] == '@'
        except IndexError:
            return False
