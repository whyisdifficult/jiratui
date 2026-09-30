"""Widgets for listing the comments associated to a work item."""

from dataclasses import dataclass
from datetime import datetime
from typing import cast

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import Collapsible, Link, Rule, Static

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import IssueComment
from jiratui.utils.ui_actions import Actionable, UIAction
from jiratui.utils.urls import build_external_url_for_comment
from jiratui.widgets.comments.add import AddCommentScreen, CommentScreenResult
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.factory_utils import build_read_only_rich_text_widget
from jiratui.widgets.commons.widgets import (
    ReadOnlyPlainTextTextAreaWidget,
    WebLinksCollapsible,
    WebLinksDataTable,
)
from jiratui.widgets.screens.confirmation import ConfirmationScreen


@dataclass
class WorkItemComments:
    """The data for the reactive attribute that holds the comments of a work item."""

    work_item_key: str | None = None
    comments: list[IssueComment] | None = None


class CommentCollapsible(Actionable, Collapsible, inherit_bindings=False):  # type:ignore[call-arg]
    """A collapsible to show a comment associated to a work item.

    **See Also**:
    - [Use Case: Delete Comment](#use-case-delete-comment)
    - [Use Case: Update Comment](#use-case-update-comment)
    """

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.DELETE_COMMENT,
        SupportedActions.EDIT_COMMENT,
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

    @dataclass
    class Deleted(Message):
        """Posted when the user wants to delete a comment."""

        work_item_key: str
        """The key of the work item whose comment the user wants to delete."""
        comment_id: str
        """The ID of the comment the user wants to delete."""

    @dataclass
    class EditComment(Message):
        """Posted when the user wants to edit the comment's content."""

        work_item_key: str
        """The key of the work item whose comment the user wants to update."""
        comment_id: str
        """The ID of the comment the user wants to update."""

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)  # type:ignore[annotation-unchecked]
        self._comment_id: str | None = kwargs.pop('comment_id', None)  # type:ignore[annotation-unchecked]
        super().__init__(*args, **kwargs)

    def action_edit_comment(self) -> None:
        """Posts an `EditComment` message to request updating the comment's content."""

        if self._work_item_key and self._comment_id:
            self.post_message(self.EditComment(self._work_item_key, self._comment_id))

    async def action_delete_comment(self) -> None:
        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the comment?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        """Posts a `CommentCollapsible.Deleted` to delete a comment.

        Args:
            result: if True then the message to delete the comment is posted. Otherwise, nothing is done.
        """

        if result and self._work_item_key and self._comment_id:
            self.post_message(self.Deleted(self._work_item_key, self._comment_id))


class IssueCommentsWidget(Actionable, VerticalScroll, inherit_bindings=False):  # type:ignore[call-arg]
    """A container for displaying the comments of a work item.

    This widget is responsible for the following:

    - opening the modal screen that allows users to write comments.
    - processing the result from the modal screen and adding the comment to the work item via the API.
    - deleting comments from the work item via the API when the message `CommentCollapsible.Deleted` is posted.
    - updating a comment from the work item via the API when the message `CommentCollapsible.EditComment` is posted.
    - updating the list of comments when a comment is deleted.

    **See Also**:
    - [Use Case: Add Comment](#use-case-add-comment)
    - [Use Case: Update Comment](#use-case-update-comment)
    - [Use Case: Delete Comment](#use-case-delete-comment)
    - [Architecture](#architecture-work-item-comments-classes)
    """

    HELP = 'See Comments section in the help'
    comments: Reactive[WorkItemComments | None] = reactive(None)

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.ADD_COMMENT,
        SupportedActions.PAGE_UP,
        SupportedActions.PAGE_DOWN,
        SupportedActions.SCROLL_HOME,
        SupportedActions.SCROLL_END,
        SupportedActions.SCROLL_UP,
        SupportedActions.SCROLL_DOWN,
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

    def __init__(self):
        super().__init__(id='issue_comments')
        self._work_item_key = None
        self.__comments_contents_by_id: dict[str, str | dict | None] = {}

    @property
    def help_anchor(self) -> str:
        return '#comments'

    def _update_comments_after_delete(self, comment_id: str) -> None:
        if self.comments and self.comments.comments:
            self.comments = WorkItemComments(
                work_item_key=self._work_item_key,
                comments=[
                    comment for comment in self.comments.comments or [] if comment.id != comment_id
                ],  # type:ignore[attr-defined]
            )

    def on_comment_collapsible_deleted(self, message: CommentCollapsible.Deleted) -> None:
        """Schedules a task to delete a comment.

        Args:
            message: the [CommentCollapsible.Deleted](#jiratui.widgets.comments.comments.CommentCollapsible.Deleted)
            message containing the id of the comment to be deleted.

        Returns:
            None
        """

        message.stop()  # no need to propagate the message
        self.run_worker(self._delete_comment(message.work_item_key, message.comment_id))

    @on(CommentCollapsible.EditComment)
    def open_edit_comment_screen(self, message: CommentCollapsible.EditComment) -> None:
        """Opens a modal screen to allow users to update the comment's content.

        Args:
            message: the message posted by the collapsible widget that holds the comment's content.

        Returns:
            None
        """

        message.stop()
        if message.work_item_key and message.comment_id:
            self.app.push_screen(
                AddCommentScreen(
                    message.work_item_key,
                    update_mode=True,
                    comment_id=message.comment_id,
                    content=self.__comments_contents_by_id.get(message.comment_id),
                ),
                self._edit_comment,
            )
        else:
            self.notify(
                'Select a work item before attempting to edit one of its comments.',
                title='No item selected',
                severity='warning',
            )

    async def _edit_comment(self, data: CommentScreenResult | None) -> None:
        if data and data.content and data.work_item_key and data.comment_id:
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            # update the comment
            response: APIControllerResponse = await application.api.update_comment(
                data.work_item_key,
                data.comment_id,
                data.content,
            )
            if not response.success:
                self.notify(
                    f'Failed to add the comment: {response.error}',
                    severity='error',
                    title='Comments',
                )
            else:
                # refresh the comments
                response = await application.api.get_comments(self._work_item_key)
                if response.success:
                    self.comments = WorkItemComments(
                        work_item_key=self._work_item_key, comments=response.result or []
                    )

    def _fetch_comments_on_delete(self) -> bool:
        return self.app.config.fetch_comments_on_delete  # type:ignore[attr-defined]

    async def _delete_comment(self, key: str, comment_id: str) -> None:
        """Attempts to delete a comment."""

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.delete_comment(key, comment_id)
        if response.success:
            if self._fetch_comments_on_delete():
                response = await application.api.get_comments(self._work_item_key)
                if response.success:
                    self.comments = WorkItemComments(
                        work_item_key=self._work_item_key, comments=response.result
                    )  # type:ignore[attr-defined]
                else:
                    # fallback to removing the comment manually
                    self._update_comments_after_delete(comment_id)
            else:
                # fallback to removing the comment manually
                self._update_comments_after_delete(comment_id)
        else:
            self.notify(
                f'Failed to delete the comment: {response.error}',
                severity='error',
                title='Comments',
            )

    def action_add_comment(self) -> None:
        """Opens a modal screen to allow users to add a comment for the currently selected work item."""

        if self._work_item_key:
            self.app.push_screen(AddCommentScreen(self._work_item_key), self._save_comment)
        else:
            self.notify(
                'Select a work item before attempting to add a comment.',
                title='No item selected',
                severity='warning',
            )

    def _save_comment(self, data: CommentScreenResult | None) -> None:
        if data and data.content and data.content.strip():
            self.run_worker(self._add_comment_to_issue(data.content))

    async def _add_comment_to_issue(self, content: str) -> None:
        """Adds a comment to the work item and refresh the list comments if the comment was added successfully.

        Args:
            content: the message of the comment.

        Return:
            None.
        """

        if message := content.strip():
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            response: APIControllerResponse = await application.api.add_comment(
                self._work_item_key, message
            )
            if not response.success:
                self.notify(
                    f'Failed to add the comment: {response.error}',
                    severity='error',
                    title='Comments',
                )
            else:
                self.notify('Comment added successfully', title='Comments')
                # refresh the comments
                response = await application.api.get_comments(self._work_item_key)
                if response.success:
                    self.comments = WorkItemComments(
                        work_item_key=self._work_item_key, comments=response.result or []
                    )

    def watch_comments(self, data: WorkItemComments | None) -> None:
        self.remove_children()
        self._work_item_key = data.work_item_key if data else None
        if data and (comments_list := data.comments):
            comment: IssueComment
            elements: list[CommentCollapsible] = []
            comments_list.sort(
                key=lambda x: x.updated if x.updated else datetime.today().date(), reverse=True
            )
            widget: ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget | Static
            for comment in comments_list:
                web_links: list[Link] = []
                if comment.rich_text_value_is_empty(comment.body):  # type:ignore[arg-type]
                    widget = Static('There is no "Comment" set.', classes='tip')
                    self.__comments_contents_by_id[comment.id] = None
                else:
                    widget = build_read_only_rich_text_widget(
                        jira_field_key='comment',
                        field_name='comment',
                        required=False,
                        content=comment.body,
                    )
                    self.__comments_contents_by_id[comment.id] = comment.body
                    web_links = widget.extract_web_links()

                url = (
                    build_external_url_for_comment(self._work_item_key, comment.id)
                    if self._work_item_key
                    else ''
                )

                hg = HorizontalGroup()
                hg.compose_add_child(
                    Link('Open in Browser', url=url, tooltip='view comment in the browser')
                )
                hg.compose_add_child(Static(f' | Last Update: {comment.updated_on()}'))

                collapsible_child_widgets: list[
                    ReadOnlyADFMarkdownTextAreaWidget
                    | ReadOnlyPlainTextTextAreaWidget
                    | Static
                    | WebLinksCollapsible
                ] = [widget]
                if web_links:
                    collapsible_child_widgets = [
                        WebLinksCollapsible(WebLinksDataTable(web_links))
                    ] + collapsible_child_widgets

                elements.append(
                    CommentCollapsible(
                        hg,
                        Rule(classes='rule-horizontal-compact-70'),
                        *collapsible_child_widgets,
                        title=Text(comment.short_metadata()),
                        work_item_key=self._work_item_key,
                        comment_id=comment.id,
                    )
                )
            self.mount_all(elements)
