from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Markdown

from jiratui.widgets.base import CustomTitle


class HelpScreen(ModalScreen):
    """The screen that displays help."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]
    TITLE = 'Jira TUI Help'

    def __init__(self, content: str | None = None):
        super().__init__()
        self.content = content or ''

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield CustomTitle(self.TITLE)
            yield Markdown(self.content)
