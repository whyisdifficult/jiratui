from dataclasses import dataclass
from typing import cast

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Link, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.models import JiraIssue, RelatedJiraIssue
from jiratui.utils.styling import get_style_for_work_item_priority
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.confirmation_screen import ConfirmationScreen
from jiratui.widgets.messages import SearchWorkItem
from jiratui.widgets.related_work_items.add import AddWorkItemRelationshipScreen
from jiratui.widgets.screens.goto import GotToScreen
from jiratui.widgets.screens.work_item_quick_view import WorkItemQuickViewScreen


@dataclass
class WorkItemRelatedItems:
    work_item_key: str
    related_items: list[RelatedJiraIssue] | None = None


class RelatedIssueCollapsible(Collapsible):
    """A collapsible to show a work item related to another item.

    This widget is responsible for:

    - opening a modal screen to view the details of the currently-selected work item.
    - (optionally) posting a [SearchWorkItem](#jiratui.widgets.messages.SearchWorkItem) message to load the work item
    being displayed after the quick view screen is dismissed.
    - opening a [ConfirmationScreen](#jiratui.widgets.confirmation_screen.ConfirmationScreen) to confirm deleting the
    currently selected work item.
    - posting a [LinkDeleted](#jiratui.widgets.related_work_items.related_issues.RelatedIssueCollapsible.LinkDeleted)
    message to refresh the list of related work items after deleting one.

    **See Also**:
    - [Use Case: Relate Work Items](#use-case-relate-work-items)
    - [Architecture](#architecture-related-work-items-classes)
    """

    BINDINGS = [
        Binding(
            key='v',
            action='view_work_item',
            description='Quick View',
            show=True,
            key_display='v',
        ),
        Binding(
            key='d',
            action='unlink_work_item',
            description='Unlink',
            key_display='d',
        ),
        Binding(
            key='f6',
            action='open_go_to_screen',
            description='Related',
            show=True,
            key_display='f6',
            tooltip='View related work items',
        ),
    ]
    NOTIFICATIONS_DEFAULT_TITLE = 'Related Work Items'

    @dataclass
    class LinkDeleted(Message):
        """The message posted when the user deletes a link."""

        link_id: str

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)
        self._link_id: str | None = kwargs.pop('link_id', None)
        super().__init__(*args, **kwargs)

    @property
    def work_item_key(self) -> str | None:
        return self._work_item_key

    async def action_view_work_item(self) -> None:
        if self.work_item_key:
            await self.app.push_screen(
                WorkItemQuickViewScreen(self.work_item_key),
                callback=self._load_work_item_after_viewing,
            )

    def _load_work_item_after_viewing(self, work_item_key: str | None = None) -> None:
        if work_item_key:
            self.post_message(SearchWorkItem(work_item_key))

    async def action_unlink_work_item(self) -> None:
        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the link between the issues?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        if result:
            self.run_worker(self.delete_link())

    async def delete_link(self) -> None:
        """Removes a link between two work items.

        After removing a link this method will post the
        message [LinkDeleted](#jiratui.widgets.related_work_items.related_issues.RelatedIssueCollapsible.LinkDeleted)
        to update the list of related issues in the parent widget.

        Returns:
            None
        """

        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.delete_issue_link(self._link_id)
        if not response.success:
            self.notify(
                f'Failed to delete the link: {response.error}',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            self.notify(
                'Link between work items deleted successfully',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
            self.post_message(self.LinkDeleted(self._link_id))

    async def action_open_go_to_screen(self) -> None:
        """Opens a modal screen to show the work items related to the work item selected by the user.

        The screen will be opened only if `config.enable_goto == True` and there is a work item selected.

        Returns:
            None
        """

        if CONFIGURATION.get().enable_goto and self.work_item_key:
            self.app.push_screen(
                GotToScreen(self.work_item_key, self.app.api),
                callback=self._close_goto_screen,
            )
        elif not self.work_item_key:
            self.notify('Select/Highlight an item to view its related items')
        else:
            self.notify('This feature is disabled. Check config.enable_goto', severity='warning')

    def _close_goto_screen(self, work_item_key: str) -> None:
        # sends a message to request the handler, the Main Screen, to search for the work item with the given key
        if work_item_key:
            self.post_message(SearchWorkItem(work_item_key))


class RelatedIssuesWidget(VerticalScroll):
    """A container for displaying the work items related to a work item.

    This widget is responsible for:
    - opening a modal screen [AddWorkItemRelationshipScreen](#jiratui.widgets.related_work_items.add.AddWorkItemRelationshipScreen)
    to allow the user linking 2 work items.
    - making a request to the Jira API to link 2 work items.
    - refreshing the list of issues related to the current issue after receiving the
    message [LinkDeleted](#jiratui.widgets.related_work_items.related_issues.RelatedIssueCollapsible.LinkDeleted).

    **See Also**:
    - [Use Case: Relate Work Items](#use-case-relate-work-items)
    - [Architecture](#architecture-related-work-items-classes)
    """

    HELP = 'See Related Work Items section in the help'
    BINDINGS = [
        Binding(
            key='n',
            action='link_work_item',
            description='New Related',
            key_display='n',
        )
    ]

    issues: Reactive[WorkItemRelatedItems | None] = reactive(None)
    NOTIFICATIONS_DEFAULT_TITLE = 'Related Work Items'

    def __init__(self):
        super().__init__(id='related_issues')
        self._issue_key: str | None = None

    @property
    def help_anchor(self) -> str:
        return '#related-work-items'

    def add_relationship(self, data: dict | None = None) -> None:
        if data:
            self.run_worker(self.link_work_items(data))

    async def action_link_work_item(self) -> None:
        """Opens a screen to adda link between two work items."""

        if self._issue_key:
            await self.app.push_screen(
                AddWorkItemRelationshipScreen(self._issue_key), callback=self.add_relationship
            )
        else:
            self.notify(
                'Select a work item before attempting to link work items.',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )

    async def link_work_items(self, data: dict) -> None:
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.link_work_items(
            left_issue_key=self._issue_key,
            right_issue_key=data.get('right_issue_key'),
            link_type=data.get('link_type'),
            link_type_id=data.get('link_type_id'),
        )
        if not response.success:
            self.notify(
                f'Failed to link the work items: {response.error}',
                severity='error',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )
        else:
            self.notify('Work items linked successfully', title=self.NOTIFICATIONS_DEFAULT_TITLE)
            # fetch the issue but only the issue-links field
            response = await application.api.get_issue(self._issue_key, fields=['issuelinks'])
            if response.success and response.result and response.result.issues:
                work_item: JiraIssue = response.result.issues[0]
                self.issues = WorkItemRelatedItems(
                    work_item_key=self._issue_key,
                    related_items=work_item.related_issues or [],
                )

    def watch_issues(self, data: WorkItemRelatedItems | None) -> None:
        """Updates the list of work items related to the currently-selected item.

        Args:
            data: an instance of [WorkItemRelatedItems](#) with the work items related to the currently-selected work
            item.

        Returns:
            None
        """

        self.remove_children()

        if data is None:
            return

        self._issue_key = data.work_item_key

        rows: list[RelatedIssueCollapsible] = []
        issue: RelatedJiraIssue

        for issue in data.related_items or []:
            children: list[Widget] = [Static(Text(issue.cleaned_summary()))]

            if browsable_url := build_external_url_for_issue(issue.key):
                children.append(
                    Link(
                        browsable_url, url=browsable_url, tooltip='open link in the default browser'
                    )
                )

            collapsible = RelatedIssueCollapsible(
                *children,
                title=Text(f'{issue.link_type} | {issue.key} | {issue.display_status()}'),
                work_item_key=issue.key,
                link_id=issue.id,
            )
            if issue.priority_name:
                collapsible.border_subtitle = f'Priority: {issue.priority_name}'

                if collapsible_color := get_style_for_work_item_priority(issue.priority_name):
                    collapsible.styles.border = ('round', collapsible_color)

            rows.append(collapsible)
        self.mount_all(rows)

    @on(RelatedIssueCollapsible.LinkDeleted)
    def _refresh_issues_after_delete(self, event: RelatedIssueCollapsible.LinkDeleted) -> None:
        related_items: list[RelatedJiraIssue] = []
        if self.issues is not None:
            for item in self.issues.related_items or []:
                if item.id != event.link_id:
                    related_items.append(item)
            self.issues = WorkItemRelatedItems(
                work_item_key=self._issue_key, related_items=related_items
            )
