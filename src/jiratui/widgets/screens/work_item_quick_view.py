import datetime
from typing import cast

from rich.text import Text
from textual import log, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Rule, Static, TabbedContent, TabPane

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraWorkItemFields
from jiratui.utils.styling import (
    get_style_for_work_item_priority,
    get_style_for_work_item_status,
    get_style_for_work_item_type,
)
from jiratui.utils.urls import build_external_url_for_issue
from jiratui.widgets.commons import CustomFieldType
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.factory_utils import (
    FieldMetadata,
    build_read_only_rich_text_widget,
)
from jiratui.widgets.commons.widgets import ReadOnlyPlainTextTextAreaWidget


class QuickViewDetails(DataTable):
    """A [DataTable](textual.widgets.DataTable) that displays the details of a work item being displayed on the quick
    view screen.

    This table is responsible for:
    - posting the message [WorkItemSelected](#jiratui.widgets.screens.work_item_quick_view.QuickViewDetails.WorkItemSelected)
    when the user selects a data row that contains a work item key; e.g. the key or parent key rows.
    """

    class WorkItemSelected(Message):
        def __init__(self, work_item_key: str):
            super().__init__()
            self.work_item_key = work_item_key

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Posts the message
        [WorkItemSelected](#jiratui.widgets.screens.work_item_quick_view.QuickViewDetails.WorkItemSelected) to ask the
        caller to search and load the work item displayed in the row.

        Args:
            event: the event that triggered this.
        """

        if event.row_key and event.row_key.value:
            if key := event.row_key.value.split('#')[-1]:
                self.post_message(self.WorkItemSelected(key))


class WorkItemQuickViewScreen(ModalScreen[str]):
    """A modal screen that displays the details of a work item in read-only mode.

    This screen can be dismissed with an optional string. The string represents the key of a work item that we want to
    fetch and display in the main screen. By default, the string is the key of the work item being displayed by this
    screen. This allows users to quickly jump to the work item being displayed.

    In future versions users may be able to dismiss this screen with the key of the parent of the work item being
    displayed; assuming the work item has a parent.

    The screen also supports the following features:

    - Opening the work item in the browser.
    - Copying to the clipboard the work item's key.
    - Copying to the clipboard the work item's URL.

    **See Also**
    - [Architecture](#architecture-work-item-subtasks-classes)
    """

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Close'),
        Binding(
            key='ctrl+o',
            action='open_issue_in_browser',
            description='Browse',
            show=True,
            key_display='^o',
            tooltip='Open in browser',
        ),
        Binding(
            key='ctrl+k',
            action='copy_issue_key',
            description='Copy Key',
            show=True,
            key_display='^k',
            tooltip='Copy key',
        ),
        Binding(
            key='ctrl+j',
            action='copy_issue_url',
            description='Copy URL',
            show=True,
            key_display='^j',
            tooltip='Copy URL',
        ),
        Binding(
            key='ctrl+r',
            action='search_work_item',
            description='Search Work Item',
            show=True,
            key_display='^r',
            tooltip='Search and Fetch Work Item',
        ),
    ]
    TITLE = 'Work Item Details'

    def __init__(self, work_item_key: str):
        super().__init__()
        self._work_item_key = work_item_key

    def compose(self) -> ComposeResult:
        vertical = VerticalScroll()
        vertical.border_title = f'{self.TITLE} - {self._work_item_key}'
        with vertical:
            yield QuickViewDetails(
                cursor_type='row', show_header=False, id='work-item-readonly-details-dt'
            )
            yield Rule()
            with TabbedContent(id='read-only-work-item-tabs'):
                yield TabPane('Description', id='tab-description')
        yield Footer(show_command_palette=False, compact=True)

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

            table = self.query_one(QuickViewDetails)
            table.add_columns(*['Property', 'Value'])
            table.add_row(
                *[Text('Key', justify='right'), Text(issue.key, justify='left')],
                key=f'key#{issue.key}',
            )
            table.add_row(
                *[Text('Parent', justify='right'), Text(issue.parent_key or '-', justify='left')],
                key=f'key#{issue.parent_key}' if issue.parent_key else None,
            )
            table.add_rows(
                [
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
                            datetime.datetime.strftime(issue.created, '%Y-%m-%d %H:%M')
                            if issue.created
                            else '',
                            justify='left',
                        ),
                    ),
                    (
                        Text('Last Update', justify='right'),
                        Text(
                            datetime.datetime.strftime(issue.updated, '%Y-%m-%d %H:%M')
                            if issue.updated
                            else '',
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

    def action_open_issue_in_browser(self) -> None:
        """Opens the currently-selected item in the default browser."""
        if self._work_item_key:
            self.notify('Opening Work Item in the browser...')
            self.app.open_url(build_external_url_for_issue(self._work_item_key))

    def action_copy_issue_key(self) -> None:
        """Copy to the clipboard the key of the item."""
        if self._work_item_key:
            self.app.copy_to_clipboard(self._work_item_key)
            self.notify('Work item Key copied!')

    def action_copy_issue_url(self) -> None:
        """Copy to the clipboard the URL of the item."""
        if self._work_item_key:
            if url := build_external_url_for_issue(self._work_item_key):
                self.app.copy_to_clipboard(url)
                self.notify('Work item URL copied!')

    def action_search_work_item(self) -> None:
        """Dismisses the screen with the key of the work item being displayed."""
        if self._work_item_key:
            self.dismiss(self._work_item_key)
        else:
            self.dismiss()

    @on(QuickViewDetails.WorkItemSelected)
    def _dismiss_with_work_item_key(self, message: QuickViewDetails.WorkItemSelected) -> None:
        message.stop()  # no need to propagate the message
        self.dismiss(message.work_item_key)
