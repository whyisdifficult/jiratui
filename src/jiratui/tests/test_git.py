from unittest.mock import AsyncMock, Mock, patch

from git import Head, Repo
import pytest
from textual.widgets import Button

from jiratui.models import JiraIssue, JiraIssueSearchResponse
from jiratui.widgets.git_screen import GitScreen
from jiratui.widgets.screens import MainScreen, WorkItemSearchResult


@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_git_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen.checkbox_input.value is False
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == 'feature/key-2'
        assert app.screen.create_branch_button.disabled is True


@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_select_repo(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen.checkbox_input.value is False
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == 'feature/key-2'
        assert app.screen.create_branch_button.disabled is False
        assert app.screen.repository_selector.selection == 'path/a/.git'
        assert app.screen.label_input.content == 'Target Repository: path/a/.git'


@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_no_branch_disables_button(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('backspace')
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen.checkbox_input.value is False
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == ''
        assert app.screen.create_branch_button.disabled is True
        assert app.screen.repository_selector.selection == 'path/a/.git'
        assert app.screen.label_input.content == 'Target Repository: path/a/.git'


@patch.object(GitScreen, '_create_branch')
@patch.object(GitScreen, '_get_git_repository')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_press_button_repo_not_found(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_git_repository_mock: Mock,
    create_branch_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    get_git_repository_mock.return_value = None
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.click(Button)
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen.checkbox_input.value is False
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == 'feature/key-2'
        assert app.screen.create_branch_button.disabled is False
        assert app.screen.repository_selector.selection == 'path/a/.git'
        assert app.screen.label_input.content == 'Target Repository: path/a/.git'
        create_branch_mock.assert_not_called()


@patch.object(GitScreen, '_get_repo_branches')
@patch.object(GitScreen, '_create_branch')
@patch.object(GitScreen, '_get_git_repository')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_press_button_branch_exists(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_git_repository_mock: Mock,
    create_branch_mock: Mock,
    get_repo_branches_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    get_git_repository_mock.return_value = Mock(spec=Repo)
    get_repo_branches_mock.return_value = ['feature/key-2']
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, GitScreen)
        assert app.screen.checkbox_input.value is False
        assert app.screen._work_item_key == 'key-2'
        assert app.screen._repositories == [('Repo A', 'path/a/.git')]
        assert app.screen.branch_input.value == 'feature/key-2'
        assert app.screen.create_branch_button.disabled is False
        assert app.screen.repository_selector.selection == 'path/a/.git'
        assert app.screen.label_input.content == 'Target Repository: path/a/.git'
        get_git_repository_mock.assert_called_once()
        create_branch_mock.assert_not_called()
        assert (
            app.screen.error_message_widget.content
            == 'The branch you want to create already exists'
        )


@patch.object(GitScreen, '_get_repo_branches')
@patch.object(GitScreen, '_create_branch')
@patch.object(GitScreen, '_get_git_repository')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_press_button_branch_does_not_exists(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_git_repository_mock: Mock,
    create_branch_mock: Mock,
    get_repo_branches_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    get_git_repository_mock.return_value = Mock(spec=Repo)
    get_repo_branches_mock.return_value = ['feature/key-3']
    head_mock = Mock(spec=Head)
    head_mock.configure_mock(name='feature/key-2')
    create_branch_mock.return_value = head_mock
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        get_git_repository_mock.assert_called_once()
        create_branch_mock.assert_called_once()
        assert isinstance(app.screen, MainScreen)


@patch.object(GitScreen, '_get_repo_branches')
@patch.object(GitScreen, '_get_git_repository')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_press_button_branch_creation_fails(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_git_repository_mock: Mock,
    get_repo_branches_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    get_git_repository_mock.return_value = Mock(
        spec=Repo, create_head=Mock(side_effect=Exception('error'))
    )
    get_repo_branches_mock.return_value = ['feature/key-3']
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, GitScreen)
        get_git_repository_mock.assert_called_once()
        assert app.screen.error_message_widget.content == 'error'
        assert app.screen.checkbox_input.value is False


@patch.object(GitScreen, '_create_branch')
@patch.object(GitScreen, '_get_repo_branches')
@patch.object(GitScreen, '_get_git_repository')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_git_screen_press_button_branch_creation_with_checkout(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_git_repository_mock: Mock,
    get_repo_branches_mock: Mock,
    create_branch_mock: Mock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    app.config.search_on_startup = False
    app.config.git_repositories = {'1': {'name': 'Repo A', 'path': 'path/a/.git'}}
    get_git_repository_mock.return_value = Mock(spec=Repo, create_head=Mock(spec=Head))
    get_repo_branches_mock.return_value = ['feature/key-3']
    head_checkout = Mock()
    create_branch_mock.return_value = Mock(spec=Head, checkout=head_checkout)
    async with app.run_test() as pilot:
        # GIVEN
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        # WHEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('ctrl+g')
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('space')  # click the checkbox
        await pilot.press('tab')
        await pilot.press('enter')  # click the button
        # THEN
        create_branch_mock.assert_called_once()
        get_git_repository_mock.assert_called_once()
        head_checkout.assert_called_once()
        assert isinstance(app.screen, MainScreen)
