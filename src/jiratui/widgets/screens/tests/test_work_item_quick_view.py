from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.commons.widgets import ReadOnlyPlainTextTextAreaWidget
from jiratui.widgets.screens.work_item_quick_view import QuickViewDetails, WorkItemQuickViewScreen


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_action_open_issue_in_browser(get_issue_mock: AsyncMock, mock_configuration, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        app.open_url = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_open_issue_in_browser()
        # THEN
        app.open_url.assert_called_once_with('http://foo.bar/browse/WI-1')
        get_issue_mock.assert_called_once()


@pytest.mark.asyncio
async def test_action_open_issue_in_browser_without_work_item_key(mock_configuration, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('')
        app.open_url = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_open_issue_in_browser()
        # THEN
        app.open_url.assert_not_called()


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_action_copy_issue_url(get_issue_mock: AsyncMock, mock_configuration, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        app.copy_to_clipboard = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_copy_issue_url()
        # THEN
        app.copy_to_clipboard.assert_called_once_with('http://foo.bar/browse/WI-1')


@patch.object(APIController, 'get_issue')
@patch('jiratui.widgets.screens.work_item_quick_view.build_external_url_for_issue')
@pytest.mark.asyncio
async def test_action_copy_issue_url_without_url(
    build_external_url_for_issue_mock: Mock, get_issue_mock: AsyncMock, mock_configuration, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    build_external_url_for_issue_mock.return_value = ''
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        app.copy_to_clipboard = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_copy_issue_url()
        # THEN
        app.copy_to_clipboard.assert_not_called()


@pytest.mark.asyncio
async def test_action_copy_issue_url_without_work_item_key(mock_configuration, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('')
        app.copy_to_clipboard = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_copy_issue_url()
        # THEN
        app.copy_to_clipboard.assert_not_called()


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_action_copy_issue_key(get_issue_mock: AsyncMock, mock_configuration, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        app.copy_to_clipboard = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_copy_issue_url()
        # THEN
        app.copy_to_clipboard.assert_called_once_with('http://foo.bar/browse/WI-1')


@pytest.mark.asyncio
async def test_action_copy_issue_key_without_work_item_key(mock_configuration, app):
    # GIVEN
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('')
        app.copy_to_clipboard = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_copy_issue_url()
        # THEN
        app.copy_to_clipboard.assert_not_called()


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_action_search_work_item_dismiss_screen_with_key(
    get_issue_mock: AsyncMock, mock_configuration, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_search_work_item()
        # THEN
        get_issue_mock.assert_called_once()
        assert screen.dismiss.call_args[0][0] == 'WI-1'


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_action_search_work_item_dismiss_screen_without_key(
    get_issue_mock: AsyncMock, mock_configuration, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.action_search_work_item()
        # THEN
        get_issue_mock.assert_not_called()
        assert screen.dismiss.call_args[0] == ()


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_dismiss_upon_receiving_load_work_item_message(
    get_issue_mock: AsyncMock, mock_configuration, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        screen.post_message(QuickViewDetails.LoadWorkItem('WI-2'))
        await pilot.pause()
        # THEN
        get_issue_mock.assert_called_once()
        assert screen.dismiss.call_args[0][0] == 'WI-2'


@patch('jiratui.widgets.screens.work_item_quick_view.build_read_only_rich_text_widget')
@patch.object(JiraIssue, 'rich_text_value_is_empty')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_mount_rich_text_value_is_empty(
    get_issue_mock: AsyncMock,
    rich_text_value_is_empty_mock: Mock,
    build_read_only_rich_text_widget_mock: Mock,
    mock_configuration,
    jira_issues,
    app,
):
    # GIVEN
    build_read_only_rich_text_widget_mock.return_value = ReadOnlyPlainTextTextAreaWidget(
        field_id='description',
        jira_field_key='description',
    )
    rich_text_value_is_empty_mock.return_value = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='WI-1')
        rich_text_value_is_empty_mock.assert_called_once_with(jira_issues[0].description)
        build_read_only_rich_text_widget_mock.assert_called_once()
        table = screen.query_one(QuickViewDetails)
        assert table.row_count == 13


@patch('jiratui.widgets.screens.work_item_quick_view.build_read_only_rich_text_widget')
@patch.object(JiraIssue, 'rich_text_value_is_empty')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_mount_rich_text_value_is_not_empty(
    get_issue_mock: AsyncMock,
    rich_text_value_is_empty_mock: Mock,
    build_read_only_rich_text_widget_mock: Mock,
    mock_configuration,
    jira_issues,
    app,
):
    # GIVEN
    rich_text_value_is_empty_mock.return_value = True
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=jira_issues)
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='WI-1')
        rich_text_value_is_empty_mock.assert_called_once_with(jira_issues[0].description)
        build_read_only_rich_text_widget_mock.assert_not_called()
        table = screen.query_one(QuickViewDetails)
        assert table.row_count == 13


@patch('jiratui.widgets.screens.work_item_quick_view.build_read_only_rich_text_widget')
@patch.object(JiraIssue, 'rich_text_value_is_empty')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_mount_with_issue_metadata(
    get_issue_mock: AsyncMock,
    rich_text_value_is_empty_mock: Mock,
    build_read_only_rich_text_widget_mock: Mock,
    mock_configuration,
    jira_issues,
    app,
):
    # GIVEN
    build_read_only_rich_text_widget_mock.return_value = ReadOnlyPlainTextTextAreaWidget(
        field_id='description',
        jira_field_key='description',
    )
    rich_text_value_is_empty_mock.return_value = False
    issue = jira_issues[0]
    issue.edit_meta = {
        'fields': {
            'customfield_10021': {
                'required': False,
                'schema': {
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea',
                    'customId': 10021,
                },
                'name': 'Flagged',
                'key': 'customfield_10021',
                'operations': ['add', 'set', 'remove'],
                'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
            },
        }
    }
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='WI-1')
        rich_text_value_is_empty_mock.assert_has_calls(
            [
                call(issue.description),
                call(None),
            ]
        )
        build_read_only_rich_text_widget_mock.assert_has_calls(
            [
                call(
                    jira_field_key='description',
                    field_name='Description',
                    required=False,
                    content=None,
                ),
                call(
                    jira_field_key='customfield_10021',
                    field_name='Flagged',
                    required=False,
                    content=None,
                ),
            ]
        )
        table = screen.query_one(QuickViewDetails)
        assert table.row_count == 13
        assert screen.tabbed_content.tab_count == 2


@patch('jiratui.widgets.screens.work_item_quick_view.build_read_only_rich_text_widget')
@patch.object(JiraIssue, 'rich_text_value_is_empty')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_mount_with_issue_metadata_single_tab(
    get_issue_mock: AsyncMock,
    rich_text_value_is_empty_mock: Mock,
    build_read_only_rich_text_widget_mock: Mock,
    mock_configuration,
    jira_issues,
    app,
):
    # GIVEN
    build_read_only_rich_text_widget_mock.return_value = ReadOnlyPlainTextTextAreaWidget(
        field_id='description',
        jira_field_key='description',
    )
    rich_text_value_is_empty_mock.return_value = False
    issue = jira_issues[0]
    issue.edit_meta = {
        'fields': {
            'description': {
                'required': False,
                'schema': {
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea',
                    'customId': 10021,
                },
                'name': 'Flagged',
                'key': 'description',
                'operations': ['add', 'set', 'remove'],
                'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
            },
        }
    }
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='WI-1')
        rich_text_value_is_empty_mock.assert_has_calls(
            [
                call(issue.description),
            ]
        )
        build_read_only_rich_text_widget_mock.assert_has_calls(
            [
                call(
                    jira_field_key='description',
                    field_name='Description',
                    required=False,
                    content=None,
                ),
            ]
        )
        table = screen.query_one(QuickViewDetails)
        assert table.row_count == 13
        assert screen.tabbed_content.tab_count == 1


@patch('jiratui.widgets.screens.work_item_quick_view.build_read_only_rich_text_widget')
@patch.object(JiraIssue, 'rich_text_value_is_empty')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_mount_with_issue_metadata_with_environment_field(
    get_issue_mock: AsyncMock,
    rich_text_value_is_empty_mock: Mock,
    build_read_only_rich_text_widget_mock: Mock,
    mock_configuration,
    jira_issues,
    app,
):
    # GIVEN
    build_read_only_rich_text_widget_mock.return_value = ReadOnlyPlainTextTextAreaWidget(
        field_id='description',
        jira_field_key='description',
    )
    rich_text_value_is_empty_mock.return_value = False
    issue = jira_issues[0]
    issue.edit_meta = {
        'fields': {
            'environment': {
                'required': True,
                'schema': {
                    'type': 'array',
                    'items': 'option',
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea',
                    'customId': 10021,
                },
                'name': 'Environment',
                'key': 'environment',
                'operations': ['add', 'set', 'remove'],
                'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
            },
        }
    }
    issue.environment = 'some text'
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[issue])
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        # WHEN
        screen = WorkItemQuickViewScreen('WI-1')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='WI-1')
        rich_text_value_is_empty_mock.assert_has_calls(
            [
                call(issue.description),
                call('some text'),
            ]
        )
        build_read_only_rich_text_widget_mock.assert_has_calls(
            [
                call(
                    jira_field_key='description',
                    field_name='Description',
                    required=False,
                    content=None,
                ),
                call(
                    jira_field_key='environment',
                    field_name='Environment',
                    required=True,
                    content='some text',
                ),
            ]
        )
        table = screen.query_one(QuickViewDetails)
        assert table.row_count == 13
        assert screen.tabbed_content.tab_count == 2
