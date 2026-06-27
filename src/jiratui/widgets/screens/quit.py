from typing import cast

from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuitScreen(ModalScreen[str]):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label('Are you sure you want to quit?', id='question'),
            Button('Quit', variant='warning', id='button-quit', flat=True),
            Button('Cancel', variant='primary', id='button-cancel', flat=True),
            id='dialog',
        )

    async def close_connections(self):
        app = cast('JiraApp', self.screen.app)  # type:ignore[name-defined] # noqa: F821
        await app.api.api.client.close_async_client()
        await app.api.api.async_http_client.close_async_client()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'button-quit':
            self.run_worker(self.close_connections)
            self.app.exit()
        else:
            self.app.pop_screen()
