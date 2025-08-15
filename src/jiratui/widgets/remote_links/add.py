from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Rule, Static

from jiratui.widgets.base import CustomTitle


class RemoteLinkURLInputWidget(Input):
    def __init__(self):
        super().__init__(
            classes='required',
            type='text',
            placeholder='https://www.....',
            tooltip='The URL of the external resource',
        )
        self.border_title = 'URL'
        self.border_subtitle = '(*)'

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.value and event.value.strip():
            if 'http' not in event.value:
                self.value = 'https://'


class RemoteLinkNameInputWidget(Input):
    def __init__(self):
        super().__init__(
            classes='required',
            type='text',
            placeholder='A short title for the link...',
            tooltip='A title to describe the link',
        )
        self.border_title = 'Title'
        self.border_subtitle = '(*)'


class AddRemoteLinkScreen(Screen[dict]):
    """A screen that allows a user to add a new remote link to a work item."""

    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'New Web Link'

    def __init__(self, work_item_key: str | None = None):
        super().__init__()
        self.work_item_key = work_item_key
        self.title = f'{self.TITLE} - Work Item {self.work_item_key}'

    @property
    def link_name(self) -> RemoteLinkNameInputWidget:
        return self.query_one(RemoteLinkNameInputWidget)

    @property
    def link_url(self) -> RemoteLinkURLInputWidget:
        return self.query_one(RemoteLinkURLInputWidget)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-remote-link-button-save', expect_type=Button)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle(self.title)
            yield Static(
                Text('Important: Fields marked with (*) are required.', style='italic orange')
            )
            yield Rule(classes='rule-50')
            with ItemGrid(classes='issue-remote-link-grid'):
                yield RemoteLinkURLInputWidget()
                yield RemoteLinkNameInputWidget()
            yield Rule()
            with ItemGrid(classes='add-remote-link-grid-buttons'):
                yield Button(
                    'Save', variant='success', id='add-remote-link-button-save', disabled=True
                )
                yield Button('Cancel', variant='error', id='add-remote-link-button-quit')

    @on(Input.Blurred, 'RemoteLinkURLInputWidget')
    def validate_url(self):
        value = self.link_url.value
        self.save_button.disabled = (
            False
            if (value and value.strip()) and self.link_name.value and self.link_name.value.strip()
            else True
        )

    @on(Input.Blurred, 'RemoteLinkNameInputWidget')
    def validate_name(self):
        value = self.link_name.value
        self.save_button.disabled = (
            False
            if (value and value.strip()) and self.link_url.value and self.link_url.value.strip()
            else True
        )

    @on(Input.Changed, 'RemoteLinkNameInputWidget')
    def validate_change(self, event: Input.Changed):
        if event.value and event.value.strip():
            self.save_button.disabled = not self.link_url.value or not self.link_url.value.strip()
        else:
            self.save_button.disabled = True

    @on(Button.Pressed, '#add-remote-link-button-save')
    def handle_save(self) -> None:
        if not self.link_url.value and not self.link_name.value:
            self.notify('Enter a URL and a title for the link.')
        else:
            self.dismiss(
                {
                    'link_url': self.link_url.value,
                    'link_title': self.link_name.value,
                }
            )

    @on(Button.Pressed, '#add-remote-link-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})
