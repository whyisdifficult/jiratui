from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DataTable

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraMyselfInfo, JiraServerInfo
from jiratui.widgets.base import CustomTitle


class ServerInfoScreen(ModalScreen):
    """The screen that displays information of the Jira instance server."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]
    TITLE = 'Server Details'

    def __init__(self, server_info: JiraServerInfo | None = None):
        super().__init__()
        self._server_info = server_info

    @property
    def datatable_server_info(self) -> DataTable:
        return self.query_one('#server-details', expect_type=DataTable)

    @property
    def datatable_user_info(self) -> DataTable:
        return self.query_one('#user-details', expect_type=DataTable)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield CustomTitle(self.TITLE)
            yield DataTable(cursor_type='row', show_header=False, id='server-details')
            yield CustomTitle('User Account Details')
            yield DataTable(cursor_type='row', show_header=False, id='user-details')

    async def on_mount(self) -> None:
        server_info: JiraServerInfo | None = None
        if self._server_info:
            server_info = self._server_info
        else:
            response_server_info: APIControllerResponse = await self.app.api.server_info()  # type:ignore[attr-defined]
            if not response_server_info.success or not (server_info := response_server_info.result):
                pass

        if server_info:
            table = self.datatable_server_info
            table.add_columns(*['Property', 'Value'])
            table.add_rows(
                [
                    (
                        Text('Base URL', justify='right', style='yellow'),
                        Text(server_info.base_url, justify='left'),
                    ),
                    (
                        Text(
                            'Display URL Servicedesk Help Center', justify='right', style='yellow'
                        ),
                        Text(server_info.display_url_servicedesk_help_center, justify='left'),
                    ),
                    (
                        Text('Display URL Confluence', justify='right', style='yellow'),
                        Text(server_info.display_url_confluence, justify='left'),
                    ),
                    (
                        Text('Version', justify='right', style='yellow'),
                        Text(server_info.version, justify='left'),
                    ),
                    (
                        Text('Deployment Type', justify='right', style='yellow'),
                        Text(server_info.deployment_type, justify='left'),
                    ),
                    (
                        Text('Build Number', justify='right', style='yellow'),
                        Text(str(server_info.build_number), justify='left'),
                    ),
                    (
                        Text('Build Date', justify='right', style='yellow'),
                        Text(server_info.build_date, justify='left'),
                    ),
                    (
                        Text('Server Time', justify='right', style='yellow'),
                        Text(server_info.server_time or '', justify='left'),
                    ),
                    (
                        Text('SCM Info', justify='right', style='yellow'),
                        Text(server_info.scm_info, justify='left'),
                    ),
                    (
                        Text('Server Title', justify='right', style='yellow'),
                        Text(server_info.server_title, justify='left'),
                    ),
                    (
                        Text('Default Locale', justify='right', style='yellow'),
                        Text(server_info.default_locale, justify='left'),
                    ),
                    (
                        Text('Server Time Zone', justify='right', style='yellow'),
                        Text(server_info.server_time_zone, justify='left'),
                    ),
                ]
            )

        user_info: JiraMyselfInfo | None
        response_myself: APIControllerResponse = await self.app.api.myself()  # type:ignore[attr-defined]
        if response_myself.success and (user_info := response_myself.result):
            table = self.datatable_user_info
            table.add_columns(*['Property', 'Value'])
            is_active = Text('No', justify='left', style='red')
            if user_info.active:
                is_active = Text('Yes', justify='left', style='green')
            table.add_rows(
                [
                    (
                        Text('Account ID', justify='right', style='yellow'),
                        Text(user_info.account_id, justify='left'),
                    ),
                    (
                        Text('Account Type', justify='right', style='yellow'),
                        Text(user_info.account_type, justify='left'),
                    ),
                    (
                        Text('Active', justify='right', style='yellow'),
                        is_active,
                    ),
                    (
                        Text('Name', justify='right', style='yellow'),
                        Text(user_info.display_name or '', justify='left'),
                    ),
                    (
                        Text('Email', justify='right', style='yellow'),
                        Text(user_info.email or '', justify='left'),
                    ),
                    (
                        Text('User Groups', justify='right', style='yellow'),
                        Text(user_info.user_groups or '', justify='left'),
                    ),
                ]
            )
