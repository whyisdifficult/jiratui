from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Rule, Select, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import LinkIssueType
from jiratui.widgets.base import CustomTitle


class LinkedWorkItemInputWidget(Input):
    def __init__(self):
        super().__init__(
            classes='required',
            type='text',
            placeholder='e.g. ABC-1234',
            tooltip='Enter a case-sensitive key',
        )
        self.border_title = 'Work Item Key'
        self.border_subtitle = '(*)'


class IssueLinkTypeSelector(Select):
    def __init__(self, items: list[tuple[str, str]]):
        super().__init__(
            options=items,
            prompt='Select a link type',
            name='issue_link_types',
            type_to_search=True,
            compact=True,
        )
        self.border_title = 'Link Types'


class AddWorkItemRelationshipScreen(Screen[dict]):
    BINDINGS = [('escape', 'app.pop_screen', 'Close')]
    TITLE = 'Link Work Items'

    def __init__(self, work_item_key: str | None = None):
        super().__init__()
        self.work_item_key = work_item_key
        self.title = f'{self.TITLE} - Work Item: {self.work_item_key}'

    @property
    def relationship_type(self) -> IssueLinkTypeSelector:
        return self.query_one(IssueLinkTypeSelector)

    @property
    def linked_work_item_key(self) -> LinkedWorkItemInputWidget:
        return self.query_one(LinkedWorkItemInputWidget)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-link-button-save', expect_type=Button)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield CustomTitle(self.title)
            yield Static(
                Text('Important: Fields marked with (*) are required.', style='italic orange')
            )
            yield Rule(classes='rule-50')
            with ItemGrid(classes='issue-linking-grid'):
                yield IssueLinkTypeSelector([])
                yield LinkedWorkItemInputWidget()
            with ItemGrid(classes='issue-linking-grid-buttons'):
                yield Button('Save', variant='success', id='add-link-button-save', disabled=True)
                yield Button('Cancel', variant='error', id='add-link-button-quit')

    @on(Input.Blurred, 'LinkedWorkItemInputWidget')
    def validate_work_item_key(self):
        value = self.linked_work_item_key.value
        self.save_button.disabled = (
            False if (value and value.strip()) and self.relationship_type.selection else True
        )

    @on(Input.Changed, 'LinkedWorkItemInputWidget')
    def validate_change(self, event: Input.Changed):
        if event.value and event.value.strip():
            self.save_button.disabled = not self.relationship_type.selection
        else:
            self.save_button.disabled = True

    @on(Select.Changed, 'IssueLinkTypeSelector')
    def validate_relationship(self):
        value = self.linked_work_item_key.value
        self.save_button.disabled = (
            False if (value and value.strip()) and self.relationship_type.selection else True
        )

    async def on_mount(self) -> None:
        self.run_worker(self.fetch_issue_link_types())

    async def fetch_issue_link_types(self) -> None:
        response: APIControllerResponse = await self.app.api.issue_link_types()  # type:ignore[attr-defined]
        if not response.success:
            self.notify(
                'Unable to fetch the types of supported links',
                title='Link Work Items',
                severity='error',
            )
            self.relationship_type.set_options([])
        else:
            link_type: LinkIssueType
            options: list[tuple[str, str]] = []
            for link_type in response.result or []:
                options.append((link_type.inward, f'{link_type.id}:inward'))
                options.append((link_type.outward, f'{link_type.id}:outward'))
            self.relationship_type.set_options(options)

    @on(Button.Pressed, '#add-link-button-save')
    def handle_save(self) -> None:
        if not self.relationship_type.selection and not self.linked_work_item_key.value:
            self.notify('Select the type of link and the work item', title='Link Work Items')
        else:
            link_type_id, link_type = self.relationship_type.selection.split(':')
            self.dismiss(
                {
                    'right_issue_key': self.linked_work_item_key.value,
                    'link_type': link_type,
                    'link_type_id': link_type_id,
                }
            )

    @on(Button.Pressed, '#add-link-button-quit')
    def handle_cancel(self) -> None:
        self.dismiss({})
