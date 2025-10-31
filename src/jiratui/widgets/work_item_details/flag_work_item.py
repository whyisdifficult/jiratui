from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, TextArea


class FlagWorkItemScreen(Screen[dict]):
    """A modal screen to allow the user to add/remove a flag to a work item.

    The screen's result is a dictionary with the following keys:
    {
        'update_flag': if True then the issue's flag will be added or removed.
        'note': an optional comment.
    }
    """

    HELP = 'See Flagging Work Items section in the help'
    BINDINGS = [
        ('escape', 'pop_screen', 'Close'),
    ]

    def __init__(self, work_item_key: str, work_item_is_flagged: bool = False):
        super().__init__()
        self._work_item_key = work_item_key
        self._work_item_is_flagged = work_item_is_flagged

    @property
    def help_anchor(self) -> str:
        return '#flagging-work-items'

    @property
    def note(self) -> TextArea:
        return self.query_one(TextArea)

    @property
    def root_container(self) -> Vertical:
        return self.query_one(Vertical)

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        if self._work_item_is_flagged:
            vertical.border_title = f'Remove Flag - {self._work_item_key}'
        else:
            vertical.border_title = f'Add Flag - {self._work_item_key}'
        with vertical:
            message = TextArea(
                placeholder='An optional message to let your team why this work item is (not) flagged...'
            )
            message.border_title = 'Comment'
            yield message
            with ItemGrid(classes='flag-work-item-buttons-grid'):
                yield Button('Save', variant='success', id='flag-work-item-button-save', flat=True)
                yield Button('Cancel', variant='error', id='flag-work-item-button-quit', flat=True)

    def action_pop_screen(self) -> None:
        note = self.note.text.strip() if self.note.text else None
        self.dismiss({'update_flag': False, 'note': note})

    @on(Button.Pressed, '#flag-work-item-button-quit')
    def handle_quit_button(self) -> None:
        note = self.note.text.strip() if self.note.text else None
        self.dismiss({'update_flag': False, 'note': note})

    @on(Button.Pressed, '#flag-work-item-button-save')
    def handle_save_button(self) -> None:
        note = self.note.text.strip() if self.note.text else None
        self.dismiss({'update_flag': True, 'note': note})
