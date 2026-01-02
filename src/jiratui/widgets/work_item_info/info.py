from atlas_doc_parser.api import parse_node
from textual.app import ComposeResult
from textual.containers import Container, Vertical, VerticalGroup, VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import Markdown

from jiratui.models import CustomFieldTypes, JiraIssue
from jiratui.widgets.summary import IssueDescriptionWidget, IssueSummaryWidget


class WorkItemSummaryContainer(Container):
    """The container that holds the read-only summary of the work item."""

    def __init__(self):
        super().__init__()
        self.visible = False


class WorkItemInfoContainer(Vertical):
    """The container for all the widgets that store/show information (description and other text-based fields) of a
    work item."""

    HELP = 'See Work Item Info section in the help'
    issue: Reactive[JiraIssue | None] = reactive(None, always_update=True)
    """The issue whose information we want to display."""
    clear_information: Reactive[bool] = reactive(False, always_update=True)
    """Reactive variable to clear the summary, description and extra fields."""

    def __init__(self):
        super().__init__(id='work_item_info_container')
        self._has_extra_custom_fields = False
        self.can_focus = True

    @property
    def help_anchor(self) -> str:
        return '#work-item-info'

    @property
    def issue_summary_widget(self) -> IssueSummaryWidget:
        return self.query_one(IssueSummaryWidget)

    @property
    def issue_description_widget(self) -> IssueDescriptionWidget:
        return self.query_one(IssueDescriptionWidget)

    @property
    def summary_container_widget(self) -> WorkItemSummaryContainer:
        return self.query_one(WorkItemSummaryContainer)

    @property
    def extra_fields_container(self) -> VerticalScroll:
        return self.query_one('#work-item-info-extra-scroll-container', expect_type=VerticalScroll)

    @property
    def description_container(self) -> VerticalScroll:
        return self.query_one(
            '#work-item-info-description-scroll-container', expect_type=VerticalScroll
        )

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            with WorkItemSummaryContainer():
                yield IssueSummaryWidget()
            with VerticalScroll(id='work-item-info-description-scroll-container'):
                yield IssueDescriptionWidget()
            yield VerticalScroll(id='work-item-info-extra-scroll-container')

    async def _setup_work_item_description(self, work_item: JiraIssue) -> None:
        if work_item.description:
            base_url = getattr(getattr(self.app, 'config', None), 'jira_base_url', None)
            content: str = work_item.get_description(base_url=base_url)
            if content:
                await self.issue_description_widget.update(content)
            else:
                await self.issue_description_widget.update('Unable to display the description.')
            self.issue_description_widget.visible = True
            self.description_container.visible = True
            self.description_container.border_title = 'Description'
        else:
            self.description_container.visible = False
            self.issue_description_widget.visible = False
            await self.issue_description_widget.update('')

    def watch_issue(self, work_item: JiraIssue | None) -> None:
        # "reset" the information of any previous widget
        self.clear_information = True

        if not work_item:
            return None

        # set the summary of the work item and make the widget visible
        self.issue_summary_widget.update(work_item.summary)
        self.issue_summary_widget.visible = True
        self.summary_container_widget.visible = True

        # set the description of the work item and make the widget visible
        self.run_worker(self._setup_work_item_description(work_item))

        # display all the editable custom fields with whose type is string-textarea
        self._has_extra_custom_fields = False
        if issue_edit_metadata := work_item.get_edit_metadata():
            for field_id, field_data in issue_edit_metadata.items():
                if field_data.get('key', '').startswith('customfield_') or field_id.startswith(
                    'customfield_'
                ):
                    if field_schema := field_data.get('schema'):
                        # only extract abd process editable custom fields of type textarea
                        if (
                            field_schema.get('type') == 'string'
                            and field_schema.get('custom') == CustomFieldTypes.TEXTAREA.value
                        ):
                            # get the value of the custom field
                            if custom_field_value := work_item.get_custom_field_value(field_id):
                                if isinstance(custom_field_value, str):
                                    content = custom_field_value.strip()
                                else:
                                    content = self._extract_adf(custom_field_value)

                                if content:
                                    extra_field_markdown = Markdown(
                                        content, classes='work-item-info-custom-field-textarea'
                                    )
                                    extra_field_markdown.border_title = field_data.get('name')
                                    self.extra_fields_container.mount(extra_field_markdown)
                                    self._has_extra_custom_fields = True

        if self._has_extra_custom_fields:
            self.extra_fields_container.visible = True
            self.description_container.styles.height = '50%'
        else:
            self.description_container.styles.height = '92%'  # leave some space
        return None

    @staticmethod
    def _extract_adf(data) -> str:
        """Extract and convert ADF (Atlassian Document Format) to markdown.

        Args:
            data: ADF document as dict

        Returns:
            Markdown string, or empty string on error
        """
        try:
            from jiratui.utils.adf_helpers import (
                fix_adf_text_with_marks,
                replace_media_with_text,
            )

            if isinstance(data, dict):
                fixed_data = replace_media_with_text(data)
                fixed_data = fix_adf_text_with_marks(fixed_data)
                node = parse_node(fixed_data)
                markdown = node.to_markdown(ignore_error=True)
                return markdown
            return ''
        except Exception:
            return ''

    async def reset_description(self) -> None:
        await self.issue_description_widget.update('')

    def watch_clear_information(self, clear: bool = False) -> None:
        if clear:
            # reset the value of the summary and hide the widget
            self.issue_summary_widget.update('')
            self.issue_summary_widget.visible = False
            self.summary_container_widget.visible = False
            # reset the value of the description and hide the widget
            self.run_worker(self.reset_description())
            self.description_container.visible = False
            self.issue_description_widget.visible = False
            # remove the extra fields and hide the widget
            self.extra_fields_container.visible = False
            self.extra_fields_container.remove_children()
