from dataclasses import dataclass
from datetime import datetime
from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import Collapsible, Link, Markdown, Rule, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import IssueComment
from jiratui.utils.urls import build_external_url_for_comment
from jiratui.widgets.comments.add import AddCommentScreen
from jiratui.widgets.confirmation_screen import ConfirmationScreen


@dataclass
class WorkItemComments:
    """The data for the reactive attribute that holds the comments of a work item."""

    work_item_key: str | None = None
    comments: list[IssueComment] | None = None


class CommentCollapsible(Collapsible):
    """A collapsible to show a comment associated to a work item."""

    BINDINGS = [
        Binding(
            key='d',
            action='delete_comment',
            description='Delete Comment',
            key_display='d',
        ),
    ]

    class Deleted(Message):
        """Posted when a comment is deleted.

        It holds the key of the work item whose comment we deleted and the ID of the deleted comment.
        """

        def __init__(self, work_item_key: str, comment_id: str) -> None:
            self.work_item_key = work_item_key
            self.comment_id = comment_id
            super().__init__()

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)  # type:ignore[annotation-unchecked]
        self._comment_id: str | None = kwargs.pop('comment_id', None)  # type:ignore[annotation-unchecked]
        super().__init__(*args, **kwargs)

    async def action_delete_comment(self) -> None:
        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the comment?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        if result:
            self.post_message(self.Deleted(self._work_item_key, self._comment_id))


class IssueCommentsWidget(VerticalScroll):
    """A container for displaying the comments of a work item.

    This widget is responsible for the following:

    - opening the modal screen that allows users to write comments.
    - processing the result from the modal screen and adding the comment to the work item via the API.
    - deleting comments from the work item via the API when the message
    `jiratui.widgets.comments.comments.CommentCollapsible.Deleted` is posted.
    - updating the list of comments when a comment is deleted.
    """

    HELP = 'See Comments section in the help'
    comments: Reactive[WorkItemComments | None] = reactive(None)

    BINDINGS = [
        Binding(
            key='n',
            action='add_comment',
            description='New Comment',
            key_display='n',
        )
    ]

    def __init__(self):
        super().__init__(id='issue_comments')
        self._work_item_key = None

    @property
    def help_anchor(self) -> str:
        return '#comments'

    def _update_comments_after_delete(self, comment_id: str) -> None:
        self.comments = WorkItemComments(
            work_item_key=self._work_item_key,
            comments=[
                comment for comment in self.comments.comments or [] if comment.id != comment_id
            ],  # type:ignore[attr-defined]
        )

    def on_comment_collapsible_deleted(self, message: CommentCollapsible.Deleted) -> None:
        """Schedules a task to delete a comment."""
        self.run_worker(self._delete_comment(message.work_item_key, message.comment_id))
        message.stop()  # no need to propagate the message

    @staticmethod
    def _fetch_comments_on_delete() -> bool:
        return CONFIGURATION.get().fetch_comments_on_delete

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
        """Opens a screen to capture the comment's text."""
        if self._work_item_key:
            self.app.push_screen(AddCommentScreen(self._work_item_key), self._save_comment)
        else:
            self.notify('Select a work item before attempting to add a comment.', title='Comments')

    def _save_comment(self, content: str) -> None:
        if content and content.strip():
            self.run_worker(self._add_comment_to_issue(content))

    async def _add_comment_to_issue(self, content: str) -> None:
        """Adds a comment to the issue and retrieves the list comments if the comment was added successfully.

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
        if data and data.comments:
            comment: IssueComment
            elements: list[CommentCollapsible] = []
            data.comments.sort(
                key=lambda x: x.updated if x.updated else datetime.today().date(), reverse=True
            )
            comment_text: Markdown | Static
            for comment in data.comments:
                if content := comment.get_body():
                    comment_text = Markdown(content)
                else:
                    comment_text = Static(
                        Text(
                            'Unable to display the comment. Open the link above to view it.',
                            style='bold orange',
                        )
                    )

                url = (
                    build_external_url_for_comment(self._work_item_key, comment.id)
                    if self._work_item_key
                    else ''
                )

                hg = HorizontalGroup()
                hg.compose_add_child(
                    Link('Open Link', url=url, tooltip='view comment in the browser')
                )
                hg.compose_add_child(Static(f' | Last Update: {comment.updated_on()}'))

                elements.append(
                    CommentCollapsible(
                        hg,
                        Rule(classes='rule-horizontal-compact-70'),
                        comment_text,
                        title=Text(comment.short_metadata()),
                        work_item_key=self._work_item_key,
                        comment_id=comment.id,
                    )
                )
            self.mount_all(elements)
