from textual.widgets import Markdown, Static


class IssueDescriptionWidget(Markdown):
    def __init__(self):
        super().__init__(id='issue_description_text')


class IssueSummaryWidget(Static):
    def __init__(self):
        super().__init__(id='issue_summary', markup=False)
