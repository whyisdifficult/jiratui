from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.models import IssueStatus, IssueType, JiraIssueSearchResponse, RelatedJiraIssue
from jiratui.widgets.screens.goto import GotToScreen


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_item_not_found(get_issue_mock: AsyncMock, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        assert screen.table_related.row_count == 0
        assert not screen.table_related.display
        assert screen.table_parent.row_count == 0
        assert not screen.table_parent.display
        assert screen.table_subtasks.row_count == 0
        assert not screen.table_subtasks.display
        assert screen.table_basic_details.row_count == 0
        assert screen.table_basic_details.display
        assert screen.table_basic_details.border_title == 'key-2'


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_item_found_with_related_tasks_parent_and_subtasks(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    main_work_item = jira_issues[1]
    main_work_item.related_issues = [
        RelatedJiraIssue(
            id='99',
            key='key-99',
            summary='test',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[main_work_item])
    )
    get_subtasks_mock.return_value = [jira_issues[0]]
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        get_issue_mock.assert_called_once_with(issue_id_or_key='key-2')
        get_subtasks_mock.assert_called_once()
        get_parent_mock.assert_called_once()
        assert screen.table_related.row_count == 1
        assert screen.table_related.display is True
        assert screen.table_parent.row_count == 1
        assert screen.table_parent.display is True
        assert screen.table_subtasks.row_count == 1
        assert screen.table_subtasks.display is True
        assert screen.table_basic_details.row_count == 2
        assert screen.table_basic_details.display is True


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_fill_in_parent_table(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    get_subtasks_mock.return_value = []
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        screen._fill_in_parent_table(jira_issues[1])
        assert screen.table_parent.row_count == 1
        assert screen.table_parent.display is True


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_fill_in_parent_table_without_parent(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    get_subtasks_mock.return_value = []
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        screen._fill_in_parent_table(None)
        assert screen.table_parent.row_count == 0
        assert screen.table_parent.display is False


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_fill_in_subtasks_table(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    get_subtasks_mock.return_value = [jira_issues[1]]
    get_parent_mock.return_value = None
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        screen._fill_in_subtasks_table([jira_issues[1]])
        assert screen.table_subtasks.row_count == 1
        assert screen.table_subtasks.display is True


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_fill_in_subtasks_table_without_subtasks(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    get_subtasks_mock.return_value = []
    get_parent_mock.return_value = None
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        screen._fill_in_subtasks_table([])
        assert screen.table_subtasks.row_count == 0
        assert screen.table_subtasks.display is False


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_fill_in_related_work_items_table(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    get_subtasks_mock.return_value = [jira_issues[1]]
    get_parent_mock.return_value = None
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        screen._fill_in_related_work_items_table(
            [
                RelatedJiraIssue(
                    id='99',
                    key='key-99',
                    summary='test',
                    status=IssueStatus(name='Done', id='1'),
                    issue_type=IssueType(id='1', name='Task'),
                )
            ]
        )
        assert screen.table_subtasks.row_count == 1
        assert screen.table_subtasks.display is True


@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_fill_in_related_work_items_table_without_tasks(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    get_subtasks_mock.return_value = []
    get_parent_mock.return_value = None
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        screen._fill_in_related_work_items_table([])
        assert screen.table_subtasks.row_count == 0
        assert screen.table_subtasks.display is False


@patch.object(APIController, 'search_issues')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_get_subtasks(
    get_issue_mock: AsyncMock, search_issues_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    search_issues_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[0]])
    )
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        result = await screen._get_subtasks()
        # THEN
        assert result == [jira_issues[0]]


@pytest.mark.parametrize(
    'search_issues_result',
    [
        APIControllerResponse(result=JiraIssueSearchResponse(issues=[])),
        APIControllerResponse(result=None),
        APIControllerResponse(success=False),
    ],
)
@patch.object(APIController, 'search_issues')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_get_subtasks_no_tasks_found(
    get_issue_mock: AsyncMock, search_issues_mock: AsyncMock, search_issues_result, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    search_issues_mock.return_value = search_issues_result
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        result = await screen._get_subtasks()
        # THEN
        assert result == []


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_get_parent(get_issue_mock: AsyncMock, jira_issues, app):
    # GIVEN
    get_issue_mock.side_effect = [
        APIControllerResponse(result=JiraIssueSearchResponse(issues=[])),
        APIControllerResponse(result=JiraIssueSearchResponse(issues=[jira_issues[0]])),
    ]
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        result = await screen._get_parent('key-1')
        # THEN
        assert result == jira_issues[0]
        get_issue_mock.assert_has_calls(
            [call(issue_id_or_key='key-2'), call(issue_id_or_key='key-1')]
        )


@pytest.mark.parametrize(
    'search_issues_result',
    [
        APIControllerResponse(result=JiraIssueSearchResponse(issues=[])),
        APIControllerResponse(result=None),
        APIControllerResponse(success=False),
    ],
)
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_get_parent_no_tasks_found(
    get_issue_mock: AsyncMock, search_issues_result, app
):
    # GIVEN
    get_issue_mock.side_effect = [
        APIControllerResponse(result=JiraIssueSearchResponse(issues=[])),
        search_issues_result,
    ]
    async with app.run_test():
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        result = await screen._get_parent('key-1')
        # THEN
        assert result is None
        get_issue_mock.assert_has_calls(
            [call(issue_id_or_key='key-2'), call(issue_id_or_key='key-1')]
        )


@patch.object(JiraApp, 'copy_to_clipboard')
@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_copy_key(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    copy_to_clipboard_mock: Mock,
    jira_issues,
    app,
):
    # GIVEN
    main_work_item = jira_issues[1]
    main_work_item.related_issues = [
        RelatedJiraIssue(
            id='99',
            key='key-99',
            summary='test',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[main_work_item])
    )
    get_subtasks_mock.return_value = [jira_issues[0]]
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test() as pilot:
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('ctrl+k')
        # THEN
        copy_to_clipboard_mock.assert_called_once_with('key-1')


@patch('jiratui.widgets.screens.goto.build_external_url_for_issue')
@patch.object(JiraApp, 'copy_to_clipboard')
@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_copy_url(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    copy_to_clipboard_mock: Mock,
    build_external_url_for_issue_mock: Mock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    build_external_url_for_issue_mock.return_value = 'http://foo.bar/browse/key-1'
    mock_configuration.jira_base_url = 'http://foo.bar'
    main_work_item = jira_issues[1]
    main_work_item.related_issues = [
        RelatedJiraIssue(
            id='99',
            key='key-99',
            summary='test',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[main_work_item])
    )
    get_subtasks_mock.return_value = [jira_issues[0]]
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test() as pilot:
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('ctrl+j')
        # THEN
        copy_to_clipboard_mock.assert_called_once_with('http://foo.bar/browse/key-1')


@patch('jiratui.widgets.screens.goto.build_external_url_for_issue')
@patch.object(JiraApp, 'copy_to_clipboard')
@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_copy_url_without_url(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    copy_to_clipboard_mock: Mock,
    build_external_url_for_issue_mock: Mock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    build_external_url_for_issue_mock.return_value = ''
    mock_configuration.jira_base_url = 'http://foo.bar'
    main_work_item = jira_issues[1]
    main_work_item.related_issues = [
        RelatedJiraIssue(
            id='99',
            key='key-99',
            summary='test',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[main_work_item])
    )
    get_subtasks_mock.return_value = [jira_issues[0]]
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test() as pilot:
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('ctrl+j')
        # THEN
        copy_to_clipboard_mock.assert_not_called()


@patch('jiratui.widgets.screens.goto.build_external_url_for_issue')
@patch.object(JiraApp, 'open_url')
@patch.object(GotToScreen, '_get_parent')
@patch.object(GotToScreen, '_get_subtasks')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_goto_screen_open_url(
    get_issue_mock: AsyncMock,
    get_subtasks_mock: AsyncMock,
    get_parent_mock: AsyncMock,
    open_url_mock: Mock,
    build_external_url_for_issue_mock: Mock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    build_external_url_for_issue_mock.return_value = 'http://foo.bar/browse/key-1'
    mock_configuration.jira_base_url = 'http://foo.bar'
    main_work_item = jira_issues[1]
    main_work_item.related_issues = [
        RelatedJiraIssue(
            id='99',
            key='key-99',
            summary='test',
            status=IssueStatus(name='Done', id='1'),
            issue_type=IssueType(id='1', name='Task'),
        )
    ]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[main_work_item])
    )
    get_subtasks_mock.return_value = [jira_issues[0]]
    get_parent_mock.return_value = jira_issues[1]
    async with app.run_test() as pilot:
        # WHEN
        screen = GotToScreen('key-2', APIController())
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('ctrl+o')
        # THEN
        open_url_mock.assert_called_once_with('http://foo.bar/browse/key-1')
