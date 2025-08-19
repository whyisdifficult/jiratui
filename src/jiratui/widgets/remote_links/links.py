from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import Collapsible, Link, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import IssueRemoteLink
from jiratui.widgets.confirmation_screen import ConfirmationScreen
from jiratui.widgets.remote_links.add import AddRemoteLinkScreen


class IssueRemoteLinkCollapsible(Collapsible):
    BINDINGS = [
        Binding(
            key='d',
            action='delete_remote_link',
            description='Delete Link',
            key_display='d',
        )
    ]
    NOTIFICATIONS_DEFAULT_TITLE = 'Remote Links'

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)
        self._link_id: str | None = kwargs.pop('link_id', None)
        super().__init__(*args, **kwargs)

    async def action_delete_remote_link(self) -> None:
        """Opens a moda screen to ask the user if they want to delete a remote link or not.

        Returns:
            Nothing.
        """
        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the link?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        """Schedules the operation to delete a link when a user accepts deleting a link.

        Args:
            result: the decision of the user. `True` means: "delete the link".

        Returns:
            Nothing.
        """
        if result is True:
            self.run_worker(self.delete_link())

    async def delete_link(self) -> None:
        """Removes a remote link associated to a work item.

        Returns:
            Nothing
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.delete_issue_remote_link(
            self._work_item_key, self._link_id
        )
        if not response.success:
            self.notify(
                f'Failed to delete the link: {response.error}',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            self.notify('Link deleted successfully', title=self.NOTIFICATIONS_DEFAULT_TITLE)
            self.parent.issue_key = self._work_item_key  # type:ignore[attr-defined]


class IssueRemoteLinksWidget(VerticalScroll):
    """This widget handles adding and updating the list of remote links (aka. web links) associated to a work item."""

    HELP = """\
# Web Links (aka. Remote Links)

This will display a list of URLs associated to the selected work item. files attached to the selected work item.

To add a new link simply press `n` and provide the details in the pop-up that opens.

To delete a link simply focus on the title of the collapsible whose link you want to delete and then press `d`.
    """

    BINDINGS = [
        Binding(
            key='n',
            action='add_remote_link',
            description='Add Link',
            key_display='n',
        )
    ]

    # we need to use always_active to support updates after deleting
    issue_key: Reactive[str | None] = reactive(None, always_update=True)
    NOTIFICATIONS_DEFAULT_TITLE = 'Remote Links'

    def __init__(self):
        super().__init__(id='issue_remote_links')

    async def action_add_remote_link(self) -> None:
        """Handles the event to open a pop-up screen to add a remote (web) link to a work item.

        Returns:
            Nothing.
        """
        if self.issue_key:
            await self.app.push_screen(AddRemoteLinkScreen(self.issue_key), callback=self.add_link)
        else:
            self.notify(
                'Select a work item before attempting to add a link.',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )

    def add_link(self, data: dict | None = None) -> None:
        """Processes the callback form the op-up screen and adds the link to the work item.

        Args:
            data: the data related to the link we need to add.

        Returns:
            Nothing.
        """
        if data:
            self.run_worker(self.create_link(data))

    async def create_link(self, data: dict) -> None:
        """Creates the actual link for the work item and updates the list of links that are displayed for the item.

        Args:
            data: the data related to the link we need to add. Expects `link_url` and `link_title`.

        Returns:
            Nothing.
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
            self.notify('Link added successfully', title=self.NOTIFICATIONS_DEFAULT_TITLE)
            # update the links in this widget with the new results
            self.issue_key = self.issue_key

    async def fetch_remote_links(self, issue_key: str) -> None:
        """Retrieves the remote links of a work item and displays them as a list of collapsible widgets in the screen.

        Args:
            issue_key: the case-sensitive key of the item.

        Returns:
            Nothing.
        """
        links: list[IssueRemoteLink] = []
        screen = cast('MainScreen', self.screen)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await screen.api.get_issue_remote_links(issue_key)
        if not response.success:
            self.notify(
                'Unable to retrieve the remote links associated to the work item.',
                title='Work Items Remote Links',
                severity='warning',
            )
        else:
            links = response.result or []

        rows: list[IssueRemoteLinkCollapsible] = []

        for item in links:
            if item.status_resolved is True:
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

        await self.remove_children()
        await self.mount_all(rows)

    def watch_issue_key(self, issue_key: str | None = None) -> None:
        """Updates the remote links of the work item being displayed every time a new work item is set for the widget.

        Args:
            issue_key: the case-sensitive key of the item.

        Returns:
            Nothing.
        """
        if issue_key:
            self.run_worker(self.fetch_remote_links(issue_key))
