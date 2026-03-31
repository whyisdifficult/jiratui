from textual.reactive import Reactive, reactive
from textual.widgets import Input
from textual_autocomplete import AutoComplete, DropdownItem, TargetState
import logging

logger = logging.getLogger(__name__)

class JiraUserInput(Input):
    """An input field for selecting a Jira user.

    This widget holds the Jira user's account id that is used to identify the user. This is useful for operations
    that create/update work items' user fields, such as assignee, reporter, etc.
    """

    update_enabled: Reactive[bool | None] = reactive(True)

    def __init__(self, *args, **kwargs):
        border_subtitle: str | None = kwargs.pop('border_subtitle', None)
        jira_field_key: str | None = kwargs.pop('jira_field_key', None)
        super().__init__(*args, **kwargs)
        self.border_title = 'Assignee'
        self.border_subtitle = border_subtitle
        self.jira_field_key = jira_field_key
        """The id used by Jira to identify this field in the edit-metadata or to update its value in a work item."""
        self._account_id: str | None = None
        """The account id of the currently selected Jira user."""
        self._update_is_enabled: bool = False
        """Indicates whether the work item allows editing/updating this field."""

    @property
    def account_id(self) -> str | None:
        return self._account_id if self.value and self.value.strip() else None

    @account_id.setter
    def account_id(self, account_id: str | None):
        self._account_id = account_id

    @property
    def update_is_enabled(self) -> bool:
        return self._update_is_enabled

    @update_is_enabled.setter
    def update_is_enabled(self, value: bool):
        self._update_is_enabled = value

    def watch_update_enabled(self, enabled: bool = True) -> None:
        self.update_is_enabled = enabled
        self.disabled = not enabled

    def clear(self):
        super().clear()
        self.account_id = None

    def set_value(self, account_id: str | None, value: str | None) -> None:
        self.value = value if value else ''
        self.account_id = account_id

class UsersAutoComplete(AutoComplete):
    """AutoComplete for Jira users that fetches suggestions from Jira API.

    This widget fetches users suggestions dynamically as the user types. It requires an Input widget as the target;
    the target widget MUST provide a property to set the user's account id.
    """

    def __init__(
        self,
        target: Input,
        api_controller,
        required: bool = False,
        title: str | None = None,
    ):
        """Initializes a UsersAutoComplete widget.

        Args:
            target: the Input widget to attach autocomplete to
            api_controller: APIController instance for fetching suggestions.
            required: whether the field is required.
            title: display title for the field (defaults to 'Assignee')
        """

        self._api_controller = api_controller
        self._stored_title = title or 'Assignee'
        self._required = required
        self._cached_suggestions: list[DropdownItem] = []
        self._last_query = ''

        # initialize with empty candidates - will be populated dynamically
        super().__init__(
            target=target,
            candidates=self._get_candidates_sync,   # type:ignore
        )

    def _get_candidates_sync(self, target_state: TargetState) -> list[DropdownItem]:
        """Synchronous wrapper that returns cached suggestions."""

        # get the search string
        search_string = self.get_search_string(target_state)

        # if query changed, trigger async fetch
        if search_string and search_string != self._last_query:
            self._last_query = search_string
            # schedule async fetch - don't await here since this must be sync
            self.call_later(self._fetch_suggestions, search_string)
        return self._cached_suggestions

    async def _fetch_suggestions(self, query: str) -> None:
        """Fetch users suggestions from Jira API asynchronously."""

        if not query:
            self._cached_suggestions = []
            return

        try:
            response = await self._api_controller.search_users(email_or_name=query)
            # API controller returns APIControllerResponse with result containing suggestions list
            if response and response.success and response.result:
                # update cached suggestions
                self._cached_suggestions = []
                for user in response.result:
                    main = user.display_name
                    if user.email:
                        main = f'{main}|{user.email}'
                    self._cached_suggestions.append(DropdownItem(main=main, id=user.account_id))

                # trigger dropdown re-evaluation to show the suggestions
                self._handle_target_update()
            else:
                self._cached_suggestions = []
                # TODO remove
                self._cached_suggestions = [
                    DropdownItem("emma stone|emma@alpha.test", id="2"),
                    DropdownItem("liam smith|liam@beta.test", id="3"),
                    DropdownItem("olivia brown|olivia@gamma.test", id="4"),
                    DropdownItem("noah johnson|noah@delta.test", id="5"),
                    DropdownItem("ava williams|ava@epsilon.test", id="6"),
                    DropdownItem("lucas jones|lucas@zeta.test", id="7"),
                    DropdownItem("sophia garcia|sophia@eta.test", id="8"),
                    DropdownItem("mason martinez|mason@theta.test", id="9"),
                    DropdownItem("mia rodriguez|mia@iota.test", id="10"),
                    DropdownItem("ethan lee|ethan@kappa.test", id="11"),
                    DropdownItem("isabella walker|isabella@lambda.test", id="12"),
                    DropdownItem("logan hall|logan@mu.test", id="13"),
                    DropdownItem("charlotte allen|charlotte@nu.test", id="14"),
                    DropdownItem("jacob young|jacob@xi.test", id="15"),
                    DropdownItem("amelia hernandez|amelia@omicron.test", id="16"),
                    DropdownItem("oliver king|oliver@pi.test", id="17"),
                    DropdownItem("harper wright|harper@rho.test", id="18"),
                    DropdownItem("elijah lopez|elijah@sigma.test", id="19"),
                    DropdownItem("evelyn hill|evelyn@tau.test", id="20"),
                    DropdownItem("avery scott|avery@upsilon.test", id="21"),
                    DropdownItem("benjamin green|benjamin@phi.test", id="22"),
                    DropdownItem("zoe adams|zoe@chi.test", id="23"),
                    DropdownItem("samuel baker|samuel@psi.test", id="24"),
                    DropdownItem("hannah nelson|hannah@omega.test", id="25"),
                    DropdownItem("henry clark|henry@alpha2.test", id="26"),
                    DropdownItem("lily moore|lily@beta2.test", id="27"),
                    DropdownItem("alexander rivera|alex@gamma2.test", id="28"),
                    DropdownItem("scarlett reyes|scarlett@delta2.test", id="29"),
                    DropdownItem("sebastian cook|sebastian@epsilon2.test", id="30"),
                    DropdownItem("nora morgan|nora@zeta2.test", id="31"),
                    DropdownItem("julian bell|julian@eta2.test", id="32"),
                    DropdownItem("ella cooper|ella@theta2.test", id="33"),
                    DropdownItem("levi murphy|levi@iota2.test", id="34"),
                    DropdownItem("penelope bailey|penelope@kappa2.test", id="35"),
                    DropdownItem("owen rivera|owen@lambda2.test", id="36"),
                    DropdownItem("addison sanders|addison@mu2.test", id="37"),
                    DropdownItem("mateo price|mateo@nu2.test", id="38"),
                    DropdownItem("clara long|clara@xi2.test", id="39"),
                    DropdownItem("ryan foster|ryan@omicron2.test", id="40"),
                    DropdownItem("violet wagner|violet@pi2.test", id="41"),
                    DropdownItem("david stanley|david@rho2.test", id="42"),
                    DropdownItem("grace watts|grace@sigma2.test", id="43"),
                    DropdownItem("nicholas perez|nick@tau2.test", id="44"),
                    DropdownItem("aria cole|aria@upsilon2.test", id="45"),
                    DropdownItem("carter ross|carter@phi2.test", id="46"),
                    DropdownItem("zachary reid|zach@chi2.test", id="47"),
                    DropdownItem("madison cruz|madison@psi2.test", id="48"),
                    DropdownItem("wyatt hughes|wyatt@omega2.test", id="49"),
                    DropdownItem("luna ford|luna@alpha3.test", id="50"),

                ]
        except Exception as e:
            logger.error(f'Error fetching Jira users with the given query: {query} - {e}', exc_info=True)
            self._cached_suggestions = []

    def should_show_dropdown(self, search_string: str) -> bool:
        if self.option_list.option_count == 1:
            first_option = self.option_list.get_option_at_index(0).prompt
            from rich.text import Text

            text_from_option = (
                first_option.plain if isinstance(first_option, Text) else first_option
            )
            return text_from_option != search_string
        return True

    def apply_completion(self, value: str, state: TargetState) -> None:
        if '|' in value:
            value = value.split('|', 1)[0]
        super().apply_completion(value, state)
        self.target.account_id = self.option_list.highlighted_option.id
