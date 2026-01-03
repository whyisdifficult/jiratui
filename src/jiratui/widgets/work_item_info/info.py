from textual.app import ComposeResult
from textual.containers import Center, Container, Vertical, VerticalGroup, VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import LoadingIndicator

from jiratui.models import JiraIssue
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
    def description_container(self) -> VerticalScroll:
        return self.query_one(
            '#work-item-info-description-scroll-container', expect_type=VerticalScroll
        )

    @property
    def loading_container(self) -> Center:
        return self.query_one('#work-item-info-loading-container', expect_type=Center)

    @property
    def content_container(self) -> VerticalGroup:
        return self.query_one('#work-item-info-content', expect_type=VerticalGroup)

    def compose(self) -> ComposeResult:
        with Center(id='work-item-info-loading-container') as loading_container:
            loading_container.display = False
            yield LoadingIndicator()
        with VerticalGroup(id='work-item-info-content'):
            with WorkItemSummaryContainer():
                yield IssueSummaryWidget()
            with VerticalScroll(id='work-item-info-description-scroll-container'):
                yield IssueDescriptionWidget()

    async def _setup_work_item_description(self, work_item: JiraIssue) -> None:
        if work_item.description:
            content: str = work_item.get_description()
            if content:
                await self.issue_description_widget.update(content)
            else:
                await self.issue_description_widget.update('Unable to display the description.')
            self.issue_description_widget.visible = True
            self.description_container.visible = True

            # Check if description is required in the edit metadata
            is_required = False
            if issue_edit_metadata := work_item.get_edit_metadata():
                description_field = issue_edit_metadata.get('description', {})
                is_required = description_field.get('required', False)

            # Set border title with required indicator if needed
            if is_required:
                self.description_container.border_title = 'Description'
                self.description_container.border_subtitle = '(*)'
                self.description_container.add_class('required')
            else:
                self.description_container.border_title = 'Description'
                self.description_container.border_subtitle = ''
                self.description_container.remove_class('required')
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
        return None

    async def reset_description(self) -> None:
        """Reset the description widget."""
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

    def show_loading(self) -> None:
        """Show the loading indicator and hide content."""
        self.loading_container.display = True
        self.content_container.display = False

    def hide_loading(self) -> None:
        """Hide the loading indicator and show content."""
        self.loading_container.display = False
        self.content_container.display = True
