from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest
from textual.widgets import Select

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.exceptions import UpdateWorkItemException, ValidationError
from jiratui.models import (
    Attachment,
    IssuePriority,
    IssueStatus,
    IssueType,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraSprint,
    JiraUser,
    Project,
    TimeTracking,
)
from jiratui.widgets.commons import FieldMode
from jiratui.widgets.commons.adf import ADFTextAreaWidget
from jiratui.widgets.commons.base import MultiUserPickerAutoComplete
from jiratui.widgets.commons.users import JiraUserInput, UsersAutoComplete
from jiratui.widgets.commons.widgets import (
    DateInputWidget,
    MultiUserPickerWidget,
    NumericInputWidget,
    SingleUserPickerWidget,
)
from jiratui.widgets.screens import WorkItemSearchResult
from jiratui.widgets.work_item_details.details import IssueDetailsWidget
from jiratui.widgets.work_item_details.fields import (
    IssueDetailsPrioritySelection,
    IssueDetailsStatusSelection,
    WorkItemDetailsDueDate,
)
from jiratui.widgets.work_item_details.flag_work_item import FlagWorkItemScreen
from jiratui.widgets.work_item_details.work_log import LogWorkScreen, WorkItemWorkLogScreen


@pytest.fixture
def jira_issue() -> JiraIssue:
    return JiraIssue(
        id='2',
        key='key-2',
        summary='qwerty',
        status=IssueStatus(name='Done', id='3'),
        issue_type=IssueType(id='2', name='Bug'),
        project=Project(id='1', name='Project 1', key='P1'),
        parent_issue_key='P2',
        created=datetime(2025, 10, 11),
        updated=datetime(2025, 10, 11),
        due_date=datetime(2025, 10, 12),
        resolution_date=datetime(2025, 10, 11),
        priority=IssuePriority(id='1', name='Medium'),
        assignee=JiraUser(account_id='2', display_name='Homer Simpson', active=True),
        reporter=JiraUser(account_id='1', display_name='Bart Simpson', active=True),
        resolution='this was done',
        sprint=JiraSprint(id='5', name='This Sprint', active=True),
        edit_meta={
            'fields': {
                'summary': {
                    'required': True,
                    'schema': {'type': 'string', 'system': 'summary'},
                    'name': 'Summary',
                    'key': 'summary',
                    'operations': ['set'],
                },
                'customfield_10021': {
                    'required': False,
                    'schema': {
                        'type': 'array',
                        'items': 'option',
                        'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                        'customId': 10021,
                    },
                    'name': 'Flagged',
                    'key': 'customfield_10021',
                    'operations': ['add', 'set', 'remove'],
                    'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
                },
                'priority': {
                    'required': False,
                    'schema': {'type': 'priority', 'system': 'priority'},
                    'name': 'Priority',
                    'key': 'priority',
                    'operations': ['set'],
                    'allowedValues': [{'name': 'Medium', 'id': '1'}],
                },
                'assignee': {'name': 'Assignee', 'key': 'assignee', 'operations': ['set']},
                'duedate': {
                    'required': False,
                    'schema': {'type': 'date', 'system': 'duedate'},
                    'name': 'Due date',
                    'key': 'duedate',
                    'operations': ['set'],
                },
                'parent': {
                    'required': False,
                    'schema': {'type': 'issuelink', 'system': 'parent'},
                    'name': 'Parent',
                    'key': 'parent',
                    'hasDefaultValue': False,
                    'operations': ['set'],
                },
                'reporter': {
                    'required': True,
                    'schema': {'type': 'user', 'system': 'reporter'},
                    'name': 'Reporter',
                    'key': 'reporter',
                    'autoCompleteUrl': 'https://jiratuicli.atlassian.net/rest/api/3/user/recommend?context=Reporter&issueKey=JT-21',
                    'operations': ['set'],
                },
                'labels': {
                    'required': False,
                    'schema': {'type': 'array', 'items': 'string', 'system': 'labels'},
                    'name': 'Labels',
                    'key': 'labels',
                    'autoCompleteUrl': 'https://jiratuicli.atlassian.net/rest/api/1.0/labels/10682/suggest?query=',
                    'operations': ['add', 'set', 'remove'],
                },
            }
        },
        attachments=[
            Attachment(
                id='1',
                filename='file-one.csv',
                mime_type='text/csv',
                size=10,
                created=datetime(2025, 10, 11),
                author=JiraUser(
                    account_id='12345',
                    active=True,
                    display_name='Bart',
                    email='bart@simpson.com',
                    username='bart',
                ),
            ),
            Attachment(
                id='2',
                filename='file-two.txt',
                mime_type='text/plain',
                size=10,
                created=datetime(2025, 10, 11),
                author=JiraUser(
                    account_id='12345',
                    active=True,
                    display_name='Bart',
                    email='bart@simpson.com',
                    username='bart',
                ),
            ),
            Attachment(
                id='3',
                filename='file-three.xml',
                mime_type='application/xml',
                size=10,
                created=datetime(2025, 10, 11),
                author=JiraUser(
                    account_id='12345',
                    active=True,
                    display_name='Bart',
                    email='bart@simpson.com',
                    username='bart',
                ),
            ),
            Attachment(
                id='4',
                filename='file-four.md',
                mime_type='text/markdown',
                size=10,
                created=datetime(2025, 10, 11),
                author=JiraUser(
                    account_id='12345',
                    active=True,
                    display_name='Bart',
                    email='bart@simpson.com',
                    username='bart',
                ),
            ),
            Attachment(
                id='5',
                filename='file-five.abc',
                mime_type='text/abc',
                size=10,
                created=datetime(2025, 10, 11),
                author=JiraUser(
                    account_id='12345',
                    active=True,
                    display_name='Bart',
                    email='bart@simpson.com',
                    username='bart',
                ),
            ),
        ],
    )


@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_users_by_issue_key(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        get_issue_mock.return_value = APIControllerResponse(
            result=JiraIssueSearchResponse(issues=[jira_issues[1]])
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.resize_terminal(600, 400)
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('right')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('q')
        await pilot.press('w')
        await pilot.press('r')
        # THEN
        assert isinstance(main_screen.focused, JiraUserInput)
        assert main_screen.focused.id == 'edit-work-item-input-assignee'
        assert main_screen.search_results_table.focus()
        assert main_screen.search_results_table.page == 1
        search_work_items_mock.assert_called_once()
        assert main_screen.search_results_table.search_results == JiraIssueSearchResponse(
            issues=jira_issues, next_page_token=None, is_last=None
        )
        assert main_screen.search_results_table.current_work_item_key == 'key-2'
        search_users_assignable_to_issue_mock.assert_called_once_with(
            issue_key='key-2', query='qwr'
        )


@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_select_and_display_work_item(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        get_issue_mock.return_value = APIControllerResponse(
            result=JiraIssueSearchResponse(issues=[jira_issues[1]])
        )
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('right')
        await pilot.press('tab')
        # THEN
        assert main_screen.search_results_table.focus()
        assert main_screen.search_results_table.page == 1
        search_work_items_mock.assert_called_once()
        assert main_screen.search_results_table.search_results == JiraIssueSearchResponse(
            issues=jira_issues, next_page_token=None, is_last=None
        )
        assert main_screen.search_results_table.current_work_item_key == 'key-2'
        focused_widget = main_screen.focused
        assert isinstance(focused_widget, IssueDetailsWidget)
        assert focused_widget.issue_key_field.value == 'key-2'
        assert focused_widget.issue_summary_field.value == 'qwerty'
        assert focused_widget.project_id_field.value == '(P1) Project 1'
        assert focused_widget.issue_created_date_field.value == '2025-10-11 00:00'
        assert focused_widget.issue_created_date_field.value == '2025-10-11 00:00'
        assert focused_widget.issue_due_date_field.value == '2025-10-12'
        assert focused_widget.issue_resolution_date_field.value == '2025-10-11 00:00'
        assert focused_widget.issue_parent_field.value == 'P2'
        assert focused_widget.issue_type_field.value == 'Bug'
        assert focused_widget.priority_selector.selection == '1'
        assert focused_widget.reporter_selector.value == 'Bart Simpson'
        assert focused_widget.assignee_selector.value == ''
        assert focused_widget.issue_resolution_field.value == 'this was done'
        assert focused_widget.issue_sprint_field.value == 'This Sprint'


@pytest.mark.parametrize('edit_metadata', [None, {'fields': {}}, {'fields': None}])
@pytest.mark.asyncio
async def test_determine_editable_fields_without_edit_metadata(
    edit_metadata, jira_issue, app: JiraApp
):
    # GIVEN
    jira_issue.edit_meta = edit_metadata
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()

        # WHEN
        result = details_widget._determine_editable_fields(jira_issue)
        # THEN
        assert result == {}


@pytest.mark.asyncio
async def test_determine_editable_fields(jira_issue, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        result = details_widget._determine_editable_fields(jira_issue)
        # THEN
        assert result == {
            'summary': True,
            'assignee': True,
            'priority': True,
            'customfield_10021': True,
            'parent': True,
            'duedate': True,
            'reporter': True,
            'labels': True,
        }


@pytest.mark.asyncio
async def test_determine_editable_fields_item_without_parent(jira_issue, app: JiraApp):
    # GIVEN
    jira_issue.issue_type.hierarchy_level = 1
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        result = details_widget._determine_editable_fields(jira_issue)
        # THEN
        assert result['parent'] is False


@pytest.mark.asyncio
async def test_determine_editable_fields_item_with_possible_parent(jira_issue, app: JiraApp):
    # GIVEN
    jira_issue.issue_type.hierarchy_level = 2
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        result = details_widget._determine_editable_fields(jira_issue)
        # THEN
        assert result['parent'] is True


@patch.object(APIController, 'get_project_statuses')
@pytest.mark.asyncio
async def test_retrieve_applicable_status_codes_success_false(
    get_project_statuses_mock: AsyncMock, app: JiraApp
):
    # GIVEN
    get_project_statuses_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        await details_widget._retrieve_applicable_status_codes(
            'P1', work_item_type_id='2', current_status_id='3'
        )
        # THEN
        assert details_widget.issue_status_selector.is_blank()
        assert details_widget.issue_status_selector._options == [('', Select.NULL)]


@patch.object(APIController, 'get_project_statuses')
@pytest.mark.asyncio
async def test_retrieve_applicable_status_codes_success_without_current_status_id(
    get_project_statuses_mock: AsyncMock, app: JiraApp
):
    # GIVEN
    get_project_statuses_mock.return_value = APIControllerResponse(
        result={
            '2': {
                'issue_type_name': 'Task',
                'issue_type_statuses': [IssueStatus(id='5', name='Done')],
            }
        }
    )
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        await details_widget._retrieve_applicable_status_codes(
            'P1', work_item_type_id='2', current_status_id='5'
        )
        # THEN
        assert details_widget.issue_status_selector.selection == '5'


@pytest.mark.asyncio
async def test_build_payload_for_update_nothing_to_update(app: JiraApp):
    # GIVEN
    app.config.enable_updating_additional_fields = False
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@pytest.mark.asyncio
async def test_build_payload_for_update_nothing_to_update_update_additional_fields_enabled(
    app: JiraApp,
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_summary_changed(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = False
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        issue_mock.return_value = jira_issue
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = True
        details_widget.issue_summary_field.value = 'v2'
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {'summary': 'v2'}


@patch('jiratui.widgets.work_item_details.details.IssueDetailsWidget.issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_summary_unchanged(issue_mock: Mock, app: JiraApp):
    # GIVEN
    app.config.enable_updating_additional_fields = False
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(summary='qwerty')
        details_widget.issue_summary_field.update_enabled = True
        details_widget.issue_summary_field.value = 'qwerty'
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(WorkItemDetailsDueDate, 'value_has_changed', PropertyMock(return_value=False))
@pytest.mark.asyncio
async def test_build_payload_for_update_with_duedate_unchanged(app: JiraApp):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = True
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(WorkItemDetailsDueDate, 'value_has_changed', PropertyMock(return_value=True))
@pytest.mark.asyncio
async def test_build_payload_for_update_with_duedate_changed(app: JiraApp):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = True
        details_widget.issue_due_date_field.get_value_for_update = Mock(return_value='2026-10-10')  # type:ignore[method-assign]
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {'duedate': '2026-10-10'}


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_priority_unchanged(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.return_value = jira_issue
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = True
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_priority_changed_without_priority_selection(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.return_value = jira_issue
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = True
        details_widget.priority_selector.value = Select.NULL
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_priority_changed_with_priority_selection(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.return_value = jira_issue
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = True
        details_widget.priority_selector.set_options([('High', '1')])
        details_widget.priority_selector.value = '1'
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {'priority': '1'}


@patch('jiratui.widgets.work_item_details.details.IssueDetailsWidget.issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_parent_unchanged(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        issue_mock.configure_mock(parent_issue_key='P2')
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = True
        details_widget.issue_parent_field.value = 'P2'
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_parent_changed(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        issue_mock.return_value = jira_issue
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = True
        details_widget.issue_parent_field.value = 'WI-1'
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {'parent': 'WI-1'}


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value='2'))
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_assignee_unchanged(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(assignee=jira_issue.assignee)
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = True
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value='99'))
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_assignee_changed(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(assignee=jira_issue.assignee)
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = True
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {'assignee_account_id': '99'}


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value='99'))
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_reporter_changed(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(reporter=jira_issue.reporter)
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = True
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert jira_issue.reporter.account_id == '1'
        assert payload == {'reporter': '99'}


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value=None))
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_reporter_missing(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(reporter=jira_issue.reporter)
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = True
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload is None


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value='1'))
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_reporter_unchanged(
    issue_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(reporter=jira_issue.reporter)
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = True
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert jira_issue.reporter.account_id == '1'
        assert payload == {}


@pytest.mark.parametrize(
    'labels, expected_labels',
    [
        ('test1,test2', ['test1', 'test2']),
        ('test2', ['test2']),
    ],
)
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_labels_changed(
    issue_mock: Mock, labels, expected_labels, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(labels=['test1'])
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = True
        details_widget.work_item_labels_widget.value = labels
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {'labels': expected_labels}


@pytest.mark.parametrize(
    'new_labels, current_labels',
    [
        ('test1,test2', ['test1', 'test2']),
        ('Test2', ['test2']),
        ('Test2, test3 ', ['test2', 'test3']),
    ],
)
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_build_payload_for_update_with_labels_unchanged(
    issue_mock: Mock, new_labels, current_labels, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(labels=current_labels)
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = True
        details_widget.work_item_labels_widget.value = new_labels
        await details_widget.dynamic_fields_widgets_container.remove_children()

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(NumericInputWidget, 'value_has_changed', PropertyMock(return_value=False))
@pytest.mark.asyncio
async def test_build_payload_for_update_update_additional_fields_enabled_numeric_field_value_unchanged(
    app: JiraApp,
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()
        await details_widget.dynamic_fields_widgets_container.mount(
            NumericInputWidget(mode=FieldMode.UPDATE, field_id='a', jira_field_key='a')
        )

        # WHEN
        payload = details_widget._build_payload_for_update()
        # THEN
        assert payload == {}


@patch.object(NumericInputWidget, 'value_has_changed', PropertyMock(return_value=True))
@pytest.mark.asyncio
async def test_build_payload_for_update_update_additional_fields_enabled_numeric_field_value_changed(
    app: JiraApp,
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()
        await details_widget.dynamic_fields_widgets_container.mount(
            NumericInputWidget(mode=FieldMode.UPDATE, field_id='field_a', jira_field_key='field_a')
        )

        # WHEN
        with patch.object(NumericInputWidget, 'get_value_for_update') as m:
            m.return_value = 1.2
            payload = details_widget._build_payload_for_update()
            # THEN
            assert payload == {'field_a': 1.2}


@patch.object(NumericInputWidget, 'value_has_changed', PropertyMock(return_value=True))
@pytest.mark.asyncio
async def test_build_payload_for_update_update_additional_fields_enabled_numeric_field_value_changed_to_none(
    app: JiraApp,
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()
        await details_widget.dynamic_fields_widgets_container.mount(
            NumericInputWidget(mode=FieldMode.UPDATE, field_id='field_a', jira_field_key='field_a')
        )

        # WHEN
        with patch.object(NumericInputWidget, 'get_value_for_update') as m:
            m.return_value = None
            payload = details_widget._build_payload_for_update()
            # THEN
            assert payload == {}


@pytest.mark.parametrize(
    'value_for_update, expected_value', [('2026-01-10', '2026-01-10'), (None, None)]
)
@patch.object(DateInputWidget, 'value_has_changed', PropertyMock(return_value=True))
@pytest.mark.asyncio
async def test_build_payload_for_update_update_additional_fields_enabled_non_numeric_field_value_changed(
    value_for_update, expected_value, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget.issue_summary_field.update_enabled = False
        details_widget.issue_due_date_field.update_enabled = False
        details_widget.priority_selector.update_enabled = False
        details_widget.issue_parent_field.update_enabled = False
        details_widget.assignee_selector.update_enabled = False
        details_widget.reporter_selector.update_enabled = False
        details_widget.work_item_labels_widget.update_enabled = False
        await details_widget.dynamic_fields_widgets_container.remove_children()
        await details_widget.dynamic_fields_widgets_container.mount(
            DateInputWidget(mode=FieldMode.UPDATE, field_id='field_a', jira_field_key='field_a')
        )

        # WHEN
        with patch.object(DateInputWidget, 'get_value_for_update') as m:
            m.return_value = value_for_update
            payload = details_widget._build_payload_for_update()
            # THEN
            assert payload == {'field_a': expected_value}


@pytest.mark.parametrize(
    'key, widget',
    [
        ('x', JiraUserInput),
        ('y', IssueDetailsPrioritySelection),
        ('z', IssueDetailsStatusSelection),
    ],
)
@pytest.mark.asyncio
async def test_action_focus_widget(key: str, widget, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        details_widget.action_focus_widget(key)
        # THEN
        assert isinstance(app.screen.focused, widget)


@pytest.mark.asyncio
async def test_clear_form(app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        details_widget.clear_form = True
        # THEN
        assert details_widget._work_item_key is None
        assert details_widget.issue_summary_field.value == ''
        assert details_widget.issue_parent_field.value == ''
        assert details_widget.issue_resolution_field.value == ''
        assert details_widget.issue_resolution_date_field.value == ''
        assert details_widget.issue_last_update_date_field.value == ''
        assert details_widget.issue_key_field.value == ''
        assert details_widget.project_id_field.value == ''
        assert details_widget.issue_type_field.value == ''
        assert details_widget.issue_sprint_field.value == ''
        assert details_widget.issue_status_selector.selection is None
        assert details_widget.assignee_selector.value == ''
        assert details_widget.assignee_selector.account_id is None
        assert details_widget.reporter_selector.value == ''
        assert details_widget.reporter_selector.account_id is None
        assert details_widget.priority_selector.selection is None
        assert details_widget.priority_selector.update_enabled is True
        assert details_widget.issue_due_date_field.original_value is None
        assert details_widget.work_item_labels_widget.value == ''
        assert details_widget._work_item_is_flagged is None
        assert details_widget._issue_supports_flagging is True
        assert details_widget.work_item_flag_widget.show is False


@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_without_payload(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.return_value = jira_issue
        build_payload_for_update_mock.return_value = None
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_not_called()


@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_without_payload_issue_not_require_transition(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(status=IssueStatus(id='5', name='Open'))
        build_payload_for_update_mock.return_value = {}
        details_widget.issue_status_selector.set_options([('Done', '5')])
        details_widget.issue_status_selector.value = '5'
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_not_called()
        transition_issue_status_mock.assert_not_called()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_without_payload_issue_requires_transition(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    refresh_work_item_details_mock: Mock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(status=IssueStatus(id='1', name='Open'), key=jira_issue.key)
        build_payload_for_update_mock.return_value = {}
        details_widget.issue_status_selector.set_options([('Done', '5')])
        details_widget.issue_status_selector.value = '5'
        transition_issue_status_mock.return_value = APIControllerResponse()
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_not_called()
        transition_issue_status_mock.assert_called_once_with('key-2', '5')
        refresh_work_item_details_mock.assert_called_once()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_without_payload_issue_requires_transition_transition_fails(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    refresh_work_item_details_mock: Mock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(status=IssueStatus(id='1', name='Open'), key=jira_issue.key)
        build_payload_for_update_mock.return_value = {}
        details_widget.issue_status_selector.set_options([('Done', '5')])
        details_widget.issue_status_selector.value = '5'
        transition_issue_status_mock.return_value = APIControllerResponse(success=False)
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_not_called()
        transition_issue_status_mock.assert_called_once_with('key-2', '5')
        refresh_work_item_details_mock.assert_not_called()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_with_payload_issue_not_require_transition_updates_issue(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    refresh_work_item_details_mock: Mock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(status=IssueStatus(id='5', name='Open'))
        build_payload_for_update_mock.return_value = {'a': 1}
        details_widget.issue_status_selector.set_options([('Done', '5')])
        details_widget.issue_status_selector.value = '5'
        update_issue_mock.return_value = APIControllerResponse()
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_called_once_with(issue_mock, {'a': 1})
        transition_issue_status_mock.assert_not_called()
        refresh_work_item_details_mock.assert_called_once()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_with_payload_issue_not_require_transition_fails_issue_update(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    refresh_work_item_details_mock: Mock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(status=IssueStatus(id='5', name='Open'))
        build_payload_for_update_mock.return_value = {'a': 1}
        details_widget.issue_status_selector.set_options([('Done', '5')])
        details_widget.issue_status_selector.value = '5'
        update_issue_mock.return_value = APIControllerResponse(success=False)
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_called_once_with(issue_mock, {'a': 1})
        transition_issue_status_mock.assert_not_called()
        refresh_work_item_details_mock.assert_not_called()


@pytest.mark.parametrize('exception_type', [UpdateWorkItemException, ValidationError, ValueError])
@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch.object(APIController, 'transition_issue_status')
@patch.object(APIController, 'update_issue')
@patch.object(IssueDetailsWidget, '_build_payload_for_update')
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_save_work_item_with_payload_issue_not_require_transition_fails_with_error(
    issue_mock: Mock,
    build_payload_for_update_mock: Mock,
    update_issue_mock: AsyncMock,
    transition_issue_status_mock: AsyncMock,
    refresh_work_item_details_mock: Mock,
    exception_type,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(status=IssueStatus(id='5', name='Open'))
        build_payload_for_update_mock.return_value = {'a': 1}
        details_widget.issue_status_selector.set_options([('Done', '5')])
        details_widget.issue_status_selector.value = '5'
        update_issue_mock.side_effect = exception_type()
        # WHEN
        await details_widget.action_save_work_item()
        # THEN
        update_issue_mock.assert_called_once_with(issue_mock, {'a': 1})
        transition_issue_status_mock.assert_not_called()
        refresh_work_item_details_mock.assert_not_called()


@pytest.mark.asyncio
async def test_watch_issue(jira_issue, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        result = details_widget.watch_issue(None)  # type:ignore[func-returns-value]
        # THEN
        assert result is None


@patch.object(IssueDetailsWidget, '_setup_time_tracking')
@patch.object(IssueDetailsWidget, '_add_dynamic_widgets')
@patch.object(IssueDetailsWidget, '_determine_issue_flagged_status')
@patch.object(IssueDetailsWidget, '_determine_editable_fields')
@patch.object(APIController, 'get_project_statuses')
@pytest.mark.asyncio
async def test_watch_issue_with_valid_issue(
    get_project_statuses_mock: AsyncMock,
    determine_editable_fields_mock: Mock,
    determine_issue_flagged_status_mock: Mock,
    add_dynamic_widgets_mock: Mock,
    setup_time_tracking_mock: Mock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    app.config.enable_updating_additional_fields = False
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        get_project_statuses_mock.return_value = APIControllerResponse(
            result={'2': {'issue_type_statuses': [IssueStatus(id='3', name='Done')]}}
        )
        determine_editable_fields_mock.return_value = {
            'assignee': True,
            'reporter': True,
            'parent': True,
            'summary': True,
            'duedate': True,
        }
        # WHEN
        details_widget.watch_issue(jira_issue)
        await pilot.pause()
        # THEN
        get_project_statuses_mock.assert_called_once_with('P1')
        determine_editable_fields_mock.assert_called_once()
        assert details_widget.assignee_selector.account_id == '2'
        assert details_widget.assignee_selector.update_enabled is True
        assert details_widget.reporter_selector.account_id == '1'
        assert details_widget.reporter_selector.update_enabled is True
        assert details_widget.issue_resolution_date_field.value == '2025-10-11 00:00'
        assert details_widget.issue_resolution_field.value == 'this was done'
        assert details_widget.issue_last_update_date_field.value == '2025-10-11 00:00'
        assert details_widget.issue_created_date_field.value == '2025-10-11 00:00'
        assert details_widget.issue_key_field.value == 'key-2'
        assert details_widget.project_id_field.value == '(P1) Project 1'
        assert details_widget.issue_type_field.value == 'Bug'
        assert details_widget.issue_parent_field.value == 'P2'
        assert details_widget.issue_parent_field.update_enabled is True
        assert details_widget.issue_sprint_field.value == 'This Sprint'
        assert details_widget.issue_summary_field.value == 'qwerty'
        assert details_widget.issue_summary_field.update_enabled is True
        assert details_widget.issue_due_date_field.value == '2025-10-12'
        assert details_widget.issue_due_date_field.update_enabled is True
        assert details_widget.work_item_labels_widget.value == ''
        assert details_widget.priority_selector.update_enabled is True
        determine_issue_flagged_status_mock.assert_called_once()
        setup_time_tracking_mock.assert_called_once()
        add_dynamic_widgets_mock.assert_not_called()


@patch.object(IssueDetailsWidget, '_setup_time_tracking')
@patch.object(IssueDetailsWidget, '_add_dynamic_widgets')
@patch.object(IssueDetailsWidget, '_determine_issue_flagged_status')
@patch.object(IssueDetailsWidget, '_determine_editable_fields')
@patch.object(APIController, 'get_project_statuses')
@pytest.mark.asyncio
async def test_watch_issue_with_valid_issue_alternative_values(
    get_project_statuses_mock: AsyncMock,
    determine_editable_fields_mock: Mock,
    determine_issue_flagged_status_mock: Mock,
    add_dynamic_widgets_mock: Mock,
    setup_time_tracking_mock: Mock,
    jira_issue,
    app: JiraApp,
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        get_project_statuses_mock.return_value = APIControllerResponse(
            result={'2': {'issue_type_statuses': [IssueStatus(id='3', name='Done')]}}
        )
        determine_editable_fields_mock.return_value = {
            'assignee': True,
            'reporter': True,
            'parent': True,
            'summary': True,
            'duedate': True,
        }
        jira_issue.assignee = None
        jira_issue.reporter = None
        jira_issue.resolution_date = None
        jira_issue.resolution = None
        jira_issue.updated = None
        # WHEN
        details_widget.watch_issue(jira_issue)
        await pilot.pause()
        # THEN
        get_project_statuses_mock.assert_called_once_with('P1')
        determine_editable_fields_mock.assert_called_once()
        assert details_widget.assignee_selector.account_id is None
        assert details_widget.assignee_selector.update_enabled is True
        assert details_widget.reporter_selector.account_id is None
        assert details_widget.reporter_selector.update_enabled is True
        assert details_widget.issue_resolution_date_field.value == ''
        assert details_widget.issue_resolution_field.value == ''
        assert details_widget.issue_last_update_date_field.value == ''
        add_dynamic_widgets_mock.assert_called_once()


@patch('jiratui.widgets.work_item_details.details.create_dynamic_widgets_for_updating_work_item')
@pytest.mark.asyncio
async def test_add_dynamic_widgets_no_widgets_to_add(
    create_dynamic_widgets_for_updating_work_item_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    app.config.update_additional_fields_ignore_ids = []
    create_dynamic_widgets_for_updating_work_item_mock.return_value = []
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        await details_widget._add_dynamic_widgets(jira_issue)
        # THEN
        assert details_widget.dynamic_fields_widgets_container.is_empty is True


@patch('jiratui.widgets.work_item_details.details.create_dynamic_widgets_for_updating_work_item')
@pytest.mark.asyncio
async def test_add_dynamic_widgets(
    create_dynamic_widgets_for_updating_work_item_mock: Mock, jira_issue, app: JiraApp
):
    # GIVEN
    app.config.enable_updating_additional_fields = True
    app.config.update_additional_fields_ignore_ids = []
    widget_2 = MultiUserPickerWidget(
        mode=FieldMode.UPDATE, field_id='approvers', jira_field_key='approvers'
    )
    widget_4 = SingleUserPickerWidget(mode=FieldMode.UPDATE, field_id='user', jira_field_key='user')
    create_dynamic_widgets_for_updating_work_item_mock.return_value = [
        ADFTextAreaWidget(mode=FieldMode.UPDATE, field_id='environment'),
        widget_2,
        NumericInputWidget(mode=FieldMode.UPDATE, field_id='score', jira_field_key='score'),
        widget_4,
        MultiUserPickerAutoComplete(widget_2, app.api),
        UsersAutoComplete(widget_4, app.api),
    ]
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        await details_widget._add_dynamic_widgets(jira_issue)
        # THEN
        assert details_widget.dynamic_fields_widgets_container.is_empty is False
        children = list(details_widget.dynamic_fields_widgets_container.children)
        assert isinstance(children[0], MultiUserPickerWidget)
        assert isinstance(children[1], SingleUserPickerWidget)
        assert isinstance(children[2], NumericInputWidget)
        assert isinstance(children[3], MultiUserPickerAutoComplete)
        assert isinstance(children[4], UsersAutoComplete)
        assert isinstance(children[5], ADFTextAreaWidget)


@pytest.mark.asyncio
async def test_static_widgets_css_classes(jira_issue, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        assert 'issue_details_input_field' in details_widget.issue_summary_field.classes
        assert 'issue_details_input_field' in details_widget.issue_key_field.classes
        assert 'work-item-key' in details_widget.issue_key_field.classes
        assert 'issue_details_input_field' in details_widget.issue_sprint_field.classes
        assert 'issue_details_input_field' in details_widget.issue_parent_field.classes
        assert 'work-item-key' in details_widget.issue_parent_field.classes
        assert 'issue_details_input_field' in details_widget.project_id_field.classes
        assert 'issue_details_input_field' in details_widget.issue_created_date_field.classes
        assert 'input-date' in details_widget.issue_created_date_field.classes
        assert 'issue_details_input_field' in details_widget.issue_last_update_date_field.classes
        assert 'input-date' in details_widget.issue_last_update_date_field.classes
        assert 'input-date' in details_widget.issue_due_date_field.classes
        assert 'issue_details_input_field' in details_widget.issue_resolution_date_field.classes
        assert 'input-date' in details_widget.issue_resolution_date_field.classes
        assert 'issue_details_input_field' in details_widget.issue_resolution_field.classes
        assert 'issue_details_input_field' in details_widget.work_item_labels_widget.classes


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_action_flag_work_item_opens_modal_screen(issue_mock: Mock, jira_issue, app: JiraApp):
    # GIVEN
    issue_mock.configure_mock(key=jira_issue.key)
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget._issue_supports_flagging = True
        # WHEN
        details_widget.action_flag_work_item()
        # THEN
        assert isinstance(app.screen, FlagWorkItemScreen)


@pytest.mark.parametrize(
    'work_item_key, issue_supports_flagging',
    [
        ('', True),
        ('key-3', False),
    ],
)
@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_action_flag_work_item_does_not_open_modal_screen(
    issue_mock: Mock, work_item_key: str, issue_supports_flagging: bool, app: JiraApp
):
    # GIVEN
    issue_mock.configure_mock(key=work_item_key)
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        details_widget._issue_supports_flagging = False
        # WHEN
        details_widget.action_flag_work_item()
        # THEN
        assert not isinstance(app.screen, FlagWorkItemScreen)


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_action_view_worklog(issue_mock: Mock, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        details_widget.action_view_worklog()
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)


@pytest.mark.asyncio
async def test_action_view_worklog_no_issue_set(app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        details_widget.action_view_worklog()
        # THEN
        assert not isinstance(app.screen, WorkItemWorkLogScreen)


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_action_log_work(issue_mock: Mock, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(key='key-2', time_tracking=None)
        # WHEN
        details_widget.action_log_work()
        # THEN
        assert isinstance(app.screen, LogWorkScreen)
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._current_remaining_estimate is None


@patch.object(IssueDetailsWidget, 'issue')
@pytest.mark.asyncio
async def test_action_log_work_with_time_remaining(issue_mock: Mock, app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        issue_mock.configure_mock(key='key-2', time_tracking=TimeTracking(remaining_estimate='1h'))
        # WHEN
        details_widget.action_log_work()
        # THEN
        assert isinstance(app.screen, LogWorkScreen)
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._current_remaining_estimate == '1h'


@pytest.mark.asyncio
async def test_action_log_work_no_issue_set(app: JiraApp):
    # GIVEN
    async with app.run_test() as pilot:
        details_widget = IssueDetailsWidget()
        await app.mount(details_widget)
        await pilot.pause()
        # WHEN
        details_widget.action_log_work()
        # THEN
        assert not isinstance(app.screen, LogWorkScreen)
