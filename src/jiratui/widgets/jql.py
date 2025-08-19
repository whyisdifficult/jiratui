from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Select, TextArea

from jiratui.config import CONFIGURATION
from jiratui.widgets.base import CustomTitle


class PreDefinedJQLExpressionsWidget(Select):
    def __init__(self, options: list):
        super().__init__(
            options=options,
            prompt='Pre-defined expressions',
            id='issue-search-predefined-jql-selector',
            type_to_search=True,
            compact=True,
            classes='jira-selector',
        )
        self.border_title = 'Expression'


class JQLEditorScreen(ModalScreen[str]):
    """A screen that displays an editor for JQL expressions."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]
    TITLE = 'JQL Expression Editor'

    def __init__(self, content: str | None = None):
        super().__init__()
        self.content = content or ''
        self.predefined_jql_expressions: dict | None = None
        if CONFIGURATION.get().pre_defined_jql_expressions:
            self.predefined_jql_expressions = CONFIGURATION.get().pre_defined_jql_expressions

    @property
    def expressions(self) -> list:
        if self.predefined_jql_expressions:
            return list(self.predefined_jql_expressions.items())
        return []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle('JQL Expression Editor')
            yield PreDefinedJQLExpressionsWidget(
                [(item.get('label'), key) for key, item in self.expressions]
            )
            yield TextArea.code_editor(
                self.content,
                language='sql',
                classes='jql-expression-editor',
                show_line_numbers=False,
            )

    def on_key(self, event: Key):
        if event.key == 'escape':
            self.dismiss(self.query_one(TextArea).text.strip())

    @on(PreDefinedJQLExpressionsWidget.Changed)
    def select_pre_defined_expression(self, event: Select.Changed) -> None:
        if event.value != Select.BLANK:
            if (data := self.predefined_jql_expressions.get(event.value)) and (
                expression := data.get('expression')
            ):
                self.query_one(TextArea).text = expression
