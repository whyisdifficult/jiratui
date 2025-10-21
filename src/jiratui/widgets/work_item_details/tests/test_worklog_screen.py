from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

from dateutil import parser  # type:ignore[import-untyped]
import pytest
from textual.widgets import Button

from jiratui.api_controller.controller import APIControllerResponse
from jiratui.app import JiraApp
from jiratui.models import JiraIssue, JiraIssueSearchResponse, JiraWorklog, PaginatedJiraWorklog
from jiratui.widgets.filters import ProjectSelectionInput
from jiratui.widgets.screens import MainScreen, WorkItemSearchResult
from jiratui.widgets.work_item_details.details import IssueDetailsWidget
from jiratui.widgets.work_item_details.work_log import (
    LogDateTimeInput,
    LogWorkScreen,
    TimeRemainingInput,
    TimeSpentInput,
    WorkDescription,
    WorkItemWorkLogScreen,
)


@pytest.mark.parametrize(
    'time_spent, time_remaining, current_remaining_estimate, disabled',
    [
        ('', '', '2h', True),
        ('1h', '', '2h', False),
        ('1q', '', '2h', True),
        ('1w 1d', '', '2h', False),
        ('', '1w', '2h', True),
        ('', '2h', '2h', True),
        ('', '1q', '2h', True),
        ('1h', '1w', '2h', False),
        ('1h ', '1d', '2h', False),
        ('1w 1d', '1w', '2h', False),
        ('1w', '1q', '2h', True),
        ('1q', '1d', '2h', True),
        ('', '', None, True),
        ('1h', '', None, False),
        ('1q', '', None, True),
        ('1w 1d', '', None, False),
        ('', '1w', None, True),
        ('', '1q', None, True),
        ('1h', '1w', None, False),
        ('1h ', '1d', None, False),
        ('1w 1d', '1w', None, False),
        ('1w', '1q', None, True),
        ('1q', '1d', None, True),
    ],
)
@pytest.mark.asyncio
async def test_log_work_screen(
    time_spent: str,
    time_remaining: str,
    current_remaining_estimate: str | None,
    disabled: bool,
    jira_api_controller,
    app,
):
    async with app.run_test():
        await app.push_screen(LogWorkScreen('1'))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        screen._enable_disable_widgets(time_spent, time_remaining, True)
        assert screen.save_button.disabled is disabled
        assert screen.log_date_time_input.disabled is disabled
        assert screen.work_description_input.disabled is disabled


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_initial_state(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test():
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.save_button.disabled is True
        assert screen.log_date_time_input.disabled is True
        assert screen.work_description_input.disabled is True
        assert screen.time_spent_input.value == ''
        assert screen.time_remaining_input.value == current_remaining_estimate


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_with_valid_time_spent_value(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_with_incorrect_time_spent_value(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('q')
        assert screen.focused.value == '1q'
        assert screen.save_button.disabled is True
        assert screen.log_date_time_input.disabled is True
        assert screen.work_description_input.disabled is True
        assert screen.time_remaining_input.value == current_remaining_estimate


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_with_correct_datetime_value(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    # GIVEN
    date_time_input = datetime.now().strftime('%Y-%m-%d %H:%M')
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == date_time_input
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
        assert screen.log_date_time_input.value == date_time_input
        await pilot.press('backspace')  # delete content
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('2')
        await pilot.press('0')
        await pilot.press('2')
        await pilot.press('5')
        await pilot.press('1')
        await pilot.press('0')
        await pilot.press('1')
        await pilot.press('8')
        await pilot.press('1')
        await pilot.press('3')
        await pilot.press('4')
        await pilot.press('5')
        assert screen.log_date_time_input.value == '2025-10-18 13:45'
        assert screen.save_button.disabled is False


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_with_incorrect_datetime_value(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        await pilot.press('2')
        await pilot.press('0')
        await pilot.press('2')
        await pilot.press('5')
        await pilot.press('2')
        await pilot.press('0')
        await pilot.press('1')
        await pilot.press('8')
        await pilot.press('1')
        await pilot.press('3')
        await pilot.press('4')
        await pilot.press('5')
        await pilot.press('tab')  # move focus away
        assert isinstance(screen.focused, WorkDescription)
        assert screen.log_date_time_input.value == '2025-20-18 13:45'
        assert screen.save_button.disabled is True


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_with_empty_datetime_value(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    # GIVEN
    date_time_input = datetime.now().strftime('%Y-%m-%d %H:%M')
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == date_time_input
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
        await pilot.press('backspace')  # delete content
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('backspace')
        await pilot.press('tab')  # move focus away
        assert screen.log_date_time_input.value == ''
        assert isinstance(screen.focused, WorkDescription)
        await pilot.press('a')
        assert screen.save_button.disabled is True


@pytest.mark.parametrize('current_remaining_estimate', [''])
@pytest.mark.asyncio
async def test_log_work_screen_with_valid_time_spent_incorrect_time_remaining(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        assert isinstance(screen.focused, TimeRemainingInput)
        await pilot.press('1')
        await pilot.press('q')
        assert screen.time_remaining_input.value == '1q'
        assert screen.save_button.disabled is True


@pytest.mark.parametrize('current_remaining_estimate', [''])
@pytest.mark.asyncio
async def test_log_work_screen_with_valid_time_spent_correct_time_remaining(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        assert isinstance(screen.focused, TimeRemainingInput)
        await pilot.press('1')
        await pilot.press('w')
        assert screen.time_remaining_input.value == '1w'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False


@pytest.mark.asyncio
async def test_log_work_screen_dismissed(
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1'))
        await pilot.press('escape')
        assert isinstance(app.focused, ProjectSelectionInput)


@patch.object(LogWorkScreen, 'dismiss')
@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_saving(
    dismiss_mock: Mock,
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        await pilot.press('2')
        await pilot.press('0')
        await pilot.press('2')
        await pilot.press('5')
        await pilot.press('1')
        await pilot.press('0')
        await pilot.press('1')
        await pilot.press('8')
        await pilot.press('1')
        await pilot.press('3')
        await pilot.press('4')
        await pilot.press('5')
        assert screen.log_date_time_input.value == '2025-10-18 13:45'
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, WorkDescription)
        await pilot.press('t')
        assert screen.save_button.disabled is False
        await pilot.press('tab')
        assert isinstance(screen.focused, Button)
        await pilot.press('enter')
        dismiss_mock.assert_called_once_with(
            {
                'time_spent': '1h',
                'time_remaining': current_remaining_estimate,
                'description': 't',
                'started': '2025-10-18T13:45',
                'current_remaining_estimate': current_remaining_estimate,
            }
        )


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch.object(LogWorkScreen, 'dismiss')
@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_adding_worklog_user_clicks_cancel(
    dismiss_mock: Mock,
    refresh_work_item_details_mock: Mock,
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(LogWorkScreen('1', current_remaining_estimate))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        screen._current_remaining_estimate = current_remaining_estimate
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
        assert screen.log_date_time_input.value == datetime.now().strftime('%Y-%m-%d %H:%M')
        await pilot.press('2')
        await pilot.press('0')
        await pilot.press('2')
        await pilot.press('5')
        await pilot.press('1')
        await pilot.press('0')
        await pilot.press('1')
        await pilot.press('8')
        await pilot.press('1')
        await pilot.press('3')
        await pilot.press('4')
        await pilot.press('5')
        assert screen.log_date_time_input.value == '2025-10-18 13:45'
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, WorkDescription)
        await pilot.press('t')
        assert screen.save_button.disabled is False
        await pilot.press('tab')
        await pilot.press('tab')
        assert isinstance(screen.focused, Button)
        await pilot.press('enter')
        dismiss_mock.assert_called_once_with({})
        refresh_work_item_details_mock.assert_not_called()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch('jiratui.widgets.screens.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_with_success(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    refresh_work_item_details_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    add_work_item_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+t')
        assert isinstance(app.screen, LogWorkScreen)
        date_time_value = app.screen.log_date_time_input.value  # type:ignore
        await pilot.press('1')
        await pilot.press('w')
        await pilot.press('tab')  # move to time remaining
        await pilot.press('2')
        await pilot.press('w')
        await pilot.press('tab')  # move to date/time
        await pilot.press('tab')  # move to description
        await pilot.press('-')  # move to time remaining
        await pilot.press('tab')  # move to save button
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, MainScreen)
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id='key-2',
            started=parser.parse(f'{date_time_value}Z'),
            time_spent='1w',
            time_remaining='2w',
            comment='-',
            current_remaining_estimate=None,
        )
        refresh_work_item_details_mock.assert_called_once()


@patch.object(IssueDetailsWidget, '_refresh_work_item_details')
@patch('jiratui.widgets.screens.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_with_error_adding_new_worklog(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    refresh_work_item_details_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    add_work_item_worklog_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+t')
        assert isinstance(app.screen, LogWorkScreen)
        date_time_value = app.screen.log_date_time_input.value  # type:ignore
        await pilot.press('1')
        await pilot.press('w')
        await pilot.press('tab')  # move to time remaining
        await pilot.press('2')
        await pilot.press('w')
        await pilot.press('tab')  # move to date/time
        await pilot.press('tab')  # move to description
        await pilot.press('-')  # move to time remaining
        await pilot.press('tab')  # move to save button
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, MainScreen)
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id='key-2',
            started=parser.parse(f'{date_time_value}Z'),
            time_spent='1w',
            time_remaining='2w',
            comment='-',
            current_remaining_estimate=None,
        )
        refresh_work_item_details_mock.assert_not_called()


@patch('jiratui.widgets.screens.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_when_users_clicks_cancel(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    add_work_item_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+t')
        assert isinstance(app.screen, LogWorkScreen)
        await pilot.press('1')
        await pilot.press('w')
        await pilot.press('tab')  # move to time remaining
        await pilot.press('2')
        await pilot.press('w')
        await pilot.press('tab')  # move to date/time
        await pilot.press('tab')  # move to description
        await pilot.press('-')  # move to time remaining
        await pilot.press('tab')  # move to save button
        await pilot.press('tab')  # move to cancel button
        await pilot.press('enter')
        # THEN
        assert isinstance(app.screen, MainScreen)
        add_work_item_worklog_mock.assert_not_called()


@patch('jiratui.widgets.work_item_details.work_log.build_external_url_for_work_log')
@patch('jiratui.widgets.screens.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_modal_to_view_work_logs(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    jira_issues: list[JiraIssue],
    jira_worklogs: list[JiraWorklog],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    build_external_url_for_work_log_mock.return_value = 'foo.bar'
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        screen = cast('WorkItemWorkLogScreen', app.screen)
        assert screen.root_container.border_subtitle == 'Showing 2 of 2'
        assert screen.root_container.border_title == 'Worklog - key-2'


@patch('jiratui.widgets.screens.APIController.remove_worklog')
@patch('jiratui.widgets.work_item_details.work_log.build_external_url_for_work_log')
@patch('jiratui.widgets.screens.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_delete_worklog(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    remove_worklog_mock: Mock,
    jira_issues: list[JiraIssue],
    jira_worklogs: list[JiraWorklog],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    build_external_url_for_work_log_mock.return_value = 'foo.bar'
    remove_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.root_container.border_subtitle == 'Showing 2 of 2'
        assert screen.root_container.border_title == 'Worklog - key-2'
        assert screen._work_logs_deleted is False
        await pilot.press('tab')
        await pilot.press('d')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        remove_worklog_mock.assert_called_once_with('key-2', '1')
        assert screen.root_container.border_subtitle == 'Showing 1 of 1'
        assert screen._work_logs_deleted is True


@patch.object(IssueDetailsWidget, '_handle_worklog_screen_dismissal')
@patch('jiratui.widgets.screens.APIController.remove_worklog')
@patch('jiratui.widgets.work_item_details.work_log.build_external_url_for_work_log')
@patch('jiratui.widgets.screens.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_delete_worklog_and_close_worklog_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    remove_worklog_mock: Mock,
    handle_worklog_screen_dismissal_mock: Mock,
    jira_issues: list[JiraIssue],
    jira_worklogs: list[JiraWorklog],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    build_external_url_for_work_log_mock.return_value = 'foo.bar'
    remove_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.root_container.border_subtitle == 'Showing 2 of 2'
        assert screen.root_container.border_title == 'Worklog - key-2'
        assert screen._work_logs_deleted is False
        await pilot.press('tab')
        await pilot.press('d')
        await pilot.press('escape')
        # THEN
        assert isinstance(app.screen, MainScreen)
        handle_worklog_screen_dismissal_mock.assert_called_once_with({'work_logs_deleted': True})


@patch.object(IssueDetailsWidget, '_handle_worklog_screen_dismissal')
@patch('jiratui.widgets.screens.APIController.remove_worklog')
@patch('jiratui.widgets.work_item_details.work_log.build_external_url_for_work_log')
@patch('jiratui.widgets.screens.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_show_and_close_worklog_screen_without_deleting(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    remove_worklog_mock: Mock,
    handle_worklog_screen_dismissal_mock: Mock,
    jira_issues: list[JiraIssue],
    jira_worklogs: list[JiraWorklog],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    build_external_url_for_work_log_mock.return_value = 'foo.bar'
    remove_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen._work_logs_deleted is False
        await pilot.press('escape')
        # THEN
        assert isinstance(app.screen, MainScreen)
        handle_worklog_screen_dismissal_mock.assert_called_once_with({'work_logs_deleted': False})


@patch.object(JiraApp, 'open_url')
@patch('jiratui.widgets.work_item_details.work_log.build_external_url_for_work_log')
@patch('jiratui.widgets.screens.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screens.APIController.get_issue')
@patch('jiratui.widgets.screens.MainScreen._search_work_items')
@patch('jiratui.widgets.screens.MainScreen.get_users')
@patch('jiratui.widgets.screens.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screens.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screens.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_worklog_in_browser(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    get_users_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    open_url_mock: Mock,
    jira_issues: list[JiraIssue],
    jira_worklogs: list[JiraWorklog],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=jira_worklogs, max_results=10, start_at=0, total=2)
    )
    build_external_url_for_work_log_mock.return_value = 'foo.bar'
    async with app.run_test() as pilot:
        search_work_items_mock.return_value = WorkItemSearchResult(
            total=2,
            response=JiraIssueSearchResponse(
                issues=jira_issues, next_page_token=None, is_last=None
            ),
        )
        cast('MainScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN/THEN
        await pilot.press('ctrl+r')
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        await pilot.press('tab')
        await pilot.press('ctrl+o')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        open_url_mock.assert_called_once_with('foo.bar')
