import datetime

from rich.text import Text
from textual import log
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DataTable, Rule

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssueSearchResponse
from jiratui.utils.styling import (
    get_style_for_work_item_priority,
    get_style_for_work_item_status,
    get_style_for_work_item_type,
)
from jiratui.widgets.summary import IssueDescriptionWidget


class WorkItemReadOnlyDetailsScreen(ModalScreen):
    """A modal screen that displays the details of a work item in read-only mode."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]
    TITLE = 'Work Item Details'

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key

    def compose(self) -> ComposeResult:
        vertical = VerticalScroll()
        vertical.border_title = self.TITLE
        with vertical:
            yield DataTable(
                cursor_type='row', show_header=False, id='work-item-readonly-details-dt'
            )
            yield Rule()
            yield IssueDescriptionWidget()

    @property
    def issue_description_widget(self) -> IssueDescriptionWidget:
        return self.query_one(IssueDescriptionWidget)

    async def on_mount(self) -> None:
        if not self._work_item_key:
            return
        response: APIControllerResponse = await self.parent.api.get_issue(  # type:ignore[attr-defined]
            issue_id_or_key=self._work_item_key
        )
        if not response.success:
            log.error(
                f'Unable to retrieve the work item with key: {self._work_item_key}: {response.error}'
            )
            self.notify(f'Unable to retrieve the work item with key: {self._work_item_key}')
        elif response.result:
            result: JiraIssueSearchResponse = response.result
            if result.issues:
                issue = result.issues[0]
                color_style_priority = get_style_for_work_item_priority(issue.priority_name)
                color_style_status = get_style_for_work_item_status(issue.status.name)
                color_style_type = get_style_for_work_item_type(issue.issue_type.name)
                table = self.query_one(DataTable)
                table.add_columns(*['Property', 'Value'])
                table.add_rows(
                    [
                        (
                            Text('Key', justify='right'),
                            Text(issue.key, justify='left'),
                        ),
                        (
                            Text('Parent', justify='right'),
                            Text(issue.parent_key or '-', justify='left'),
                        ),
                        (
                            Text('Summary', justify='right'),
                            Text(issue.cleaned_summary(), justify='left'),
                        ),
                        (
                            Text('Assignee', justify='right'),
                            Text(issue.assignee_display_name, justify='left'),
                        ),
                        (
                            Text('Reporter', justify='right'),
                            Text(issue.reporter_display_name, justify='left'),
                        ),
                        (
                            Text('Status', justify='right'),
                            Text(issue.status.name, justify='left', style=color_style_status),
                        ),
                        (
                            Text('Project', justify='right'),
                            Text(str(issue.project), justify='left'),
                        ),
                        (
                            Text('Issue Type', justify='right'),
                            Text(issue.issue_type.name, justify='left', style=color_style_type),
                        ),
                        (
                            Text('Priority', justify='right'),
                            Text(issue.priority_name, justify='left', style=color_style_priority),
                        ),
                        (
                            Text('Created', justify='right'),
                            Text(
                                datetime.datetime.strftime(issue.created, '%Y-%m-%d %H:%M'),
                                justify='left',
                            ),
                        ),
                        (
                            Text('Last Update', justify='right'),
                            Text(
                                datetime.datetime.strftime(issue.updated, '%Y-%m-%d %H:%M'),
                                justify='left',
                            ),
                        ),
                        (
                            Text('Resolution', justify='right'),
                            Text(issue.resolution or '', justify='left'),
                        ),
                        (
                            Text('Resolved', justify='right'),
                            Text(issue.resolved_on, justify='left'),
                        ),
                    ]
                )

                if issue.description:
                    if content := issue.get_description():
                        await self.issue_description_widget.update(content)
                    else:
                        log.error(
                            f'Failed to parse the description for work item with key: {self._work_item_key}'
                        )
                        await self.issue_description_widget.update(
                            'Unable to display the description.'
                        )
                else:
                    await self.issue_description_widget.update('')
