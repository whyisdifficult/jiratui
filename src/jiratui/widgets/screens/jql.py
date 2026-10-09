from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Select, TextArea

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraFilter

FAVOURITE_FILTER_OPTION_PREFIX = 'jira-filter-'


class PreDefinedJQLExpressionsWidget(Select):
    """A custom [Select](#textual.widgets.Select) widget for selecting pre-defined JQL expressions loaded for the
    configuration file."""

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
        self.favourite_filters: dict[str, JiraFilter] = {}

    @property
    def _pre_defined_jql_expressions(self) -> dict | None:
        if self.app.config.pre_defined_jql_expressions:  # type:ignore[attr-defined]
            return self.app.config.pre_defined_jql_expressions  # type:ignore[attr-defined]
        return None

    @property
    def _show_favourite_filters(self) -> bool:
        return self.app.config.show_favourite_filters_in_jql_editor  # type:ignore[attr-defined]

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

    def on_mount(self) -> None:
        if self._show_favourite_filters:
            self.run_worker(self._load_favourite_filters(), exclusive=True)

    async def _load_favourite_filters(self) -> None:
        """Fetches the user's favourite Jira filters and appends them to the options of the dropdown."""

        response: APIControllerResponse = await self.app.api.get_favourite_filters()  # type:ignore[attr-defined]
        if not response.success:
            self.notify(
                f'Unable to fetch your favourite filters: {response.error}',
                severity='warning',
                title='JQL Expression Editor',
            )
            return
        if not response.result:
            return
        self.favourite_filters = {
            f'{FAVOURITE_FILTER_OPTION_PREFIX}{jira_filter.id}': jira_filter
            for jira_filter in response.result
        }
        widget = self.query_one(PreDefinedJQLExpressionsWidget)
        selected_value = widget.value
        widget.set_options(
            [(item.get('label'), key) for key, item in self.expressions]
            + [
                (f'★ {jira_filter.name}', key)
                for key, jira_filter in self.favourite_filters.items()
            ]
        )
        if selected_value != Select.NULL:
            # setting new options clears the selection
            widget.value = selected_value

    def on_key(self, event: Key):
        if event.key == 'escape':
            self.dismiss(self.query_one(TextArea).text.strip())

    @on(PreDefinedJQLExpressionsWidget.Changed)
    def select_pre_defined_expression(self, event: Select.Changed) -> None:
        if event.value in self.favourite_filters:
            jira_filter = self.favourite_filters[event.value]
            self.query_one(TextArea).text = jira_filter.jql or f'filter = {jira_filter.id}'
        elif event.value != Select.NULL:
            if (data := self.predefined_jql_expressions.get(event.value)) and (
                expression := data.get('expression')
            ):
                self.query_one(TextArea).text = expression
