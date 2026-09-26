import json

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DataTable, TextArea

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.config import CONFIGURATION
from jiratui.utils.ui_actions import Actionable, UIAction


class ConfigTable(Actionable, DataTable, inherit_bindings=False):  # type:ignore[call-arg]
    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.SELECT_CURSOR,
        SupportedActions.CURSOR_UP,
        SupportedActions.CURSOR_DOWN,
        SupportedActions.PAGE_UP,
        SupportedActions.PAGE_DOWN,
        SupportedActions.SCROLL_TOP,
        SupportedActions.SCROLL_BOTTOM,
    ]:
        data = key_bindings.get(supported_action_id.value, {})
        ACTIONS.append(
            UIAction(
                action=supported_action_id.value,
                keys=data.get('keys', []),
                show=data.get('show', False),
                description=data.get('description'),
                tooltip=data.get('tooltip', ''),
            )
        )

    BINDINGS = [  # type:ignore[assignment]
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ]


class ConfigFileScreen(ModalScreen):
    """The screen that displays the configuration settings."""

    BINDINGS = [('escape', 'process_escape', 'Close')]
    TITLE = 'JiraTUI Configuration'

    @property
    def datatable_config_info(self) -> ConfigTable:
        return self.query_one('#config-details', expect_type=ConfigTable)

    @property
    def left_vertical_container(self) -> VerticalScroll:
        return self.query_one('#left-vertical-container', expect_type=VerticalScroll)

    @property
    def textarea(self) -> TextArea:
        return self.query_one(TextArea)

    def compose(self) -> ComposeResult:
        with Horizontal() as h:
            h.border_title = self.TITLE
            yield ConfigTable(cursor_type='row', show_header=False, id='config-details')
            with VerticalScroll(id='left-vertical-container', can_focus=False) as vs:
                vs.display = False
                yield TextArea(
                    language='json', compact=True, read_only=True, classes='config-file-textarea'
                )

    @staticmethod
    def _get_config_data():
        return CONFIGURATION.get().model_dump(exclude={'jira_api_token'})

    @property
    def _json_fields(self) -> list[str]:
        return ['pre_defined_jql_expressions', 'styling', 'git_repositories', 'ssl']

    @on(DataTable.RowSelected)
    def _toggle_left_vertical_container(self, event: DataTable.RowSelected) -> None:
        left_vertical_container = self.left_vertical_container
        if not left_vertical_container.display:
            data = self._get_config_data()
            if event.row_key.value in self._json_fields and event.row_key.value in data:
                left_vertical_container.display = True
                if data.get(event.row_key.value) is not None:
                    self.textarea.load_text(
                        json.dumps(data.get(event.row_key.value), indent=3, sort_keys=True)
                    )
                    self.textarea.border_title = event.row_key.value
        else:
            left_vertical_container.display = False

    def action_process_escape(self) -> None:
        if self.focused == self.textarea:
            self.set_focus(self.datatable_config_info)
            self.left_vertical_container.display = False
        else:
            self.dismiss()

    def on_mount(self) -> None:
        table = self.datatable_config_info
        table.add_columns(*['Property', 'Value'])
        data = self._get_config_data()
        for key, value in data.items():
            if key in self._json_fields:
                display_value = Text('Press enter to view', justify='left', style='blue')
            else:
                row_style = ''
                if isinstance(value, bool):
                    row_style = 'green'
                elif isinstance(value, int):
                    row_style = 'blue'
                display_value = Text(
                    str(value) if value is not None else '-', justify='left', style=row_style
                )

            table.add_row(Text(key, justify='left', style='yellow'), display_value, key=str(key))
