from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label, Static

from jiratui.actions.constants import SupportedActions
from jiratui.actions.keys import get_application_key_bindings
from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import Votes
from jiratui.utils.ui_actions import Actionable, UIAction


@dataclass
class WorkItemVoteUpdateRequest:
    """"""

    work_item_key: str
    vote: bool
    """If true then the user is voting for the work item; otherwise the user is not voting for the work item."""
    update: bool
    """If true then the vote of the users must be updated based on the value of `vote`."""


class WorkItemVotesScreen(Actionable, ModalScreen[WorkItemVoteUpdateRequest]):
    """A modal screen that allows users to view the votes and update their vote on work item."""

    ACTIONS: list[UIAction] = []
    # set up the key-bindings based on the configuration selected by the user
    key_bindings: dict[str, dict] = get_application_key_bindings()
    for supported_action_id in [
        SupportedActions.ADD_VOTE,
        SupportedActions.DELETE_VOTE,
    ]:
        data = key_bindings.get(supported_action_id.value, {})
        ACTIONS.append(
            UIAction(
                action=supported_action_id.value,
                keys=data.get('keys', []),
                show=data.get('show', False),
                description=data.get('description'),
                tooltip=data.get('tooltip', ''),
            )
        )

    BINDINGS = [  # type:ignore[assignment]
        Binding(
            key=','.join(action.keys),
            action=action.action,
            show=action.show,
            description=action.description or '',
            tooltip=action.tooltip,
        )
        for action in ACTIONS
        if isinstance(action.action, str)
    ] + [Binding('escape', 'app.pop_screen', 'Close')]

    def __init__(self, work_item_key: str):
        super().__init__()
        self.__work_item_key = work_item_key
        self.__voting_enabled = True
        self.__unvoting_enabled = False

    @property
    def vertical_container(self) -> Vertical:
        return self.query_one(Vertical)

    @property
    def message(self) -> Static:
        return self.query_one('#message', Static)

    @property
    def vote_status_field(self) -> Label:
        return self.query_one('#vote_status', Label)

    @property
    def datatable(self) -> DataTable:
        return self.query_one(DataTable)

    def compose(self) -> ComposeResult:
        with Vertical():
            label = Label('', id='vote_status')
            label.styles.display = 'none'
            yield label
            yield Static(id='message')
            data_table: DataTable = DataTable(cursor_type='row')
            data_table.display = False
            yield data_table
        yield Footer(compact=True, show_command_palette=False)

    def on_mount(self) -> None:
        self.vertical_container.border_title = f'Votes - {self.__work_item_key}'
        self.run_worker(self._populate_table)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""

        if action == SupportedActions.ADD_VOTE.value and not self.__voting_enabled:
            return False
        if action == SupportedActions.DELETE_VOTE.value and not self.__unvoting_enabled:
            return False
        return True

    async def _populate_table(self) -> None:
        response: APIControllerResponse = await self.app.api.get_work_item_votes(  # type:ignore[attr-defined]
            issue_id_or_key=self.__work_item_key
        )
        if response.success and response.result:
            votes: Votes = response.result
            self.__voting_enabled = not votes.has_voted
            self.__unvoting_enabled = votes.has_voted
            if votes.has_voted:
                self.vote_status_field.content = 'Voted'
                self.vote_status_field.styles.display = 'block'
            self.datatable.clear()
            if votes.voters:
                self.datatable.add_columns('Name')
                for voter in votes.voters:
                    self.datatable.add_row(voter.display_name)
                self.datatable.border_subtitle = f'{votes.votes} votes'
                self.datatable.border_title = 'Voters'
                self.datatable.display = True
                self.message.display = False
            else:
                self.message.content = 'The work item does not have votes yet.'
                self.message.display = True
        self.refresh_bindings()

    def action_add_vote(self) -> None:
        self.dismiss(WorkItemVoteUpdateRequest(self.__work_item_key, True, update=True))

    def action_delete_vote(self) -> None:
        self.dismiss(WorkItemVoteUpdateRequest(self.__work_item_key, False, update=True))
