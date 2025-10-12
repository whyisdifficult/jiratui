import json

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, TextArea

from jiratui.config import CONFIGURATION


class ConfigFileScreen(ModalScreen):
    """The screen that displays the configuration settings."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'JiraTUI Configuration'

    @property
    def datatable_config_info(self) -> DataTable:
        return self.query_one('#config-details', expect_type=DataTable)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.TITLE
        with vertical:
            yield DataTable(cursor_type='row', show_header=False, id='config-details')
            if CONFIGURATION.get().pre_defined_jql_expressions:
                jql_expressions_textarea = TextArea.code_editor(
                    language='json',
                    read_only=True,
                    classes='config-file-textarea',
                    show_line_numbers=False,
                    compact=True,
                )
                jql_expressions_textarea.border_title = 'pre_defined_jql_expressions'
                yield jql_expressions_textarea

    @staticmethod
    def _get_data():
        return CONFIGURATION.get().model_dump(
            exclude={'pre_defined_jql_expressions', 'jira_api_token', 'git_repositories'}
        )

    async def on_mount(self) -> None:
        table = self.datatable_config_info
        table.add_columns(*['Property', 'Value'])
        rows = []
        data = self._get_data()
        for key, value in data.items():
            rows.append(
                (
                    Text(key, justify='right', style='yellow'),
                    Text(str(value), justify='left'),
                )
            )

        if ssl_config := CONFIGURATION.get().ssl:
            rows.append(
                (
                    Text('ssl.verify_ssl', justify='right', style='yellow'),
                    Text(str(ssl_config.verify_ssl), justify='left'),
                )
            )
            rows.append(
                (
                    Text('ssl.ca_bundle', justify='right', style='yellow'),
                    Text(str(ssl_config.ca_bundle), justify='left'),
                )
            )
            rows.append(
                (
                    Text('ssl.certificate_file', justify='right', style='yellow'),
                    Text(str(ssl_config.certificate_file), justify='left'),
                )
            )
            rows.append(
                (
                    Text('ssl.key_file', justify='right', style='yellow'),
                    Text(str(ssl_config.key_file), justify='left'),
                )
            )
            rows.append(
                (
                    Text('ssl.password', justify='right', style='yellow'),
                    Text(str(ssl_config.password), justify='left'),
                )
            )

        if CONFIGURATION.get().pre_defined_jql_expressions:
            ta = self.query_one(TextArea)
            ta.text = json.dumps(CONFIGURATION.get().pre_defined_jql_expressions, indent=3)

        table.add_rows(rows)
