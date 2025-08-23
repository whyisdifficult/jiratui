from typing import cast

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Collapsible, Link, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssue, RelatedJiraIssue
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.confirmation_screen import ConfirmationScreen
from jiratui.widgets.constants import RELATED_WORK_ITEMS_PRIORITY_BASED_STYLING
from jiratui.widgets.related_work_items.add import AddWorkItemRelationshipScreen
from jiratui.widgets.work_item_details.read_only_details import WorkItemReadOnlyDetailsScreen


class RelatedIssueCollapsible(Collapsible):
    HELP = """\
# Related Work Items

This will display a summary of all the work items related to the item currently selected in the Work Items panel on the
left.
    """

    BINDINGS = [
        Binding(
            key='v',
            action='view_work_item',
            description='View Work Item',
            show=True,
            key_display='v',
        ),
        Binding(
            key='d',
            action='unlink_work_item',
            description='Unlink Work Item',
            key_display='d',
        ),
    ]
    NOTIFICATIONS_DEFAULT_TITLE = 'Related Work Items'

    def __init__(self, *args, **kwargs):
        self._work_item_key: str | None = kwargs.pop('work_item_key', None)
        self._link_id: str | None = kwargs.pop('link_id', None)
        super().__init__(*args, **kwargs)

    @property
    def work_item_key(self) -> str | None:
        return self._work_item_key

    async def action_view_work_item(self) -> None:
        if self.work_item_key:
            await self.app.push_screen(WorkItemReadOnlyDetailsScreen(self.work_item_key))

    async def action_unlink_work_item(self) -> None:
        await self.app.push_screen(
            ConfirmationScreen('Are you sure you want to delete the link between the issues?'),
            callback=self.handle_delete_choice,
        )

    def handle_delete_choice(self, result: bool) -> None:
        if result is True:
            self.run_worker(self.delete_link())

    async def delete_link(self) -> None:
        """Removes a link between two work items.

        After removing a link the list of links is updated by removing the item from the list without fetching data
        from the API.

        Returns:
            Nothing
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
            self.parent.issues = [i for i in self.parent.issues or [] if i.id != self._link_id]  # type:ignore[attr-defined]


class RelatedIssuesWidget(VerticalScroll):
    """A container for displaying the work items related to a work item."""

    HELP = """\
# Related Work Items

This will display a summary of all the work items related to the item currently selected.

Pressing `n` allows the user to add new related work items while focusing on a related item and then pressing `d` will
delete the item.

To view the details of a related item simply focus on the item and then press `v`.
    """

    BINDINGS = [
        Binding(
            key='n',
            action='link_work_item',
            description='Link Work Item',
            key_display='n',
        )
    ]

    issues: Reactive[list[RelatedJiraIssue] | None] = reactive(None)
    NOTIFICATIONS_DEFAULT_TITLE = 'Related Work Items'

    def __init__(self):
        super().__init__(id='related_issues')
        self._issue_key: str | None = None

    @property
    def issue_key(self) -> str | None:
        return self._issue_key

    @issue_key.setter
    def issue_key(self, value: str | None) -> None:
        self._issue_key = value

    def add_relationship(self, data: dict | None = None) -> None:
        if data:
            self.run_worker(self.link_work_items(data))

    async def action_link_work_item(self) -> None:
        """Opens a screen to adda link between two work items."""

        if self.issue_key:
            await self.app.push_screen(
                AddWorkItemRelationshipScreen(self.issue_key), callback=self.add_relationship
            )
        else:
            self.notify(
                'Select a work item before attempting to add a link.',
                title=self.NOTIFICATIONS_DEFAULT_TITLE,
            )

    async def link_work_items(self, data: dict) -> None:
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.link_work_items(
            left_issue_key=self.issue_key,
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
            response = await application.api.get_issue(self.issue_key, fields=['issuelinks'])
            if response.success and response.result and response.result.issues:
                work_item: JiraIssue = response.result.issues[0]
                self.issues = work_item.related_issues or []

    def watch_issues(self, items: list[RelatedJiraIssue] | None) -> None:
        self.remove_children()

        if not items:
            return

        rows: list[RelatedIssueCollapsible] = []
        issue: RelatedJiraIssue
        for issue in items:
            styles: dict | None = RELATED_WORK_ITEMS_PRIORITY_BASED_STYLING.get(
                issue.priority_name.lower(), {}
            )

            children: list[Widget] = [
                Static(Text(issue.cleaned_summary())),
            ]

            if browsable_url := build_external_url_for_issue(issue.key):
                children.append(
                    Link(
                        browsable_url, url=browsable_url, tooltip='open link in the default browser'
                    )
                )

            children.append(
                Static(
                    Text(
                        f'{issue.priority_name} priority',
                        style=styles.get('text_style', '') if styles else '',
                    ),
                    classes='related-work-item-priority',
                ),
            )
            collapsible = RelatedIssueCollapsible(
                *children,
                title=Text(f'{issue.link_type} | {issue.key} | {issue.display_status()}'),
                work_item_key=issue.key,
                link_id=issue.id,
            )
            if styles and (collapsible_class := styles.get('collapsible_class')):
                collapsible.add_class(collapsible_class)
            rows.append(collapsible)
        self.mount_all(rows)
