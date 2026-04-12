from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import IssueType, Project
from jiratui.widgets.commons import UserPickerWidget
from jiratui.widgets.commons.users import JiraUserInput
from jiratui.widgets.commons.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    DescriptionWidget,
    LabelsWidget,
    MultiSelectWidget,
    MultiUserPickerWidget,
    NumericInputWidget,
    SelectionWidget,
    SprintWidget,
    TextInputWidget,
    URLWidget,
)
from jiratui.widgets.create_work_item.factory import create_widgets_for_work_item_creation
from jiratui.widgets.create_work_item.fields import (
    CreateWorkItemIssueSummaryField,
    CreateWorkItemIssueTypeSelectionInput,
    CreateWorkItemProjectSelectionInput,
)
from jiratui.widgets.create_work_item.screen import AddWorkItemScreen


@pytest.fixture
def create_metadata_with_editable_reporter() -> dict:
    """Create metadata response where reporter field is editable."""
    return {
        'fields': [
            {
                'fieldId': 'reporter',
                'name': 'Reporter',
                'required': False,
                'operations': ['set'],  # 'set' operation means field is editable
                'schema': {
                    'type': 'user',
                    'system': 'reporter',
                },
            },
            {
                'fieldId': 'description',
                'name': 'Description',
                'required': False,
                'operations': ['set'],
            },
        ]
    }


@pytest.fixture
def create_metadata_without_editable_reporter() -> dict:
    """Create metadata response where reporter field is NOT editable."""
    return {
        'fields': [
            {
                'fieldId': 'reporter',
                'name': 'Reporter',
                'required': False,
                'operations': [],  # No 'set' operation means field is NOT editable
                'schema': {
                    'type': 'user',
                    'system': 'reporter',
                },
            },
            {
                'fieldId': 'description',
                'name': 'Description',
                'required': False,
                'operations': ['set'],
            },
        ]
    }


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value=None))
@patch.object(APIController, 'get_user')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    get_user_mock: AsyncMock,
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_not_called()
        get_user_mock.assert_not_called()


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value=None))
@patch.object(APIController, 'get_issue_create_metadata')
@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'search_users')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen_search_assignee_and_reporter(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    search_users_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    get_issue_create_metadata_mock: AsyncMock,
    projects: list[Project],
    issue_types: list[IssueType],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    # GIVEN
    search_projects_mock.return_value = APIControllerResponse(result=projects)
    get_issue_types_for_project_mock.return_value = APIControllerResponse(result=issue_types)
    get_issue_create_metadata_mock.return_value = APIControllerResponse(result=[])
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('s')
        await pilot.press('t')
        await pilot.press('tab')
        await pilot.press('q')
        await pilot.press('w')
        await pilot.press('r')
        await pilot.press('tab')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_called_once_with('P1')
        search_users_mock.assert_called_once_with(email_or_name='tst')
        search_users_assignable_to_issue_mock.assert_called_once_with(
            project_id_or_key='P1', query='qwr'
        )
        get_issue_create_metadata_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value=None))
@patch.object(APIController, 'get_issue_create_metadata')
@patch.object(APIController, 'search_users_assignable_to_issue')
@patch.object(APIController, 'search_users')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen_search_reporter_only(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    search_users_mock: AsyncMock,
    search_users_assignable_to_issue_mock: AsyncMock,
    get_issue_create_metadata_mock: AsyncMock,
    projects: list[Project],
    issue_types: list[IssueType],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    # GIVEN
    search_projects_mock.return_value = APIControllerResponse(result=projects)
    get_issue_types_for_project_mock.return_value = APIControllerResponse(result=issue_types)
    get_issue_create_metadata_mock.return_value = APIControllerResponse(result=[])
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('t')
        await pilot.press('s')
        await pilot.press('t')
        await pilot.press('tab')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_called_once_with('P1')
        search_users_mock.assert_called_once_with(email_or_name='tst')
        search_users_assignable_to_issue_mock.assert_not_called()
        get_issue_create_metadata_mock.assert_called_once()


@patch.object(AddWorkItemScreen, 'reporter_account_id', PropertyMock(return_value='12345'))
@patch.object(APIController, 'get_user')
@patch.object(APIController, 'get_issue_types_for_project')
@patch.object(APIController, 'search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_create_work_item_open_modal_screen_with_reporter_account_id(
    fetch_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    get_issue_types_for_project_mock: AsyncMock,
    get_user_mock: AsyncMock,
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_user_mock.return_value = APIControllerResponse(result=None)
    async with app.run_test() as pilot:
        # WHEN
        await pilot.press('ctrl+n')
        # THEN
        assert isinstance(app.screen, AddWorkItemScreen)
        search_projects_mock.assert_called_once()
        get_issue_types_for_project_mock.assert_not_called()
        get_user_mock.assert_called_once_with('12345')


@patch.object(APIController, 'get_issue_create_metadata')
@pytest.mark.asyncio
async def test_reporter_field_hidden_when_not_editable(
    get_issue_create_metadata_mock: AsyncMock,
    create_metadata_without_editable_reporter,
    app,
):
    """Test that reporter field is hidden when API metadata indicates it's not editable."""
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        result=create_metadata_without_editable_reporter
    )
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='user123')
        await app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Assertions
        assert screen._reporter_is_editable is False, 'Reporter should not be editable'
        assert screen.reporter_selector.display is False, 'Reporter field should be hidden'


@patch.object(APIController, 'get_issue_create_metadata')
@pytest.mark.asyncio
async def test_reporter_field_shown_when_editable(
    get_issue_create_metadata_mock: AsyncMock, app, create_metadata_with_editable_reporter
):
    """Test that reporter field is shown when API metadata indicates it's editable."""
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        result=create_metadata_with_editable_reporter
    )
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='user123')
        await app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Assertions
        assert screen._reporter_is_editable is True, 'Reporter should be editable'
        assert screen.reporter_selector.display is True, 'Reporter field should be shown'


@patch.object(APIController, 'get_issue_create_metadata')
@pytest.mark.asyncio
async def test_validation_skips_reporter_when_not_editable(
    get_issue_create_metadata_mock: AsyncMock, app, create_metadata_without_editable_reporter
):
    """Test that validation does not require reporter field when it's not editable."""
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        result=create_metadata_without_editable_reporter
    )
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()

        # Trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Mock the selection properties to return valid values
        with (
            patch.object(
                type(screen.project_selector), 'selection', new_callable=PropertyMock
            ) as mock_project,
            patch.object(
                type(screen.issue_type_selector), 'selection', new_callable=PropertyMock
            ) as mock_issue_type,
            patch.object(
                type(screen.reporter_selector), 'selection', new_callable=PropertyMock
            ) as mock_reporter,
            patch.object(
                type(screen.summary_field), 'value', new_callable=PropertyMock
            ) as mock_summary,
        ):
            mock_project.return_value = 'TEST'
            mock_issue_type.return_value = 'task-123'
            mock_reporter.return_value = None  # No reporter selected
            mock_summary.return_value = 'Test Summary'

            # Validation should pass even without reporter
            assert screen._validate_required_fields() is True, (
                "Validation should pass without reporter when it's not editable"
            )


@patch.object(APIController, 'get_issue_create_metadata')
@pytest.mark.asyncio
async def test_save_excludes_reporter_when_not_editable(
    get_issue_create_metadata_mock: AsyncMock, app, create_metadata_without_editable_reporter
):
    """Test that save handler does not include reporter field when it's not editable."""
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        result=create_metadata_without_editable_reporter
    )
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()

        # trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Mock dismiss
        screen.dismiss = Mock()

        # Mock the selection and value properties
        with (
            patch.object(
                type(screen.project_selector), 'selection', new_callable=PropertyMock
            ) as mock_project,
            patch.object(
                type(screen.issue_type_selector), 'selection', new_callable=PropertyMock
            ) as mock_issue_type,
            patch.object(
                type(screen.assignee_selector), 'selection', new_callable=PropertyMock
            ) as mock_assignee,
            patch.object(
                type(screen.reporter_selector), 'selection', new_callable=PropertyMock
            ) as mock_reporter,
            patch.object(
                type(screen.parent_key_field), 'value', new_callable=PropertyMock
            ) as mock_parent,
            patch.object(
                type(screen.summary_field), 'value', new_callable=PropertyMock
            ) as mock_summary,
            patch.object(
                type(screen.description_field), 'text', new_callable=PropertyMock
            ) as mock_description,
        ):
            mock_project.return_value = 'TEST'
            mock_issue_type.return_value = 'task-123'
            mock_assignee.return_value = 'assignee123'
            mock_reporter.return_value = 'reporter123'  # Set but should be ignored
            mock_parent.return_value = None
            mock_summary.return_value = 'Test Summary'
            mock_description.return_value = 'Test Description'

            # Trigger save
            screen.handle_save()

        # Get the data passed to dismiss
        dismiss_args = screen.dismiss.call_args[0][0]

        # Assertions
        assert 'reporter_account_id' not in dismiss_args, (
            'Reporter should not be included in save data when not editable'
        )
        assert dismiss_args['project_key'] == 'TEST'
        assert dismiss_args['summary'] == 'Test Summary'


@patch.object(APIController, 'get_issue_create_metadata')
@pytest.mark.asyncio
async def test_save_includes_reporter_when_editable(
    get_issue_create_metadata_mock: AsyncMock, app, create_metadata_with_editable_reporter
):
    """Test that save handler includes reporter field when it's editable."""
    # GIVEN
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        result=create_metadata_with_editable_reporter
    )
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='reporter123')
        await app.push_screen(screen)
        await pilot.pause()

        # trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()

        # Mock dismiss
        screen.dismiss = Mock()

        # Mock the selection and value properties
        with (
            patch.object(
                type(screen.project_selector), 'selection', new_callable=PropertyMock
            ) as mock_project,
            patch.object(
                type(screen.issue_type_selector), 'selection', new_callable=PropertyMock
            ) as mock_issue_type,
            patch.object(
                type(screen.assignee_selector), 'account_id', new_callable=PropertyMock
            ) as mock_assignee,
            patch.object(
                type(screen.reporter_selector), 'account_id', new_callable=PropertyMock
            ) as mock_reporter,
            patch.object(
                type(screen.parent_key_field), 'value', new_callable=PropertyMock
            ) as mock_parent,
            patch.object(
                type(screen.summary_field), 'value', new_callable=PropertyMock
            ) as mock_summary,
            patch.object(
                type(screen.description_field), 'text', new_callable=PropertyMock
            ) as mock_description,
        ):
            mock_project.return_value = 'TEST'
            mock_issue_type.return_value = 'task-123'
            mock_assignee.return_value = 'assignee123'
            mock_reporter.return_value = 'reporter123'
            mock_parent.return_value = None
            mock_summary.return_value = 'Test Summary'
            mock_description.return_value = 'Test Description'

            # WHEN
            screen.handle_save()

        # THEN
        # get the data passed to dismiss
        dismiss_args = screen.dismiss.call_args[0][0]
        assert 'reporter_account_id' in dismiss_args, (
            'Reporter should be included in save data when editable'
        )
        assert dismiss_args['reporter_account_id'] == 'reporter123'
        assert dismiss_args['project_key'] == 'TEST'
        assert dismiss_args['summary'] == 'Test Summary'


@patch.object(AddWorkItemScreen, '_validate_required_fields')
@patch.object(APIController, 'get_issue_create_metadata')
@pytest.mark.asyncio
async def test_jira_field_key(
    get_issue_create_metadata_mock: AsyncMock,
    validate_required_fields_mock: Mock,
    create_metadata_with_editable_reporter,
    app,
):
    # GIVEN
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    get_issue_create_metadata_mock.return_value = APIControllerResponse(
        result=create_metadata_with_editable_reporter
    )
    validate_required_fields_mock.return_value = True
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST', reporter_account_id='user123')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        # WHEN
        # trigger metadata fetch
        await screen.fetch_issue_create_metadata('TEST', 'task-123')
        await pilot.pause()
        screen.handle_save()
        # THEN
        assert screen.project_selector.jira_field_key == 'project_key'
        assert screen.issue_type_selector.jira_field_key == 'issue_type_id'
        assert screen.reporter_selector.jira_field_key == 'reporter_account_id'
        assert screen.assignee_selector.jira_field_key == 'assignee_account_id'
        assert screen.parent_key_field.jira_field_key == 'parent_key'
        assert screen.summary_field.jira_field_key == 'summary'
        assert screen.description_field.jira_field_key == 'description'


def test_jira_field_key_for_additional_fields(config_for_testing):
    # GIVEN
    config_for_testing.enable_creating_additional_fields = True
    fields = [
        {
            'required': True,
            'schema': {'type': 'array', 'items': 'attachment', 'system': 'attachment'},
            'name': 'Attachment',
            'key': 'attachment',
            'hasDefaultValue': False,
            'operations': ['set', 'copy'],
            'fieldId': 'attachment',
        },
        {
            'required': True,
            'schema': {
                'type': 'any',
                'custom': 'com.atlassian.jira.plugins.jira-development-integration-plugin:devsummarycf',
                'customId': 10000,
            },
            'name': 'Development',
            'key': 'customfield_10000',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10000',
        },
        {
            'required': True,
            'schema': {
                'type': 'team',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:atlassian-team',
                'customId': 10001,
                'configuration': {
                    'com.atlassian.jira.plugin.system.customfieldtypes:atlassian-team': True
                },
            },
            'name': 'Team',
            'key': 'customfield_10001',
            'autoCompleteUrl': 'https://example.atlassian.net/gateway/api/v1/recommendations',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10001',
        },
        {
            'required': True,
            'schema': {
                'type': 'date',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:datepicker',
                'customId': 10015,
            },
            'name': 'Start date',
            'key': 'customfield_10015',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10015',
        },
        {
            'required': True,
            'schema': {
                'type': 'number',
                'custom': 'com.pyxis.greenhopper.jira:jsw-story-points',
                'customId': 10016,
            },
            'name': 'Story point estimate',
            'key': 'customfield_10016',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10016',
        },
        {
            'required': True,
            'schema': {
                'type': 'string',
                'custom': 'com.pyxis.greenhopper.jira:jsw-issue-color',
                'customId': 10017,
            },
            'name': 'Issue color',
            'key': 'customfield_10017',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10017',
        },
        {
            'required': True,
            'schema': {
                'type': 'any',
                'custom': 'com.pyxis.greenhopper.jira:gh-lexo-rank',
                'customId': 10019,
            },
            'name': 'Rank',
            'key': 'customfield_10019',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10019',
        },
        {
            'required': True,
            'schema': {
                'type': 'array',
                'items': 'json',
                'custom': 'com.pyxis.greenhopper.jira:gh-sprint',
                'customId': 10020,
            },
            'name': 'Sprint',
            'key': 'customfield_10020',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10020',
        },
        {
            'required': True,
            'schema': {
                'type': 'array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10021,
            },
            'name': 'Flagged',
            'key': 'customfield_10021',
            'hasDefaultValue': False,
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [
                {
                    'self': 'https://example.atlassian.net/rest/api/3/customFieldOption/10019',
                    'value': 'Impediment',
                    'id': '10019',
                }
            ],
            'fieldId': 'customfield_10021',
        },
        {
            'required': True,
            'schema': {
                'type': 'any',
                'custom': 'com.atlassian.jira.plugins.jira-development-integration-plugin:vulnerabilitycf',
                'customId': 10035,
            },
            'name': 'Vulnerability',
            'key': 'customfield_10035',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10035',
        },
        {
            'required': True,
            'schema': {
                'type': 'array',
                'items': 'design.field.name',
                'custom': 'com.atlassian.jira.plugins.jira-development-integration-plugin:designcf',
                'customId': 10037,
            },
            'name': 'Design',
            'key': 'customfield_10037',
            'autoCompleteUrl': '',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10037',
        },
        {
            'required': True,
            'schema': {'type': 'date', 'system': 'duedate'},
            'name': 'Due date',
            'key': 'duedate',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'duedate',
        },
        {
            'required': True,
            'schema': {'type': 'array', 'items': 'issuelinks', 'system': 'issuelinks'},
            'name': 'Linked Issues',
            'key': 'issuelinks',
            'autoCompleteUrl': 'https://example.atlassian.net/rest/api/3/issue/picker?currentProjectId=&showSubTaskParent=true&showSubTasks=true&currentIssueKey=null&query=',
            'hasDefaultValue': False,
            'operations': ['add', 'copy'],
            'fieldId': 'issuelinks',
        },
        {
            'required': True,
            'schema': {'type': 'array', 'items': 'string', 'system': 'labels'},
            'name': 'Labels',
            'key': 'labels',
            'autoCompleteUrl': 'https://example.atlassian.net/rest/api/1.0/labels/suggest?query=',
            'hasDefaultValue': False,
            'operations': ['add', 'set', 'remove'],
            'fieldId': 'labels',
        },
        {
            'required': True,
            'schema': {'type': 'user', 'system': 'assignee'},
            'name': 'Assignee',
            'key': 'assignee',
            'autoCompleteUrl': 'https://example.atlassian.net/rest/api/3/user/assignable/search?project=JT&query=',
            'hasDefaultValue': True,
            'operations': ['set'],
            'fieldId': 'assignee',
        },
        {
            'required': True,
            'schema': {
                'type': 'string',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:url',
                'customId': 1111,
            },
            'name': 'Some URL',
            'key': 'url',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'url',
        },
        {
            'required': True,
            'schema': {
                'type': 'string',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:datetime',
                'customId': 1111,
            },
            'name': 'Some Datetime',
            'key': 'date-time',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'date-time',
        },
        {
            'required': True,
            'schema': {
                'type': 'string',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:userpicker',
                'customId': 2222,
            },
            'name': 'Some Datetime',
            'key': 'user-picker',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'user-picker',
        },
        {
            'required': False,
            'schema': {
                'type': 'array',
                'items': 'user',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker',
                'customId': 10003,
            },
            'name': 'Approvers',
            'key': 'customfield_10003',
            'autoCompleteUrl': 'https://example.net/rest/api/1.0/users/picker?fieldName=customfield_10003&showAvatar=true&query=',
            'hasDefaultValue': False,
            'operations': ['add', 'set', 'remove'],
            'fieldId': 'customfield_10003',
        },
    ]
    # WHEN
    widgets = create_widgets_for_work_item_creation(fields)
    # THEN
    for widget in widgets:
        assert widget.jira_field_key is not None
        if widget.id == 'customfield_10000':
            assert widget.jira_field_key == 'customfield_10000'
            assert isinstance(widget, TextInputWidget)
        if widget.id == 'customfield_10003':
            assert widget.jira_field_key == 'customfield_10003'
            assert isinstance(widget, MultiUserPickerWidget)
        elif widget.id == 'customfield_10001':
            assert widget.jira_field_key == 'customfield_10001'
            assert isinstance(widget, TextInputWidget)
        elif widget.id == 'customfield_10015':
            assert widget.jira_field_key == 'customfield_10015'
            assert isinstance(widget, DateInputWidget)
        elif widget.id == 'customfield_10016':
            assert widget.jira_field_key == 'customfield_10016'
            assert isinstance(widget, NumericInputWidget)
        elif widget.id == 'customfield_10017':
            assert widget.jira_field_key == 'customfield_10017'
            assert isinstance(widget, TextInputWidget)
        elif widget.id == 'customfield_10019':
            assert widget.jira_field_key == 'customfield_10019'
            assert isinstance(widget, TextInputWidget)
        elif widget.id == 'customfield_10020':
            assert widget.jira_field_key == 'customfield_10020'
            assert isinstance(widget, SprintWidget)
        elif widget.id == 'customfield_10021':
            assert widget.jira_field_key == 'customfield_10021'
            assert isinstance(widget, MultiSelectWidget)
        elif widget.id == 'customfield_10035':
            assert widget.jira_field_key == 'customfield_10035'
            assert isinstance(widget, TextInputWidget)
        elif widget.id == 'customfield_10037':
            assert widget.jira_field_key == 'customfield_10037'
            assert isinstance(widget, TextInputWidget)
        elif widget.id == 'duedate':
            assert widget.jira_field_key == 'duedate'
            assert isinstance(widget, DateInputWidget)
        elif widget.id == 'labels':
            assert widget.jira_field_key == 'labels'
            assert isinstance(widget, LabelsWidget)
        elif widget.id == 'url':
            assert widget.jira_field_key == 'url'
            assert isinstance(widget, URLWidget)
        elif widget.id == 'date-time':
            assert widget.jira_field_key == 'date-time'
            assert isinstance(widget, DateTimeInputWidget)
        elif widget.id == 'user-picker':
            assert widget.jira_field_key == 'user-picker'
            assert isinstance(widget, UserPickerWidget)
    assert len(widgets) == 15


def test_jira_field_key_for_non_required_additional_fields_with_ignore_list(app):
    # GIVEN
    app.config.enable_creating_additional_fields = True
    app.config.create_additional_fields_ignore_ids = ['attachment']
    fields = [
        {
            'required': False,
            'schema': {'type': 'array', 'items': 'attachment', 'system': 'attachment'},
            'name': 'Attachment',
            'key': 'attachment',
            'hasDefaultValue': False,
            'operations': ['set', 'copy'],
            'fieldId': 'attachment',
        }
    ]
    # WHEN
    widgets = create_widgets_for_work_item_creation(fields)
    # THEN
    assert widgets == []


def test_jira_field_key_for_non_required_additional_fields_without_ignore_list_non_optional_processing(
    app,
):
    # GIVEN
    app.config.enable_creating_additional_fields = False
    app.config.create_additional_fields_ignore_ids = []
    fields = [
        {
            'required': False,
            'schema': {'type': 'array', 'items': 'attachment', 'system': 'attachment'},
            'name': 'Attachment',
            'key': 'attachment',
            'hasDefaultValue': False,
            'operations': ['set', 'copy'],
            'fieldId': 'attachment',
        }
    ]
    # WHEN
    widgets = create_widgets_for_work_item_creation(fields)
    # THEN
    assert widgets == []


def test_jira_field_key_no_fields(
    config_for_testing,
):
    # WHEN
    widgets = create_widgets_for_work_item_creation([])
    # THEN
    assert widgets == []


def test_jira_field_key_field_not_supported(
    config_for_testing,
):
    # GIVEN
    fields = [
        {
            'required': False,
            'schema': {'type': 'another-type', 'items': 'attachment', 'system': 'attachment'},
            'name': 'Attachment',
            'key': 'some-field-key',
            'hasDefaultValue': False,
            'operations': ['set', 'copy'],
            'fieldId': 'some-field-id',
        }
    ]
    # WHEN
    widgets = create_widgets_for_work_item_creation(fields)
    # THEN
    assert widgets == []


def test_jira_field_key_field_custom_field_with_tooltip(
    config_for_testing,
):
    # GIVEN
    fields = [
        {
            'required': True,
            'schema': {
                'type': 'array',
                'items': 'design.field.name',
                'custom': 'com.atlassian.jira.plugins.jira-development-integration-plugin:designcf',
                'customId': 10037,
            },
            'name': 'Design',
            'key': 'customfield_10037',
            'autoCompleteUrl': '',
            'hasDefaultValue': False,
            'operations': ['set'],
            'fieldId': 'customfield_10037',
        }
    ]
    # WHEN
    widgets = create_widgets_for_work_item_creation(fields)
    # THEN
    assert widgets[0].tooltip == 'Design (Tip: to ignore use id: customfield_10037)'


def test_jira_field_key_field_custom_field_with_allowed_values_non_array_type(
    config_for_testing,
):
    # GIVEN
    fields = [
        {
            'required': True,
            'schema': {
                'type': 'non-array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10021,
            },
            'name': 'Flagged',
            'key': 'customfield_10021',
            'hasDefaultValue': False,
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [
                {
                    'self': 'https://example.atlassian.net/rest/api/3/customFieldOption/10019',
                    'value': 'Impediment',
                    'id': '10019',
                }
            ],
            'fieldId': 'customfield_10021',
        }
    ]
    # WHEN
    widgets = create_widgets_for_work_item_creation(fields)
    # THEN
    assert isinstance(widgets[0], SelectionWidget)


@pytest.mark.asyncio
async def test_validate_required_fields_is_false(app, create_metadata_without_editable_reporter):
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()
        screen._reporter_is_editable = False
        screen.description_field.text = ''

        # WHEN
        result = screen._validate_required_fields()
        assert result is False


@patch.object(CreateWorkItemProjectSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueTypeSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueSummaryField, 'value', PropertyMock(return_value='summary text'))
@pytest.mark.asyncio
async def test_validate_required_fields(app, create_metadata_without_editable_reporter):
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()
        screen._reporter_is_editable = False

        # WHEN
        result = screen._validate_required_fields()
        assert result is True


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value='1'))
@patch.object(CreateWorkItemProjectSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueTypeSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueSummaryField, 'value', PropertyMock(return_value='summary text'))
@pytest.mark.asyncio
async def test_validate_required_fields_reporter_is_editable_and_selected(
    app, create_metadata_without_editable_reporter
):
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()
        screen._reporter_is_editable = True

        # WHEN
        result = screen._validate_required_fields()
        assert result is True


@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value=None))
@patch.object(CreateWorkItemProjectSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueTypeSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueSummaryField, 'value', PropertyMock(return_value='summary text'))
@pytest.mark.asyncio
async def test_validate_required_fields_reporter_is_editable_and_not_selected(
    app, create_metadata_without_editable_reporter
):
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()
        screen._reporter_is_editable = True

        # WHEN
        result = screen._validate_required_fields()
        assert result is False


@patch.object(DescriptionWidget, 'required', PropertyMock(return_value=True))
@patch.object(JiraUserInput, 'account_id', PropertyMock(return_value=None))
@patch.object(CreateWorkItemProjectSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueTypeSelectionInput, 'selection', PropertyMock(return_value=Mock()))
@patch.object(CreateWorkItemIssueSummaryField, 'value', PropertyMock(return_value='summary text'))
@pytest.mark.asyncio
async def test_validate_required_fields_description_is_required_and_not_set(
    app, create_metadata_without_editable_reporter
):
    app.config.create_additional_fields_ignore_ids = []
    app.config.enable_creating_additional_fields = True
    async with app.run_test() as pilot:
        screen = AddWorkItemScreen(project_key='TEST')
        await app.push_screen(screen)
        await pilot.pause()
        screen._reporter_is_editable = True
        screen.description_field.text = ''

        # WHEN
        result = screen._validate_required_fields()
        assert result is False
