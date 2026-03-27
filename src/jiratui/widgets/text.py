from textual.widgets import Markdown


class IssueDescriptionWidget(Markdown):
    """A widget to display the read-only description of a work item."""

    def __init__(self):
        super().__init__(id='issue_description_text')


class NonEditableTextFieldWidget(Markdown):
    """A widget for fields that support text values but can not be edited in the application."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_class('work-item-info-text-field')
