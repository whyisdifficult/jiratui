from typing import Any, cast

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalGroup, VerticalScroll
from textual.reactive import Reactive, reactive

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.exceptions import UpdateWorkItemException, ValidationError
from jiratui.models import JiraIssue
from jiratui.utils.adf2md.adf2md import adf2md
from jiratui.utils.work_item_updates import (
    field_supports_text_value,
    updating_text_fields_is_supported,
)
from jiratui.widgets.text import IssueDescriptionWidget, NonEditableTextFieldWidget
from jiratui.widgets.work_item_info.widgets import (
    EditableTextFieldWidget,
    IssueSummaryWidget,
    WorkItemSummaryContainer,
)


class WorkItemInfoContainer(Vertical):
    """The container for all the widgets that store/show information (description and other text-based fields) of a
    work item."""

    HELP = 'See Work Item Info section in the help'
    issue: Reactive[JiraIssue | None] = reactive(None, always_update=True)
    """The issue whose information we want to display."""
    clear_information: Reactive[bool] = reactive(False, always_update=True)
    """Reactive variable to clear the summary, description and extra fields."""
    BINDINGS = [
        ('ctrl+s', 'save_work_item', 'Save'),
    ]

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

    async def action_save_work_item(self) -> None:
        """Attempts to save the information fields of the work item with the updated values.

        Note: if this method is called then it means that the "save_work_item" action is supported by the widget and
        that the application supports updating text fields.

        Returns:
            `None`
        """

        if not self.issue:
            self.notify(
                'Select a work item before saving changes',
                severity='error',
                title='Update Work Item',
            )
            return None

        # build the payload with the fields that will be updated
        payload: dict = self._build_payload_for_update()  # TODO

        if not payload:
            return None
        return None
        application = cast('JiraApp', self.app)  # type: ignore[name-defined] # noqa: F821
        try:
            response: APIControllerResponse = await application.api.update_issue(
                self.issue,
                payload,
            )
        except UpdateWorkItemException as e:
            self.notify(
                f'An error occurred while trying to update the item: {e}',
                severity='error',
                title='Update Work Item',
            )
        except ValidationError as e:
            self.notify(f'Data validation error: {e}', severity='error', title='Update Work Item')
        except Exception as e:
            self.notify(
                f'An unknown error occurred while trying to update the item: {e}',
                severity='error',
                title='Update Work Item',
            )
        else:
            if response.success:
                self.notify('Work item updated successfully.', title='Update Work Item')
                # fetch the issue again to retrieve the latest changes and update the form
                # TODO considering merging and reusing with details._refresh_work_item_information
                await self._refresh_work_item(application)
            else:
                self.notify(
                    'The work item was not updated.', severity='error', title='Update Work Item'
                )
                self.notify(response.error, severity='error', title='Update Work Item')

        self.refresh_bindings()
        return None

    def _build_payload_for_update(self) -> dict:
        """Builds the payload with the fields and values to update the work item.

        Returns:
            A dictionary with a mapping between field ids and their values.
        """

        payload: dict[str, Any] = {}

        # TODO the issue_description_widget may be a Markdow widget if the app does nto support updating text fields or, a TextArea widget if it does
        #   we need to check this here in order to get the current value of the description field
        if self.issue_description_widget.source:
            payload['description'] = self.issue_description_widget.source
        else:
            payload['description'] = None

        for widget in self.extra_fields_container.children:
            if isinstance(widget, EditableTextFieldWidget):
                payload[widget.jira_field_key] = widget.get_value_for_update()
        return payload

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == 'save_work_item':
            return updating_text_fields_is_supported()
        return True

    async def _refresh_work_item(self, application) -> None:
        """Fetches the work item details and triggers the update of the information fields in this widget.

        Args:
            application: the JiraApp instance.

        Returns:
            `None`
        """

        issue_details_response = await application.api.get_issue(issue_id_or_key=self.issue.key)
        if issue_details_response.success and issue_details_response.result:
            self.issue = issue_details_response.result.issues[0]

    async def _setup_work_item_description(self, work_item: JiraIssue) -> None:
        """Updates the widget that contains the description of the work item.

        Args:
            work_item: the work item.

        Returns:
            `None`.
        """

        if work_item.description:
            content: str = work_item.get_description()
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
        """Updates the widgets in this widget when the work item is updated.

        The type of widgets displayed as children in this widget varies depending on the type of field and, on whether
        JiraTUI supports updating rich/full text fields, e.g. like the system field "environment". If a field can be
        updated by the user then the widget used for the field would be a writeable `Textarea`
        (`EditableTextFieldWidget`); otherwise it would be a read-only `Markdown` (`NonEditableTextFieldWidget`) field.

        Args:
            work_item: the work item instance.

        Returns:
            `None`.
        """

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

        # display editable custom fields whose type supports rich/full text values
        self._has_extra_custom_fields = False
        if issue_edit_metadata := work_item.get_edit_metadata():
            extra_field_widget: NonEditableTextFieldWidget | EditableTextFieldWidget
            for field_id, field_metadata in issue_edit_metadata.items():
                # check if the field supports rich/full text as its value
                if not field_supports_text_value(field_id, field_metadata):
                    continue
                # get the value of the field; either a custom field or an "additional" field in the JiraIssue object
                if field_id in work_item.custom_fields:
                    field_value: Any = work_item.get_custom_field_value(field_id)
                elif field_id in work_item.additional_fields:
                    field_value = work_item.get_additional_field_value(field_id)
                else:
                    continue

                content: str = ''
                if field_value:
                    if isinstance(field_value, str):
                        content = field_value.strip()
                    elif isinstance(field_value, dict) or isinstance(field_value, list):
                        # convert Jira ADF to Markdown string
                        content = self._extract_adf(field_value)
                        if field_value and not content:
                            self.notify(
                                'Failed to extract the content of this field', severity='error'
                            )
                    else:
                        continue

                # determine what type of widget to use for the field depending on whether the app supports
                # editing the type of the field
                if updating_text_fields_is_supported():
                    extra_field_widget = EditableTextFieldWidget(
                        field_id,
                        field_metadata.get('required'),
                        text=content,
                    )
                else:
                    extra_field_widget = NonEditableTextFieldWidget(content=content)

                extra_field_widget.border_title = field_metadata.get('name')
                # mount the widget
                self.extra_fields_container.mount(extra_field_widget)
                self._has_extra_custom_fields = True

        if self._has_extra_custom_fields:
            self.extra_fields_container.visible = True
            self.description_container.styles.height = '50%'
        else:
            self.description_container.styles.height = '92%'  # leave some space
        return None

    @staticmethod
    def _extract_adf(data: dict | list) -> str:
        try:
            return adf2md(data)
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
