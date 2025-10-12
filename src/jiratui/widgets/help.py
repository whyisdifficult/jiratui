from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import MarkdownViewer

from jiratui.constants import APPLICATION_HELP


class HelpScreen(ModalScreen):
    """The screen that displays help."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]
    TITLE = 'JiraTUI Help'
    HELP = None

    def __init__(self, anchor: str | None = None):
        super().__init__()
        self.__class__.HELP = APPLICATION_HELP
        self._anchor = anchor

    def compose(self) -> ComposeResult:
        vertical = VerticalScroll()
        vertical.border_title = self.TITLE
        with vertical:
            yield MarkdownViewer(APPLICATION_HELP, show_table_of_contents=True)

    async def on_mount(self):
        viewer = self.query_one(MarkdownViewer)
        if self._anchor:
            await viewer.go(self._anchor.strip())
