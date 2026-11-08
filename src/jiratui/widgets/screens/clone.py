from dataclasses import dataclass

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse


@dataclass
class CloneWorkItemRequest:
    """The result returned by the clone work item screen when the user clicks the button 'Clone'."""

    work_item_key: str
    summary: str


class SummaryField(Input):
    """A widget to allow users to provide the summary field of the work item that is being cloned."""

    def __init__(self):
        super().__init__()
        self.border_title = 'Summary'
        self.add_class(*['create-update-field-widget'])
        self.placeholder = 'the summary of the new task...'

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        event.stop()
        if event.value is not None:
            self.value = event.value.strip()

    @property
    def validated_summary(self) -> str | None:
        if self.value:
            return self.value.strip()
        return self.value


class CloneWorkItemScreen(ModalScreen[CloneWorkItemRequest]):
    """A modal screen that allows users to clone a work item.

    The screen defines a simple form to allow users to specify the (optional) summary of the new item. If a summary is
    not provided then the summary of the source work item will be used as the summary of the new item.
    """

    BINDINGS = [('escape', 'app.pop_screen', 'Close Help')]

    def __init__(self, work_item_key: str):
        super().__init__()
        self.__work_item_key = work_item_key

    @property
    def summary(self) -> Input:
        return self.query_one(Input)

    @property
    def vertical_container(self) -> Vertical:
        return self.query_one(Vertical)

    @property
    def clone_button(self) -> Button:
        return self.query_one('#clone', Button)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                'The following fields will be cloned: Summary, Assignee, Reporter, Parent, Priority, Type, Description and Due Date',
                classes='tip',
            )
            yield SummaryField()
            with Center():
                yield Button('Clone', id='clone', variant='success', flat=True)

    def on_mount(self) -> None:
        self.vertical_container.border_title = f'Clone Work Item - {self.__work_item_key}'
        self.run_worker(self._get_work_item)

    async def _get_work_item(self) -> None:
        response: APIControllerResponse = await self.app.api.get_issue(  # type:ignore[attr-defined]
            issue_id_or_key=self.__work_item_key
        )
        if response.success and response.result:
            result: JiraIssueSearchResponse | None = response.result
            if result and result.issues:
                work_item: JiraIssue = result.issues[0]
                self.summary.value = work_item.summary
                self.clone_button.disabled = False
                self.summary.disabled = False
            else:
                self.clone_button.disabled = True
                self.summary.disabled = True
                self.notify(
                    f'Work Item {self.__work_item_key} not found',
                    title='Not Found',
                    severity='error',
                )
        else:
            self.clone_button.disabled = True
            self.summary.disabled = True
            self.notify(
                f'Work Item {self.__work_item_key} not found', title='Not Found', severity='error'
            )

    @on(Button.Pressed, '#clone')
    def _request_action_execution(self) -> None:
        self.dismiss(CloneWorkItemRequest(self.__work_item_key, self.summary.value))
