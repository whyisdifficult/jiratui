from textual.containers import Container
from textual.widgets import Static, TextArea


class WorkItemSummaryContainer(Container):
    """The container that holds the read-only summary of the work item."""

    def __init__(self):
        super().__init__()
        self.visible = False


class IssueSummaryWidget(Static):
    """The read-only summary of a work item."""

    def __init__(self):
        super().__init__(id='issue_summary', markup=False)


class EditableTextFieldWidget(TextArea):
    """A widget for fields that support text values and that can be edited in the application."""

    def __init__(self, jira_field_key: str, required: bool | None = None, **kwargs):
        super().__init__(**kwargs)
        self.jira_field_key = jira_field_key
        self.tooltip = 'Markdown is supported'
        self.add_class('work-item-info-text-field')
        if required:
            self.border_subtitle = '(*)'
            self.add_class('required')

    def get_value_for_update(self) -> str | None:
        """Returns the value of the field in the format required for updating the field in Jira.

        Returns: a string; `None` if the field has no value.
        """

        if self.text is not None:
            return self.text
        return None
