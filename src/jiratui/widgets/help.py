import inspect
import os

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import MarkdownViewer


class HelpScreen(ModalScreen):
    """The screen that displays help."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]
    TITLE = 'JiraTUI Help'
    HELP = 'This is the in-app help system. If what you are looking for is not here then please refer to the official help at https://jiratui.readthedocs.io/en/latest/index.html'

    def __init__(self, anchor: str | None = None):
        super().__init__()
        self._anchor = anchor
        self._content = None
        try:
            in_app_help_filename = self._get_in_app_help_filename()
            with open(in_app_help_filename, 'r') as file:
                self._content = file.read()
        except FileNotFoundError:
            self._content = 'Unable to load the contents of the help. Please refer to https://jiratui.readthedocs.io/en/latest/index.html'

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self._content, show_table_of_contents=True)

    @staticmethod
    def _get_in_app_help_filename() -> str:
        filename = inspect.getfile(HelpScreen)
        directory = os.path.dirname(filename)
        directories = directory.split('/')[:-1]
        directories.append('utils/in_app_help.md')
        return '/'.join(directories)

    async def on_mount(self):
        viewer = self.query_one(MarkdownViewer)
        viewer.border_title = self.TITLE
        if self._anchor:
            await viewer.go(self._anchor.strip())
