from dataclasses import dataclass
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, TextArea

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.utils.mentions import build_mention_token
from jiratui.utils.text import char_at_location_matches
from jiratui.utils.ui_actions import Actionable, UIAction
from jiratui.widgets.commons.adf import ADFMarkdownTextAreaWidget
from jiratui.widgets.commons.base import FieldMode
from jiratui.widgets.commons.users import JiraUserInput, UserMentionAutoComplete
from jiratui.widgets.commons.widgets import PlainTextTextAreaWidget, UserMentionOverlay


@dataclass
class CommentScreenResult:
    """Contains the data for the caller when the screen is dismissed."""

    content: str
    """The content of the comment that we want to add or update. This is always a string."""
    work_item_key: str | None = None
    """The key of the work item whose comment the user wants to delete."""
    comment_id: str | None = None
    """The ID of the comment the user wants to delete."""


class AddCommentScreen(Actionable, Screen[CommentScreenResult | None]):
    """A modal screen that allows users to add/update work item's comments.

    The screen does not add/update the comment to the work item. Instead, it returns the comment's text to the caller
    via the `dismiss()` call and the caller will proceed to add/update the comment via the API.

    The screen also provides an `@` mention picker: typing `@` at a word boundary (or the `ctrl+@` binding) opens a
    small overlay that live-searches Jira users and inserts a mention *token* (`@[Name](accountId)`) at the
    cursor. Tokens are expanded to ADF `Mention` nodes on submit
    by [expand_mention_tokens](#jiratui.utils.mentions.expand_mention_tokens); see
    [proposals/0001](https://github.com/whyisdifficult/jiratui/issues/125).

    **See Also**:
    - [Add Comment Screen Design](#components-add-comment-screen)
    - [Use Case: Add Comment](#use-case-add-comment)
    - [Use Case: Update Comment](#use-case-update-comment)
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

    def __init__(
        self,
        work_item_key: str | None = None,
        update_mode: bool = False,
        comment_id: str | None = None,
        content: str | dict | None = None,
    ):
        """Creates the modal screen.

        Args:
            work_item_key: the key of the work item for which the user is adding or updating a comment.
            update_mode: if `True` then the user wants to update an existing comment; otherwise the user is adding a new
            comment.
            content: the initial content of the comment if update_mode is `True`. When `update_mode=True` this will
            contain the current content of the comment. The type of content varies depending on whether the Jira server
            supports ADF or not.
        """

        super().__init__()
        self.__work_item_key = work_item_key
        self.__update_mode = update_mode
        self.__comment_id = comment_id
        self.__initial_content: str | dict | None = content
        if self.__update_mode:
            self.title = f'Update Comment for {self.__work_item_key}'
        else:
            self.title = f'Add Comment for {self.__work_item_key}'
        self._mention_overlay_open: bool = False
        self._mention_trigger_location: tuple[int, int] | None = None

    @property
    def comment_textarea(self) -> ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget:
        if self._adf_support_enabled:
            return self.query_one(ADFMarkdownTextAreaWidget)
        else:
            return self.query_one(PlainTextTextAreaWidget)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-comment-button-save', expect_type=Button)

    @property
    def overlay_container(self) -> Vertical:
        return self.query_one('#user-mention-overlay-container', Vertical)

    def compose(self) -> ComposeResult:
        widget: ADFMarkdownTextAreaWidget | PlainTextTextAreaWidget
        with Vertical(id='add-comment-screen-vertical') as vc:
            vc.border_title = self.title
            if self._adf_support_enabled:
                widget = ADFMarkdownTextAreaWidget(
                    mode=FieldMode.CREATE if not self.__update_mode else FieldMode.UPDATE,
                    jira_field_key='comment',
                    field_id='comment',
                    title='Comment',
                    original_value=self.__initial_content if self.__update_mode else None,  # type:ignore[arg-type]
                )
            else:
                widget = PlainTextTextAreaWidget(
                    mode=FieldMode.CREATE if not self.__update_mode else FieldMode.UPDATE,
                    jira_field_key='comment',
                    field_id='comment',
                    title='Comment',
                    original_value=self.__initial_content if self.__update_mode else None,  # type:ignore[arg-type]
                )
            widget.compact = True
            yield widget
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
        self.dismiss(
            CommentScreenResult(
                work_item_key=self.__work_item_key,
                comment_id=self.__comment_id,
                content=self.comment_textarea.text.strip() or '',
            )
        )

    @on(Button.Pressed, '#add-comment-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss(None)

    # logic related to user mentions in textarea widgets
    @property
    def _adf_support_enabled(self) -> bool:
        return self.app.config.cloud and self.app.config.jira_api_version == 3  # type:ignore[attr-defined]

    @on(UserMentionOverlay.Cancelled)
    async def _on_mention_cancelled(self, message: UserMentionOverlay.Cancelled) -> None:
        message.stop()
        await self._close_mention_picker()
        self.comment_textarea.focus()

    @on(UserMentionAutoComplete.UserSelected)
    async def _on_mention_user_selected(
        self, message: UserMentionAutoComplete.UserSelected
    ) -> None:
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

    @on(ADFMarkdownTextAreaWidget.MentionRequested)
    async def _on_mention_requested(
        self, message: ADFMarkdownTextAreaWidget.MentionRequested
    ) -> None:
        message.stop()
        if self._adf_support_enabled:
            await self._open_user_mention_picker(trigger_location=message.location)

    def action_open_user_mention_picker(self) -> None:
        if self._adf_support_enabled:
            self.run_worker(self._open_user_mention_picker())

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
        if self._mention_overlay_open:
            return
        self._mention_overlay_open = True
        self._mention_trigger_location = trigger_location
        user_input = JiraUserInput(id='mention-user-input', border_title='User')
        overlay_container = self.overlay_container
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

    async def _close_mention_picker(self) -> None:
        self._mention_overlay_open = False
        self._mention_trigger_location = None
        self.overlay_container.styles.display = 'none'
        for widget in list(self.query(UserMentionAutoComplete)):
            await widget.remove()
        for item in list(self.query(UserMentionOverlay)):
            await item.remove()

    def _char_at_is_trigger(self, location: tuple[int, int]) -> bool:
        row, column = location
        return char_at_location_matches(self.comment_textarea, row, column, '@')
