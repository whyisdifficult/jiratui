import logging
import sys

from pythonjsonlogger.json import JsonFormatter
from textual.app import App
from textual.binding import Binding

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.config import CONFIGURATION, ApplicationConfiguration
from jiratui.constants import LOGGER_NAME
from jiratui.models import JiraServerInfo
from jiratui.widgets.quit import QuitScreen
from jiratui.widgets.screens import MainScreen
from jiratui.widgets.server_info import ServerInfoScreen


class JiraApp(App):
    """Implements the application."""

    CSS_PATH = 'css/jt.tcss'
    """The path to the file with the TCSS (Textual CSS) definitions."""

    TITLE = 'Jira TUI'
    BINDINGS = [
        Binding(key='f1,ctrl+question_mark,ctrl+shift+slash', action='help', description='Help'),
        Binding(key='f2', action='server_info', description='Server Info'),
        Binding(
            key='ctrl+q',
            action='quit',
            description='Quit',
            key_display='^q',
            tooltip='Quit',
            show=True,
        ),
    ]
    DEFAULT_THEME = 'textual-dark'

    def __init__(
        self,
        settings: ApplicationConfiguration,
        project_key: str | None = None,
        user_account_id: str | None = None,
        jql_expression_id: int | None = None,
    ):
        super().__init__()
        self.config = settings
        CONFIGURATION.set(settings)
        self.api = APIController()  # required so screens can have access to the API
        self.initial_project_key: str | None = project_key
        self.initial_user_account_id: str | None = user_account_id
        self.initial_jql_expression_id: int | None = jql_expression_id
        self.server_info: JiraServerInfo | None = None
        self._setup_logging()

    async def on_mount(self) -> None:
        self.theme = self.DEFAULT_THEME
        self._set_application_title()

        await self.push_screen(
            MainScreen(
                self.api,
                self.initial_project_key,
                self.initial_user_account_id,
                self.initial_jql_expression_id,
            )
        )

    async def action_help(self) -> None:
        from jiratui.widgets.help import HelpScreen

        # get the widget that is currently focused
        focused = self.focused

        def restore_focus(response) -> None:
            if focused:
                # re-focus the widget that was focused before the action
                self.screen.set_focus(focused)

        self.set_focus(None)

        await self.push_screen(HelpScreen(focused.HELP), restore_focus)

    async def action_server_info(self) -> None:
        """Handles the event to show the information of the Jira server instance."""
        await self.push_screen(ServerInfoScreen(server_info=self.server_info))

    async def action_quit(self) -> None:
        """Handles the event to quit the application."""
        await self.push_screen(QuitScreen())

    async def _set_application_title_using_server_info(self) -> None:
        response_server_info: APIControllerResponse = await self.api.server_info()
        if (
            response_server_info.success
            and response_server_info.result
            and response_server_info.result.base_url_or_server_title
        ):
            self.server_info = response_server_info.result
            self.title = f'{self.title} - {self.server_info.base_url_or_server_title}'  # type:ignore[has-type]

    def _set_application_title(self) -> None:
        if (custom_title := CONFIGURATION.get().tui_title) and custom_title.strip():
            self.title = custom_title.strip()
        if CONFIGURATION.get().tui_title_include_jira_server_title:
            if self.server_info:
                self.title = f'{self.title} - {self.server_info.base_url_or_server_title}'
            else:
                self.run_worker(self._set_application_title_using_server_info())

    def _setup_logging(self) -> None:
        self.logger = logging.getLogger(LOGGER_NAME)
        self.logger.setLevel(logging.WARNING)
        try:
            fh = logging.FileHandler(CONFIGURATION.get().log_file)
        except Exception:
            pass
        else:
            fh.setLevel(logging.WARNING)
            fh.setFormatter(JsonFormatter())
            self.logger.addHandler(fh)


if __name__ == '__main__':
    try:
        JiraApp(ApplicationConfiguration()).run()  # type: ignore[call-arg] # noqa
    except Exception as e:
        sys.exit(str(e))
