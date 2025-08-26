from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import Collapsible, Link, Markdown, Rule, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import IssueComment
from jiratui.utils.adf2md.adf2md import adf2md
from jiratui.utils.urls import build_external_url_for_comment
from jiratui.widgets.comments.add import AddCommentScreen
from jiratui.widgets.confirmation_screen import ConfirmationScreen


class CommentCollapsible(Collapsible):
    BINDINGS = [
        Binding(
            key='d',
            action='delete_comment',
            description='Delete Comment',
            key_display='d',
        ),
    ]

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)
        self._comment_id: str | None = kwargs.pop('comment_id', None)
        super().__init__(*args, **kwargs)

    async def action_delete_comment(self) -> None:
        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the comment?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        if result is True:
            self.run_worker(self.delete_comment(self._work_item_key, self._comment_id))

    def _update_comments_after_delete(self) -> None:
        updated_comments: list[IssueComment] = []
        for comment in self.parent.comments:  # type:ignore[attr-defined]
            if comment.id == self._comment_id:
                continue
            updated_comments.append(comment)
        self.parent.comments = updated_comments  # type:ignore[attr-defined]

    async def delete_comment(self, work_item_key: str, comment_id: str) -> None:
        """Deletes a comment associated to the selected work item and retrieves the list comments if the comment is
        deleted successfully.

        Args:
            work_item_key: the key of the work item whose comment we want to remove.
            comment_id: the ID of the comment we want to remove.

        Returns:
            `None`
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.delete_comment(
            work_item_key, comment_id
        )
        if not response.success:
            self.notify(
                f'Failed to delete the comment: {response.error}',
                severity='error',
                title='Comments',
            )
        else:
            self.notify('Comment deleted successfully', title='Comments')
            if CONFIGURATION.get().fetch_comments_on_delete:
                response = await application.api.get_comments(work_item_key)
                if not response.success or not (result := response.result):
                    # fallback to removing the comment manually
                    self._update_comments_after_delete()
                else:
                    self.parent.comments = result  # type:ignore[attr-defined]
            else:
                # fallback to removing the comment manually
                self._update_comments_after_delete()


class IssueCommentsWidget(VerticalScroll):
    HELP = """
# Comments

This contains the comments associated to the selected work item. Comments can be deleted by focusing on them and then
pressing `d`. Comments can be added by pressing `n`.
    """
    comments: Reactive[list[IssueComment] | None] = reactive(None)

    BINDINGS = [
        Binding(
            key='n',
            action='add_comment',
            description='Add Comment',
            key_display='n',
        )
    ]

    def __init__(self):
        super().__init__(id='issue_comments')
        self._issue_key = None

    @property
    def issue_key(self):
        return self._issue_key

    @issue_key.setter
    def issue_key(self, value: str | None):
        self._issue_key = value

    def save_comment(self, content: str) -> None:
        self.run_worker(self.add_comment_to_issue(content))

    def action_add_comment(self) -> None:
        """Opens a screen to add a comment to the issue."""
        if self.issue_key:
            self.app.push_screen(AddCommentScreen(self.issue_key), self.save_comment)
        else:
            self.notify('Select a work item before attempting to add a comment.', title='Comments')

    async def add_comment_to_issue(self, content: str) -> None:
        """Adds a comment to the issue and retrieves the list comments if the comment was added successfully.

        Args:
            content: the message of the comment.

        Return:
            `None`
        """
        if message := content.strip():
            application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
            response: APIControllerResponse = await application.api.add_comment(
                self.issue_key, message
            )
            if not response.success:
                self.notify(
                    f'Failed to add the comment: {response.error}',
                    severity='error',
                    title='Comments',
                )
            else:
                self.notify('Comment added successfully', title='Comments')
                response = await application.api.get_comments(self.issue_key)
                if response.success:
                    self.comments = response.result or []

    def watch_comments(self, items: list[IssueComment]) -> None:
        self.remove_children()
        if not items:
            return
        comment: IssueComment
        elements: list[CommentCollapsible] = []
        items.sort(key=lambda x: x.updated, reverse=True)
        for comment in items:
            try:
                comment_text = adf2md(comment.body_as_dict())
            except Exception:
                comment_text = 'Unable to display the comment. Open the link above to view it.'

            url = (
                build_external_url_for_comment(self.issue_key, comment.id) if self.issue_key else ''
            )

            elements.append(
                CommentCollapsible(
                    Link('Open link', url=url, tooltip='view comment in the browser'),
                    Static(f'Last update: {comment.updated_on()}'),
                    Rule(),
                    Markdown(comment_text),
                    title=Text(comment.short_metadata()),
                    work_item_key=self.issue_key,
                    comment_id=comment.id,
                )
            )
        self.mount_all(elements)
