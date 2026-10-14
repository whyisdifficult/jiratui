from textual import on
from textual.app import ComposeResult
from textual.containers import ItemGrid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Select, Static

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.models import JiraIssue, LinkIssueType
from jiratui.widgets.commons import FieldMode
from jiratui.widgets.commons.base import WorkItemKeyAutoComplete
from jiratui.widgets.commons.widgets import TextInputWidget


class LinkedWorkItemKey(TextInputWidget):
    """A custom Input widget for entering the key of a work item."""

    def __init__(self, value: str | None = None):
        super().__init__(
            mode=FieldMode.CREATE,
            field_id='related_key',
            jira_field_key='related_key',
            title='Work Item Key',
            required=True,
            placeholder='Type to search items...',
        )
        self.value = value.strip() if value is not None else ''
        self.compact = True
        self.tooltip = 'Type to search items...'
        self.field_supports_update = 1

    @on(Input.Blurred)
    def clean_value(self, event: Input.Blurred) -> None:
        if event.value is not None:
            self.value = event.value.strip().replace(' ', '')


class IssueLinkTypeSelector(Select):
    """A custom Select widget for selecting the type of link between 2 items."""

    def __init__(self, items: list[tuple[str, str]]):
        super().__init__(
            options=items,
            prompt='Select a link type',
            name='issue_link_types',
            type_to_search=True,
            compact=True,
        )
        self.valid_empty = False
        self.border_title = 'Link Type'


class AddWorkItemRelationshipScreen(Screen[dict]):
    """A modal screen that allows users to relate 2 work items.

    The screen does not create the relationship between the work items. Instead, it returns the relationship's data
    to the caller via the `dismiss()` call and the caller will proceed to create the relationship via the API.

    The screen sends back the caller the following dictionary:

    ```python
    {
        'right_issue_key': 'WI-123',
        'link_type': 'relates-to',
        'link_type_id': 1,
    }
    ```

    **See Also**:
    - [Relate Work Items Screen Design](#components-add-relationship-between-work-items)
    - [Use Case: Relate Work Items](#use-case-relate-work-items)
    - [Architecture](#architecture-related-work-items-classes)
    """

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
    def linked_work_item_key(self) -> LinkedWorkItemKey:
        return self.query_one(LinkedWorkItemKey)

    @property
    def save_button(self) -> Button:
        return self.query_one('#add-link-button-save', expect_type=Button)

    @property
    def _use_advanced_full_text_search(self) -> bool:
        return self.app.config.enable_advanced_full_text_search  # type:ignore[attr-defined]

    def compose(self) -> ComposeResult:
        vertical = Vertical()
        vertical.border_title = self.title
        with vertical:
            yield Static('')
            with ItemGrid(classes='issue-linking-grid'):
                yield IssueLinkTypeSelector([])
                yield LinkedWorkItemKey()
            yield Static('')
            with ItemGrid(classes='issue-linking-grid-buttons'):
                yield Button('Save', variant='success', id='add-link-button-save', disabled=True)
                yield Button('Cancel', variant='error', id='add-link-button-quit')

    @on(Input.Blurred, 'LinkedWorkItemKey')
    def validate_work_item_key(self):
        value = self.linked_work_item_key.value
        self.save_button.disabled = (
            False if (value and value.strip()) and self.relationship_type.selection else True
        )

    @on(Input.Changed, 'LinkedWorkItemKey')
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
        await self.fetch_issue_link_types()
        work_item_key_autocomplete = WorkItemKeyAutoComplete(
            self.linked_work_item_key,
            self.app.api,  # type:ignore[attr-defined]
            work_items_search_function=self._search_work_items,
        )
        await self.mount(work_item_key_autocomplete)

    async def _search_work_items(self, query: str) -> list[JiraIssue] | None:
        """Searches work items to fill in the autocomplete suggestions for the related work item's key.

        See Also: https://support.atlassian.com/jira-software-cloud/docs/jql-fields/

        Args:
            query: the search term to find work items.

        Returns:
            A list of `JiraIssue` instances or `None` if it fails to search work items.
        """

        if query:
            jql_query = f'summary ~ "{query}" OR description ~ "{query}" OR workItemKey ~ "{query}"'
            if self._use_advanced_full_text_search:
                jql_query = f'text ~ "{query}" OR workItemKey ~ "{query}"'
            response: APIControllerResponse = await self.app.api.search_issues(  # type:ignore[attr-defined]
                jql_query=jql_query, fields=['id', 'key', 'summary']
            )
            if response.success and response.result:
                return response.result.issues
        return None

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
