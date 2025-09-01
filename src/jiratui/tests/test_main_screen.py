from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from textual.widgets import Select

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.models import IssueStatus, IssueType, JiraUser, Project
from jiratui.widgets.attachments.attachments import IssueAttachmentsWidget
from jiratui.widgets.comments.comments import IssueCommentsWidget
from jiratui.widgets.filters import (
    ActiveSprintCheckbox,
    IssueSearchCreatedFromWidget,
    IssueSearchCreatedUntilWidget,
    IssueStatusSelectionInput,
    IssueTypeSelectionInput,
    JQLSearchWidget,
    OrderByWidget,
    ProjectSelectionInput,
    UserSelectionInput,
    WorkItemInputWidget,
)
from jiratui.widgets.related_work_items.related_issues import RelatedIssuesWidget
from jiratui.widgets.remote_links.links import IssueRemoteLinksWidget
from jiratui.widgets.search import IssuesSearchResultsTable
from jiratui.widgets.work_item_details.details import IssueDetailsWidget


@pytest.fixture()
def jira_users() -> list[JiraUser]:
    return [
        Mock(spec=JiraUser),
        Mock(spec=JiraUser),
    ]


@pytest.fixture()
def app(config_for_testing, jira_api_controller) -> JiraApp:
    app = JiraApp(config_for_testing)
    app.api = jira_api_controller
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.mark.parametrize(
    'key, widget',
    [
        ('p', ProjectSelectionInput),
        ('t', IssueTypeSelectionInput),
        ('s', IssueStatusSelectionInput),
        ('a', UserSelectionInput),
        ('k', WorkItemInputWidget),
        ('f', IssueSearchCreatedFromWidget),
        ('u', IssueSearchCreatedUntilWidget),
        ('o', OrderByWidget),
        ('v', ActiveSprintCheckbox),
        ('j', JQLSearchWidget),
        ('1', IssuesSearchResultsTable),
        ('3', IssueDetailsWidget),
        ('4', IssueCommentsWidget),
        ('5', RelatedIssuesWidget),
        ('6', IssueAttachmentsWidget),
        ('7', IssueRemoteLinksWidget),
    ],
)
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_quick_access_keys(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    key: str,
    widget,
    app,
):
    """Test pressing certain keys focus the correct widget."""
    async with app.run_test() as pilot:
        await pilot.press(key)
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert isinstance(main_screen.focused, widget)


@patch('jiratui.widgets.screens.APIController.search_projects')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@pytest.mark.asyncio
async def test_fetch_projects(
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    jira_api_controller,
    app,
):
    search_projects_mock.return_value = APIControllerResponse(
        result=[
            Project(id='2', name='Project B', key='P2'),
            Project(id='1', name='Project A', key='P1'),
        ]
    )
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert main_screen.project_selector.selection is None
        assert main_screen.project_selector._options == [
            ('', Select.BLANK),
            ('(P1) Project A', 'P1'),
            ('(P2) Project B', 'P2'),
        ]


@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_without_jira_user_group_id(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.jira_user_group_id = None
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await main_screen.fetch_users()
        # THEN
        assert main_screen.project_selector.selection is None
        assert main_screen.available_users == []
        assert result == []


@patch.object(APIController, 'list_all_active_users_in_group')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_with_jira_user_group_id(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    list_all_active_users_in_group_mock: AsyncMock,
    jira_users,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.jira_user_group_id = '1'
    list_all_active_users_in_group_mock.return_value = APIControllerResponse(result=jira_users)
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await main_screen.fetch_users()
        # THEN
        assert main_screen.project_selector.selection is None
        assert main_screen.available_users == []
        assert result == jira_users


@patch.object(APIController, 'list_all_active_users_in_group')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_with_jira_user_group_id_api_error(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    list_all_active_users_in_group_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.jira_user_group_id = '1'
    list_all_active_users_in_group_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await main_screen.fetch_users()
        # THEN
        assert main_screen.project_selector.selection is None
        assert main_screen.available_users == []
        assert result == []


@patch('jiratui.widgets.screens.APIController.search_users_assignable_to_projects')
@patch('jiratui.widgets.screens.APIController.search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@pytest.mark.asyncio
async def test_fetch_users_with_project_selection(
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    search_users_assignable_to_projects_mock: AsyncMock,
    jira_api_controller,
    app,
):
    # GIVEN
    search_projects_mock.return_value = APIControllerResponse(
        result=[
            Project(id='2', name='Project B', key='P2'),
            Project(id='1', name='Project A', key='P1'),
        ]
    )
    search_users_assignable_to_projects_mock.return_value = APIControllerResponse(
        result=[
            JiraUser(
                email='foo@bar',
                account_id='12345',
                active=True,
                display_name='Bart Simpson',
            )
        ]
    )
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.project_selector.value = 'P1'
        # WHEN
        result = await main_screen.fetch_users()
        # THEN
        assert main_screen.project_selector.selection == 'P1'
        assert main_screen.available_users == []
        search_users_assignable_to_projects_mock.assert_called_once_with(
            project_keys=['P1'], active=True
        )
        assert result == [
            JiraUser(
                email='foo@bar',
                account_id='12345',
                active=True,
                display_name='Bart Simpson',
            )
        ]


@patch('jiratui.widgets.screens.APIController.search_users_assignable_to_projects')
@patch('jiratui.widgets.screens.APIController.search_projects')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@pytest.mark.asyncio
async def test_fetch_users_with_project_selection_search_users_error(
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_projects_mock: AsyncMock,
    search_users_assignable_to_projects_mock: AsyncMock,
    jira_api_controller,
    app,
):
    # GIVEN
    search_projects_mock.return_value = APIControllerResponse(
        result=[
            Project(id='2', name='Project B', key='P2'),
            Project(id='1', name='Project A', key='P1'),
        ]
    )
    search_users_assignable_to_projects_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.project_selector.value = 'P1'
        # WHEN
        result = await main_screen.fetch_users()
        # THEN
        assert main_screen.project_selector.selection == 'P1'
        assert main_screen.available_users == []
        search_users_assignable_to_projects_mock.assert_called_once_with(
            project_keys=['P1'], active=True
        )
        assert result == []


@patch.object(APIController, 'list_all_active_users_in_group')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_with_users_group_id_without_using_project_workflow(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    list_all_active_users_in_group_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    config_for_testing.jira_user_group_id = '1'
    config_for_testing.on_start_up_only_fetch_projects = False
    list_all_active_users_in_group_mock.return_value = APIControllerResponse(
        result=[
            JiraUser(
                email='foo@bar',
                account_id='12345',
                active=True,
                display_name='Bart Simpson',
            )
        ]
    )
    async with app.run_test() as pilot:
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        await pilot.press('')
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        list_all_active_users_in_group_mock.assert_called_once_with(group_id='1')
        assert main_screen.available_users == [('Bart Simpson', '12345')]
        assert main_screen.users_selector.users == {
            'users': [
                JiraUser(
                    email='foo@bar',
                    account_id='12345',
                    active=True,
                    display_name='Bart Simpson',
                )
            ],
            'selection': None,
        }
        assert main_screen.users_selector._options == [
            ('', Select.BLANK),
            ('Bart Simpson', '12345'),
        ]


@patch.object(APIController, 'list_all_active_users_in_group')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_with_users_group_id_using_project_workflow(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    list_all_active_users_in_group_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    config_for_testing.jira_user_group_id = '1'
    config_for_testing.on_start_up_only_fetch_projects = True
    list_all_active_users_in_group_mock.return_value = APIControllerResponse(
        result=[
            JiraUser(
                email='foo@bar',
                account_id='12345',
                active=True,
                display_name='Bart Simpson',
            )
        ]
    )
    async with app.run_test() as pilot:
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        await pilot.press('')
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        list_all_active_users_in_group_mock.assert_not_called()
        assert main_screen.available_users == []
        assert main_screen.users_selector.users is None
        assert main_screen.users_selector._options == [
            ('', Select.BLANK),
        ]


@patch('jiratui.widgets.screens.APIController.list_all_active_users_in_group')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_with_users_group_id_user_listing_error_without_use_project_workflow(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    list_all_active_users_in_group_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    config_for_testing.jira_user_group_id = '1'
    config_for_testing.on_start_up_only_fetch_projects = False
    list_all_active_users_in_group_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test() as pilot:
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        await pilot.press('')
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        list_all_active_users_in_group_mock.assert_called_once_with(group_id='1')
        assert main_screen.available_users == []
        assert main_screen.users_selector.users == {'users': [], 'selection': None}
        assert main_screen.users_selector._options == [('', Select.BLANK)]


@patch('jiratui.widgets.screens.APIController.list_all_active_users_in_group')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_fetch_users_without_project_selection_with_users_group_id_user_listing_error_using_project_workflow(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    list_all_active_users_in_group_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    config_for_testing.jira_user_group_id = '1'
    config_for_testing.on_start_up_only_fetch_projects = True
    list_all_active_users_in_group_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test() as pilot:
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        await pilot.press('')
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        list_all_active_users_in_group_mock.assert_not_called()
        assert main_screen.available_users == []
        assert main_screen.users_selector.users is None
        assert main_screen.users_selector._options == [('', Select.BLANK)]


@patch('jiratui.widgets.screens.APIController.status')
@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_mount_fetch_statuses_without_initial_project_key_without_using_project_workflow(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    status_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.on_start_up_only_fetch_projects = False
    status_mock.return_value = APIControllerResponse(
        result=[
            IssueStatus(id='2', name='To Do', description='A task to do'),
            IssueStatus(id='1', name='Done', description='A task done'),
        ]
    )
    # WHEN
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        status_mock.assert_called_once()
        assert main_screen.available_issues_status == [('Done', '1'), ('To Do', '2')]
        assert main_screen.issue_status_selector.statuses == [('Done', '1'), ('To Do', '2')]


@patch('jiratui.widgets.screens.APIController.status')
@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_mount_fetch_statuses_without_initial_project_key_using_project_workflow(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    status_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.on_start_up_only_fetch_projects = True
    status_mock.return_value = APIControllerResponse(
        result=[
            IssueStatus(id='2', name='To Do', description='A task to do'),
            IssueStatus(id='1', name='Done', description='A task done'),
        ]
    )
    # WHEN
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        status_mock.assert_not_called()
        assert main_screen.available_issues_status == []
        assert main_screen.issue_status_selector.statuses is None


@patch('jiratui.widgets.screens.APIController.status')
@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_mount_fetch_statuses_without_initial_project_key_status_error(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    status_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    status_mock.return_value = APIControllerResponse(success=False)
    config_for_testing.on_start_up_only_fetch_projects = False
    # WHEN
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        status_mock.assert_called_once()
        assert main_screen.available_issues_status == []
        assert main_screen.issue_status_selector.statuses == []


@patch('jiratui.widgets.screens.APIController.get_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_mount_fetch_issues_types_without_initial_project_key(
    search_projects_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    get_issue_types_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.on_start_up_only_fetch_projects = False
    get_issue_types_mock.return_value = APIControllerResponse(
        result=[
            IssueType(
                id='1',
                name='Task',
                scope_project=None,
            )
        ]
    )
    # WHEN
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        get_issue_types_mock.assert_called_once()
        assert main_screen.issue_type_selector._options == [('', Select.BLANK), ('Task', '1')]


@patch('jiratui.widgets.screens.APIController.get_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_mount_fetch_issues_types_without_initial_project_key_fetch_types_error(
    search_projects_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    get_issue_types_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.on_start_up_only_fetch_projects = False
    get_issue_types_mock.return_value = APIControllerResponse(success=False)
    # WHEN
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        assert main_screen.initial_project_key is None
        assert main_screen.project_selector.selection is None
        get_issue_types_mock.assert_called_once()
        assert main_screen.issue_type_selector._options == [('', Select.BLANK)]


@pytest.mark.parametrize('expression_id, expected_expression', [(1, 'sprint=2'), (2, None)])
@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_mount_without_initial_project_key_set_jql_expression(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    config_for_testing,
    expression_id: int,
    expected_expression: str,
    jira_api_controller,
    app,
):
    # GIVEN
    app.initial_jql_expression_id = expression_id
    config_for_testing.pre_defined_jql_expressions = {1: {'expression': 'sprint=2'}}
    # WHEN
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        assert main_screen.jql_expression_input.expression == expected_expression


@patch('jiratui.widgets.screens.MainScreen.fetch_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.APIController.search_projects')
@pytest.mark.asyncio
async def test_select_project(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    fetch_users_mock: AsyncMock,
    config_for_testing,
    jira_api_controller,
    app,
):
    # GIVEN
    config_for_testing.on_start_up_only_fetch_projects = False
    search_projects_mock.return_value = APIControllerResponse(
        result=[
            Project(id='2', name='Project B', key='P2'),
            Project(id='1', name='Project A', key='P1'),
        ]
    )
    fetch_issue_types_mock.return_value = [(1, 'Task')]
    fetch_statuses_mock.return_value = [(1, 'Done')]
    fetch_users_mock.return_value = [
        JiraUser(
            email='foo@bar',
            account_id='12345',
            active=True,
            display_name='Bart Simpson',
        )
    ]
    async with app.run_test():
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        main_screen.project_selector.value = 'P1'
        # THEN
        fetch_issue_types_mock.assert_called_once()
        fetch_statuses_mock.assert_called_once()
        fetch_users_mock.assert_called_once()
        assert main_screen.issue_type_selector._options == [('', Select.BLANK)]
        assert main_screen.issue_status_selector.statuses is None
        assert main_screen.available_issues_status == []
        assert main_screen.project_selector.selection == 'P1'


@patch('jiratui.widgets.screens.MainScreen.action_search')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_search_button_triggers_issue_search(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    action_search_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        # THEN
        action_search_mock.assert_called_once()


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_search_button_resets_widgets(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('ctrl+r')
        # THEN
        search_issues_mock.assert_called_once()
        assert main_screen.issue_comments_widget.comments is None
        assert main_screen.issue_comments_widget.issue_key is None
        assert main_screen.related_issues_widget.issues is None
        assert main_screen.related_issues_widget.issue_key is None
        assert main_screen.issue_remote_links_widget.issue_key is None
        assert main_screen.issue_attachments_widget.attachments is None
        assert main_screen.issue_attachments_widget.issue_key is None
        assert main_screen.issue_summary_widget.renderable == ''
        assert main_screen.issue_description_widget._markdown == ''
        assert main_screen.search_results_table.token_by_page == {}
        assert main_screen.search_results_table.page == 1


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_next_page_search_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 0
        main_screen.search_results_table.token_by_page = {1: 'token_a'}
        # WHEN
        await pilot.press('alt+right')
        # THEN
        search_issues_mock.assert_called_once_with('token_a')
        assert main_screen.search_results_table.page == 1


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_next_page_search_results_with_missing_token(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 0
        main_screen.search_results_table.token_by_page = {2: 'token_a'}
        # WHEN
        await pilot.press('alt+right')
        # THEN
        search_issues_mock.assert_not_called()
        assert main_screen.search_results_table.page == 0


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_previous_page_search_results(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 2
        main_screen.search_results_table.token_by_page = {1: 'token_a'}
        # WHEN
        await pilot.press('alt+left')
        # THEN
        search_issues_mock.assert_called_once_with('token_a')
        assert main_screen.search_results_table.page == 1


@patch('jiratui.widgets.screens.MainScreen.search_issues')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_click_previous_page_search_results_with_missing_token(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_issues_mock: AsyncMock,
    app,
):
    async with app.run_test() as pilot:
        # GIVEN
        main_screen = cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        main_screen.search_results_table.page = 1
        main_screen.search_results_table.token_by_page = {2: 'token_a'}
        # WHEN
        await pilot.press('alt+left')
        # THEN
        search_issues_mock.assert_not_called()
        assert main_screen.search_results_table.page == 1
