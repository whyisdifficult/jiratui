from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import Collapsible, Link, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import IssueRemoteLink
from jiratui.widgets.confirmation_screen import ConfirmationScreen
from jiratui.widgets.remote_links.add import AddRemoteLinkScreen


class IssueRemoteLinkCollapsible(Collapsible):
    """A collapsible to show a remote link associated to a work item.

    The widget posts the message `jiratui.widgets.remote_links.links.IssueRemoteLinkCollapsible.Deleted` when a link
    is deleted.
    """

    BINDINGS = [
        Binding(
            key='d',
            action='delete_remote_link',
            description='Delete Link',
            key_display='d',
        )
    ]
    NOTIFICATIONS_DEFAULT_TITLE = 'Remote Links'

    class Deleted(Message):
        """Posted when a link is deleted.

        It holds the key of the work item whose link we deleted and the ID of the deleted link.
        """

        def __init__(self, work_item_key: str, link_id: str) -> None:
            self.work_item_key = work_item_key
            self.link_id = link_id
            super().__init__()

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)
        self._link_id: str | None = kwargs.pop('link_id', None)
        super().__init__(*args, **kwargs)

    async def action_delete_remote_link(self) -> None:
        """Opens a modal screen to ask the user if they want to delete a remote link or not.

        Returns:
            None
        """

        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the link?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        if result:
            self.post_message(self.Deleted(self._work_item_key, self._link_id))


class IssueRemoteLinksWidget(VerticalScroll):
    """A container for adding and updating the list of remote links (aka. web links) associated to a work item.

    This widget is responsible for the following:

    - opening the modal screen that allows users to add new links.
    - fetching the list of remote links associated to the work item.
    - adding a new link to the work item.
    - deleting a link when the message `jiratui.widgets.remote_links.links.IssueRemoteLinkCollapsible.Deleted` is posted
    """

    HELP = 'See Web Links section in the help'
    BINDINGS = [
        Binding(
            key='n',
            action='add_remote_link',
            description='New Link',
            key_display='n',
        )
    ]

    # we need to use always_active to support updates after deleting
    issue_key: Reactive[str | None] = reactive(None, always_update=True)
    NOTIFICATIONS_DEFAULT_TITLE = 'Remote Links'

    def __init__(self):
        super().__init__(id='issue_remote_links')

    @property
    def help_anchor(self) -> str:
        return '#web-links'

    def on_issue_remote_link_collapsible_deleted(
        self, message: IssueRemoteLinkCollapsible.Deleted
    ) -> None:
        """Schedules a task to delete a link."""

        self.run_worker(self._delete_link(message.work_item_key, message.link_id))
        message.stop()  # no need to propagate the message

    async def _delete_link(self, work_item_key: str, link_id: str) -> None:
        """Removes a remote link associated to a work item.

        Returns:
            None
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.delete_issue_remote_link(
            work_item_key, link_id
        )
        if not response.success:
            self.notify(
                f'Failed to delete the link: {response.error}',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            self.issue_key = work_item_key

    async def action_add_remote_link(self) -> None:
        """Handles the event to open a pop-up screen to add a remote (web) link to a work item.

        Returns:
            None.
        """

        if self.issue_key:
            await self.app.push_screen(AddRemoteLinkScreen(self.issue_key), callback=self.add_link)
        else:
            self.notify(
                'Select a work item before attempting to add a link.',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
                severity='warning',
            )

    def add_link(self, data: dict | None = None) -> None:
        """Processes the callback form the modal screen and adds the link to the work item.

        Args:
            data: the data related to the link we need to add.

        Returns:
            None
        """

        if data:
            self.run_worker(self.create_link(data))

    async def create_link(self, data: dict) -> None:
        """Creates the actual link for the work item and updates the list of links that are displayed for the item.

        Args:
            data: the data related to the link we need to add. Expects `link_url` and `link_title`.

        Returns:
            None
        """

        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await screen.api.create_issue_remote_link(
            self.issue_key,
            data.get('link_url'),
            data.get('link_title'),
        )
        if not response.success:
            self.notify(
                f'Failed to add link: {response.error}',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            # update the links in this widget with the new results
            self.issue_key = self.issue_key

    async def fetch_remote_links(self, issue_key: str) -> None:
        """Retrieves the remote links of a work item and displays them as a list of collapsible widgets in the screen.

        Args:
            issue_key: the case-sensitive key of the item.

        Returns:
            None
        """

        links: list[IssueRemoteLink] = []
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await screen.api.get_issue_remote_links(issue_key)
        if not response.success:
            self.notify(
                'Unable to retrieve the remote links associated to the work item.',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
                severity='warning',
            )
        else:
            links = response.result or []

        rows: list[IssueRemoteLinkCollapsible] = []

        for item in links:
            if item.status_resolved:
                status_resolved = Text('Resolved: Yes', style='green')
            elif item.status_resolved is False:
                status_resolved = Text('Resolved: No', style='red')
            else:
                status_resolved = Text('Resolved: N/A')
            title = item.title
            if item.relationship:
                title = f'{item.relationship} | {title}'
            rows.append(
                IssueRemoteLinkCollapsible(
                    Link(item.url, url=item.url, tooltip='open link in the default browser'),
                    Static(status_resolved),
                    title=Text(title),
                    work_item_key=issue_key,
                    link_id=item.id,
                )
            )

        if rows:
            await self.mount_all(rows)

    def watch_issue_key(self, issue_key: str | None = None) -> None:
        """Updates the remote links of the work item being displayed every time a new work item is set for the widget.

        Args:
            issue_key: the case-sensitive key of the item.

        Returns:
            None
        """

        self.remove_children()
        if issue_key:
            self.run_worker(self.fetch_remote_links(issue_key))
