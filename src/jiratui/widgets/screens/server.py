from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import DataTable

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.config import CONFIGURATION
from jiratui.constants import DEFAULT_JIRA_API_VERSION
from jiratui.models import JiraGlobalSettings, JiraMyselfInfo, JiraServerInfo
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

    @property
    def datatable_config_info(self) -> DataTable:
        return self.query_one('#config-details', expect_type=DataTable)

    @property
    def global_settings_details(self) -> DataTable:
        return self.query_one('#global-settings-details', expect_type=DataTable)

    def compose(self) -> ComposeResult:
        vertical = VerticalScroll()
        vertical.border_title = self.TITLE
        with vertical:
            yield CustomTitle('JiraTUI API Configuration')
            yield DataTable(cursor_type='row', show_header=False, id='config-details')
            yield CustomTitle('Server Information')
            yield DataTable(cursor_type='row', show_header=False, id='server-details')
            yield CustomTitle('User Account Details')
            yield DataTable(cursor_type='row', show_header=False, id='user-details')
            yield CustomTitle('Jira Global Settings')
            yield DataTable(cursor_type='row', show_header=False, id='global-settings-details')

    def _get_server_info(self) -> JiraServerInfo | None:
        return self._server_info

    async def on_mount(self) -> None:
        server_info: JiraServerInfo | None
        if not (server_info := self._get_server_info()):
            response_server_info: APIControllerResponse = await self.app.api.server_info()  # type:ignore[attr-defined]
            if not response_server_info.success or not (server_info := response_server_info.result):
                pass

        if server_info:
            self.datatable_server_info.add_columns(*['Property', 'Value'])
            self.datatable_server_info.add_rows(
                [
                    (
                        Text('Base URL', justify='right', style='yellow'),
                        Text(server_info.base_url, justify='left'),
                    ),
                    (
                        Text(
                            'Display URL Servicedesk Help Center', justify='right', style='yellow'
                        ),
                        Text(server_info.get_display_url_servicedesk_help_center(), justify='left'),
                    ),
                    (
                        Text('Display URL Confluence', justify='right', style='yellow'),
                        Text(server_info.get_display_url_confluence(), justify='left'),
                    ),
                    (
                        Text('Version', justify='right', style='yellow'),
                        Text(server_info.get_version(), justify='left'),
                    ),
                    (
                        Text('Deployment Type', justify='right', style='yellow'),
                        Text(server_info.get_deployment_type(), justify='left'),
                    ),
                    (
                        Text('Build Number', justify='right', style='yellow'),
                        Text(server_info.get_build_number(), justify='left'),
                    ),
                    (
                        Text('Build Date', justify='right', style='yellow'),
                        Text(server_info.get_build_date(), justify='left'),
                    ),
                    (
                        Text('Server Time', justify='right', style='yellow'),
                        Text(server_info.get_server_time(), justify='left'),
                    ),
                    (
                        Text('SCM Info', justify='right', style='yellow'),
                        Text(server_info.get_scm_info(), justify='left'),
                    ),
                    (
                        Text('Server Title', justify='right', style='yellow'),
                        Text(server_info.get_server_title(), justify='left'),
                    ),
                    (
                        Text('Default Locale', justify='right', style='yellow'),
                        Text(server_info.get_default_locale(), justify='left'),
                    ),
                    (
                        Text('Server Time Zone', justify='right', style='yellow'),
                        Text(server_info.get_server_time_zone(), justify='left'),
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
                        Text(user_info.get_account_id(), justify='left'),
                    ),
                    (
                        Text('Username', justify='right', style='yellow'),
                        Text(user_info.get_username(), justify='left'),
                    ),
                    (
                        Text('Account Type', justify='right', style='yellow'),
                        Text(str(user_info.account_type), justify='left'),
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

        self.datatable_config_info.add_columns(*['Property', 'Value'])
        self.datatable_config_info.add_rows(
            [
                (
                    Text('API Version', justify='right', style='yellow'),
                    Text(
                        str(CONFIGURATION.get().jira_api_version) or str(DEFAULT_JIRA_API_VERSION),
                        justify='left',
                    ),
                ),
            ]
        )

        jira_global_settings: JiraGlobalSettings | None
        response_global_settings: APIControllerResponse = await self.app.api.global_settings()  # type:ignore[attr-defined]
        if response_myself.success and (jira_global_settings := response_global_settings.result):
            self.global_settings_details.add_columns(*['Property', 'Value'])
            self.global_settings_details.add_rows(
                [
                    (
                        Text('Attachments Enabled', justify='right', style='yellow'),
                        Text(jira_global_settings.display_attachments_enabled(), justify='left'),
                    ),
                    (
                        Text('Issue Linking Enabled', justify='right', style='yellow'),
                        Text(jira_global_settings.display_issue_linking_enabled(), justify='left'),
                    ),
                    (
                        Text('Subtasks Enabled', justify='right', style='yellow'),
                        Text(jira_global_settings.display_subtasks_enabled(), justify='left'),
                    ),
                    (
                        Text('Voting Enabled', justify='right', style='yellow'),
                        Text(jira_global_settings.display_voting_enabled() or '', justify='left'),
                    ),
                    (
                        Text('Time Tracking Enabled', justify='right', style='yellow'),
                        Text(jira_global_settings.display_time_tracking_enabled(), justify='left'),
                    ),
                    (
                        Text('Watching Enabled', justify='right', style='yellow'),
                        Text(jira_global_settings.display_watching_enabled(), justify='left'),
                    ),
                    (
                        Text('Unassigned Issues Allowed', justify='right', style='yellow'),
                        Text(
                            jira_global_settings.display_unassigned_issues_allowed(), justify='left'
                        ),
                    ),
                ]
            )
            if tracking_configuration := jira_global_settings.time_tracking_configuration:
                self.global_settings_details.add_rows(
                    [
                        (
                            Text('Default Unit', justify='right', style='yellow'),
                            Text(tracking_configuration.display_default_unit(), justify='left'),
                        ),
                        (
                            Text('Time Format', justify='right', style='yellow'),
                            Text(tracking_configuration.display_time_format(), justify='left'),
                        ),
                        (
                            Text('Working Days per Week', justify='right', style='yellow'),
                            Text(
                                tracking_configuration.display_working_days_per_week(),
                                justify='left',
                            ),
                        ),
                        (
                            Text('Working Hours per Day', justify='right', style='yellow'),
                            Text(
                                tracking_configuration.display_working_hours_per_day(),
                                justify='left',
                            ),
                        ),
                    ]
                )
