from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Select, TextArea

from jiratui.config import CONFIGURATION


class PreDefinedJQLExpressionsWidget(Select):
    """A custom Select widget for selecting pre-defined JQL expressions loaded for the configuration file."""

    def __init__(self, options: list):
        super().__init__(
            options=options,
            prompt='Pre-defined expressions',
            id='issue-search-predefined-jql-selector',
            type_to_search=True,
            compact=True,
            classes='dropdown',
        )
        self.border_title = 'Expression'


class JQLEditorScreen(ModalScreen[str]):
    """A screen that displays an editor for JQL expressions.

    **See Also**:
    - [Use Case: Filter-based search](#use-case-filter-based-search)
    """

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'JQL Expression Editor'

    def __init__(self, content: str | None = None):
        super().__init__()
        self.content = content or ''
        self.predefined_jql_expressions: dict | None = self._pre_defined_jql_expressions

    @property
    def _pre_defined_jql_expressions(self) -> dict | None:
        if CONFIGURATION.get().pre_defined_jql_expressions:
            return CONFIGURATION.get().pre_defined_jql_expressions
        return None

    @property
    def expressions(self) -> list:
        if self.predefined_jql_expressions:
            return list(self.predefined_jql_expressions.items())
        return []

    def compose(self) -> ComposeResult:
        with Vertical() as widget:
            widget.border_title = self.TITLE
            yield PreDefinedJQLExpressionsWidget(
                [(item.get('label'), key) for key, item in self.expressions]
            )
            yield TextArea.code_editor(
                self.content,
                language='sql',
                classes='jql-expression-editor',
                show_line_numbers=False,
                theme='css',
            )

    def on_key(self, event: Key):
        if event.key == 'escape':
            self.dismiss(self.query_one(TextArea).text.strip())

    @on(PreDefinedJQLExpressionsWidget.Changed)
    def select_pre_defined_expression(self, event: Select.Changed) -> None:
        if event.value != Select.NULL:
            if (data := self.predefined_jql_expressions.get(event.value)) and (
                expression := data.get('expression')
            ):
                self.query_one(TextArea).text = expression
