import datetime
from typing import cast

from rich.text import Text
from textual import log
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DataTable, Rule, Static, TabbedContent, TabPane

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraWorkItemFields
from jiratui.utils.styling import (
    get_style_for_work_item_priority,
    get_style_for_work_item_status,
    get_style_for_work_item_type,
)
from jiratui.widgets.commons import CustomFieldType
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.factory_utils import (
    FieldMetadata,
    build_read_only_rich_text_widget,
)
from jiratui.widgets.commons.widgets import ReadOnlyPlainTextTextAreaWidget


class WorkItemReadOnlyDetailsScreen(ModalScreen):
    """A modal screen that displays the details of a work item in read-only mode."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
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
            with TabbedContent(id='read-only-work-item-tabs'):
                yield TabPane('Description', id='tab-description')

    @property
    def tab_pane_description(self) -> TabPane:
        return self.query_one('#tab-description', expect_type=TabPane)

    @property
    def tabbed_content(self) -> TabbedContent:
        return self.query_one('#read-only-work-item-tabs', expect_type=TabbedContent)

    async def on_mount(self) -> None:
        if not self._work_item_key:
            return
        application = cast('JiraApp', self.app)  # type:ignore[name-defined] # noqa: F821
        response: APIControllerResponse = await application.api.get_issue(  # type:ignore[attr-defined]
            issue_id_or_key=self._work_item_key
        )
        if not response.success:
            log.error(
                f'Unable to retrieve the work item with key: {self._work_item_key}: {response.error}'
            )
            self.notify(f'Unable to retrieve the work item with key: {self._work_item_key}')
        elif response.result and (issues := response.result.issues):
            issue = issues[0]
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

            # set the content of the description tab
            widget: ReadOnlyADFMarkdownTextAreaWidget | ReadOnlyPlainTextTextAreaWidget | Static
            if issue.rich_text_value_is_empty(issue.description):
                widget = Static('There is no Description set.', classes='tip')
            else:
                widget = build_read_only_rich_text_widget(
                    jira_field_key='description',
                    field_name='Description',
                    required=False,
                    content=issue.description,
                )
            await self.tab_pane_description.mount(widget)

            # display all the editable custom fields with whose type is textarea, i.e. those that support rich text
            if issue_edit_metadata := issue.get_edit_metadata():
                tabbed = self.tabbed_content

                for field_id, field in issue_edit_metadata.items():
                    metadata = FieldMetadata(field)
                    metadata.field_id = field_id  # override with the actual field ID; to ensure we always refer to the field's id

                    if (
                        metadata.key
                        and metadata.key.lower() == JiraWorkItemFields.DESCRIPTION.value
                    ):
                        # already added above
                        continue

                    if not (schema := field.get('schema')):
                        continue

                    if schema.get('custom') == CustomFieldType.TEXTAREA.value or (
                        metadata.key
                        and metadata.key.lower() == JiraWorkItemFields.ENVIRONMENT.value
                    ):
                        field_name = metadata.name or metadata.key.replace('_', ' ').title()

                        if metadata.key.lower() == JiraWorkItemFields.ENVIRONMENT.value:
                            if issue.rich_text_value_is_empty(issue.environment):
                                widget = Static(
                                    f'There is no "{field_name}" set.',
                                    classes='tip',
                                )
                            else:
                                widget = build_read_only_rich_text_widget(
                                    jira_field_key=metadata.key,
                                    field_name=field_name,
                                    required=metadata.required,
                                    content=issue.environment,
                                )
                        else:
                            # get the value of the field
                            field_value = issue.get_custom_field_value(field_id)
                            if issue.rich_text_value_is_empty(field_value):
                                widget = Static(
                                    f'There is no "{field_name}" set.',
                                    classes='tip',
                                )
                            else:
                                widget = build_read_only_rich_text_widget(
                                    jira_field_key=metadata.key,
                                    field_name=field_name,
                                    required=metadata.required,
                                    content=field_value,
                                )

                        await tabbed.add_pane(
                            TabPane(
                                metadata.name,
                                widget,
                                id=f'tab-{field_id}',
                                classes='summary-description-container',
                            )
                        )
