from datetime import datetime, timezone
from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest
from textual.containers import Horizontal
from textual.widgets import Button

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.models import JiraIssue, JiraIssueSearchResponse, JiraWorklog, PaginatedJiraWorklog
from jiratui.widgets.filters import ProjectSelectionInput
from jiratui.widgets.screen import MainScreen, WorkItemSearchResult
from jiratui.widgets.work_item_details.details import IssueDetailsWidget
from jiratui.widgets.work_item_worklog.screens import (
    LogWorkScreen,
    LogWorkScreenMode,
    LogWorkScreenResult,
    WorkItemWorkLogScreen,
    WorkLogCollapsible,
)
from jiratui.widgets.work_item_worklog.widgets import (
    LogDateTimeInput,
    TimeRemainingInput,
    TimeSpentInput,
    WorkDescription,
)


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


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
    jira_issues: list[JiraIssue],
    app,
):
    async with app.run_test():
        await app.push_screen(
            LogWorkScreen(
                '1',
                LogWorkScreenMode.CREATE,
                current_remaining_estimate=jira_issues[1].time_tracking.remaining_estimate,
                current_time_spent=jira_issues[1].time_tracking.time_spent,
                current_date_started='2026-01-01',
                current_description='some text',
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.time_spent_input.value == jira_issues[1].time_tracking.time_spent
        assert screen.time_remaining_input.value == jira_issues[1].time_tracking.remaining_estimate
        assert screen.work_description_input.text == 'some text'
        assert screen.log_date_time_input.value == '2026-01-01'


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_initial_state_without_initial_data(
    current_remaining_estimate: str,
    jira_api_controller,
    jira_issues: list[JiraIssue],
    app,
):
    async with app.run_test():
        await app.push_screen(LogWorkScreen('1', LogWorkScreenMode.CREATE))
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.save_button.disabled is True
        assert screen.log_date_time_input.disabled is True
        assert screen.work_description_input.disabled is True
        assert screen.time_spent_input.value == ''
        assert screen.time_remaining_input.value == ''
        assert screen.work_description_input.text == ''
        assert screen.log_date_time_input.value == datetime.today().strftime('%Y-%m-%d %H:%M')


@pytest.mark.parametrize('current_remaining_estimate', ['', '2h'])
@pytest.mark.asyncio
async def test_log_work_screen_with_valid_time_spent_value(
    current_remaining_estimate: str,
    jira_api_controller,
    app,
):
    async with app.run_test() as pilot:
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value
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
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
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
    async with app.run_test() as pilot:
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
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
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
        assert screen.log_date_time_input.value
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
    async with app.run_test() as pilot:
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value
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
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value
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
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.log_date_time_input.value
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
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
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
            LogWorkScreenResult(
                work_item_key='1',
                mode=LogWorkScreenMode.CREATE,
                worklog_id=None,
                time_spent='1h',
                time_remaining=current_remaining_estimate,
                description='t',
                started='2025-10-18T13:45',
            )
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
        await app.push_screen(
            LogWorkScreen(
                '1', LogWorkScreenMode.CREATE, current_remaining_estimate=current_remaining_estimate
            )
        )
        screen = cast('LogWorkScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.time_spent_input.has_focus is True
        assert isinstance(screen.focused, TimeSpentInput)
        await pilot.press('1')
        await pilot.press('h')
        assert screen.focused.value == '1h'
        assert screen.save_button.disabled is False
        assert screen.log_date_time_input.disabled is False
        assert screen.work_description_input.disabled is False
        assert screen.work_description_input.text == ''
        assert screen.time_remaining_input.value == current_remaining_estimate
        await pilot.press('tab')
        await pilot.press('tab')  # focus is on the date/time widget
        assert isinstance(screen.focused, LogDateTimeInput)
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
        dismiss_mock.assert_called_once_with(None)
        refresh_work_item_details_mock.assert_not_called()


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch('jiratui.widgets.screen.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_with_success(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
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
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        await pilot.press('tab')
        await pilot.press('n')
        assert isinstance(app.screen, LogWorkScreen)
        assert app.screen._current_remaining_estimate is not None
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
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        naive_dt = datetime.fromisoformat(date_time_value)
        # assume the date/time value is in local time and convert to UTC
        started_datetime = naive_dt.replace(
            tzinfo=None
        ).astimezone()  # make it aware of local TZ as defined by the OS
        started_datetime = started_datetime.astimezone(timezone.utc)
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id='key-2',
            started=started_datetime,
            time_spent='1w',
            time_remaining='2w',
            comment='-',
            current_remaining_estimate=jira_issues[1].time_tracking.remaining_estimate,
        )
        fetch_work_logs_mock.assert_has_calls([call(), call(fetch_time_tracking=True)])


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch('jiratui.widgets.screen.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_when_issue_has_no_time_tracking_data(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues: list[JiraIssue],
    app,
):
    # GIVEN
    app.config.search_results_truncate_work_item_summary = 10
    app.config.search_results_style_work_item_status = False
    app.config.search_results_style_work_item_type = False
    app.config.search_results_per_page = 10
    app.config.show_issue_web_links = False
    work_item = jira_issues[1]
    work_item.time_tracking = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
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
        await pilot.press('down')
        await pilot.press('enter')
        await pilot.press('3')
        await pilot.press('tab')
        await pilot.press('ctrl+l')
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        await pilot.press('tab')
        await pilot.press('n')
        assert isinstance(app.screen, LogWorkScreen)
        assert app.screen._current_remaining_estimate is None
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
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        naive_dt = datetime.fromisoformat(date_time_value)
        # assume the date/time value is in local time and convert to UTC
        started_datetime = naive_dt.replace(
            tzinfo=None
        ).astimezone()  # make it aware of local TZ as defined by the OS
        started_datetime = started_datetime.astimezone(timezone.utc)
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id='key-2',
            started=started_datetime,
            time_spent='1w',
            time_remaining='2w',
            comment='-',
            current_remaining_estimate=None,
        )
        fetch_work_logs_mock.assert_has_calls([call(), call(fetch_time_tracking=True)])


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch('jiratui.widgets.screen.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_with_error_adding_new_worklog(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
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
        await pilot.press('ctrl+l')
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        await pilot.press('tab')
        await pilot.press('n')
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
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        naive_dt = datetime.fromisoformat(date_time_value)
        # assume the date/time value is in local time and convert to UTC
        started_datetime = naive_dt.replace(
            tzinfo=None
        ).astimezone()  # make it aware of local TZ as defined by the OS
        started_datetime = started_datetime.astimezone(timezone.utc)
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id='key-2',
            started=started_datetime,
            time_spent='1w',
            time_remaining='2w',
            comment='-',
            current_remaining_estimate=jira_issues[1].time_tracking.remaining_estimate,
        )
        fetch_work_logs_mock.assert_has_calls([call()])


@patch('jiratui.widgets.screen.APIController.add_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_adding_worklog_when_users_clicks_cancel(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
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
        await pilot.press('ctrl+l')
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        await pilot.press('tab')
        await pilot.press('n')
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
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        add_work_item_worklog_mock.assert_not_called()


@patch('jiratui.widgets.work_item_worklog.screens.build_external_url_for_work_log')
@patch('jiratui.widgets.screen.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_modal_to_view_work_logs(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
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


@patch.object(WorkItemWorkLogScreen, '_delete_log_entry')
@patch('jiratui.widgets.work_item_worklog.screens.build_external_url_for_work_log')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_delete_worklog(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    delete_log_entry_mock: Mock,
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
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        assert screen.root_container.border_title == 'Worklog - key-2'
        assert screen._work_logs_deleted is False
        await pilot.press('tab')
        await pilot.press('d')
        # THEN
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        await app.workers.wait_for_complete()
        await pilot.pause()
        delete_log_entry_mock.assert_called_once()


@patch.object(WorkItemWorkLogScreen, '_delete_log_entry')
@patch('jiratui.widgets.screen.APIController.remove_worklog')
@patch('jiratui.widgets.work_item_worklog.screens.build_external_url_for_work_log')
@patch('jiratui.widgets.screen.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_delete_worklog_and_close_worklog_screen(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
    search_work_items_mock: AsyncMock,
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    build_external_url_for_work_log_mock: Mock,
    remove_worklog_mock: Mock,
    delete_log_entry_mock: Mock,
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
        assert screen.root_container.border_title == 'Worklog - key-2'
        assert screen._work_logs_deleted is False
        await pilot.press('tab')
        await pilot.press('d')
        await pilot.press('escape')
        # THEN
        assert isinstance(app.screen, MainScreen)
        delete_log_entry_mock.assert_called_once()


@patch('jiratui.widgets.screen.APIController.remove_worklog')
@patch('jiratui.widgets.work_item_worklog.screens.build_external_url_for_work_log')
@patch('jiratui.widgets.screen.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_show_and_close_worklog_screen_without_deleting(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
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
        assert screen._work_logs_deleted is False
        await pilot.press('escape')
        # THEN
        assert isinstance(app.screen, MainScreen)


@patch.object(JiraApp, 'open_url')
@patch('jiratui.widgets.work_item_worklog.screens.build_external_url_for_work_log')
@patch('jiratui.widgets.screen.APIController.get_work_item_worklog')
@patch('jiratui.widgets.screen.APIController.get_issue')
@patch('jiratui.widgets.screen.MainScreen._search_work_items')
@patch('jiratui.widgets.screen.MainScreen.fetch_statuses')
@patch('jiratui.widgets.screen.MainScreen.fetch_issue_types')
@patch('jiratui.widgets.screen.MainScreen.fetch_projects')
@pytest.mark.asyncio
async def test_open_worklog_in_browser(
    search_projects_mock: AsyncMock,
    fetch_issue_types_mock: AsyncMock,
    fetch_statuses_mock: AsyncMock,
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


@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_fetch_work_logs_without_initial_time_tracking_set(
    get_issue_mock: AsyncMock, get_work_item_worklog_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, None))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking is None
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')


@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_fetch_work_logs_without_initial_time_tracking_set_fail_to_get_issue(
    get_issue_mock: AsyncMock, get_work_item_worklog_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, None))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking is None
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')


@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_fetch_work_logs_with_initial_time_tracking_set(
    get_issue_mock: AsyncMock, get_work_item_worklog_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking == work_item.time_tracking
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')


@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_fetch_work_logs_work_item_has_worklogs(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(
            logs=[
                JiraWorklog(id='1', issue_id=work_item.id, author=work_item.reporter),
            ],
            max_results=1,
            start_at=0,
            total=1,
        )
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking == work_item.time_tracking
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        assert len(screen.work_log_items_container.children) == 1


@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_fetch_work_logs_with_fetch_time_tracking_true(
    get_issue_mock: AsyncMock, get_work_item_worklog_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, None))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await screen._fetch_work_logs(fetch_time_tracking=True)
        # THEN
        get_issue_mock.assert_has_calls([call(issue_id_or_key=work_item.key)])
        assert screen._work_item_time_tracking == work_item.time_tracking


@patch.object(WorkItemWorkLogScreen, '_add_worklog_entry')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_log_work_in_create_mode(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    add_worklog_entry_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.CREATE,
        work_item_key=work_item.key,
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await screen._log_work(screen_result)
        # THEN
        get_issue_mock.assert_not_called()
        add_worklog_entry_mock.assert_called_once_with(
            work_item_key=work_item.key, data=screen_result
        )


@patch.object(WorkItemWorkLogScreen, '_update_worklog_entry')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_log_work_in_update_mode(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    update_worklog_entry_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.UPDATE,
        work_item_key=work_item.key,
        worklog_id='1',
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await screen._log_work(screen_result)
        # THEN
        get_issue_mock.assert_not_called()
        update_worklog_entry_mock.assert_called_once_with(worklog_id='1', data=screen_result)


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'add_work_item_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_add_worklog_entry_without_work_item_key(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.CREATE,
        work_item_key=work_item.key,
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._add_worklog_entry('', screen_result)  # type:ignore[func-returns-value]
        # THEN
        get_issue_mock.assert_not_called()
        add_work_item_worklog_mock.assert_not_called()
        fetch_work_logs_mock.assert_has_calls([call()])
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'add_work_item_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_add_worklog_entry_without_time_spent(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.CREATE,
        work_item_key=work_item.key,
        time_spent='',
        started='2026-01-01 12:30',
    )
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._add_worklog_entry(work_item.key, screen_result)  # type:ignore[func-returns-value]
        # THEN
        get_issue_mock.assert_not_called()
        add_work_item_worklog_mock.assert_not_called()
        fetch_work_logs_mock.assert_has_calls([call()])
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'add_work_item_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_add_worklog_entry(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.CREATE,
        work_item_key=work_item.key,
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    add_work_item_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._add_worklog_entry(work_item.key, screen_result)  # type:ignore[func-returns-value]
        # THEN
        get_issue_mock.assert_not_called()
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id=work_item.key,
            started=datetime.fromisoformat(screen_result.started).astimezone(timezone.utc),
            time_spent=screen_result.time_spent,
            time_remaining=screen_result.time_remaining,
            comment=screen_result.description,
            current_remaining_estimate=screen._work_item_time_tracking.remaining_estimate,
        )
        fetch_work_logs_mock.assert_has_calls([call(), call(fetch_time_tracking=True)])
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'add_work_item_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_add_worklog_entry_fails_to_add_entry(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    add_work_item_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.CREATE,
        work_item_key=work_item.key,
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    add_work_item_worklog_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._add_worklog_entry(work_item.key, screen_result)  # type:ignore[func-returns-value]
        # THEN
        get_issue_mock.assert_not_called()
        add_work_item_worklog_mock.assert_called_once_with(
            issue_key_or_id=work_item.key,
            started=datetime.fromisoformat(screen_result.started).astimezone(timezone.utc),
            time_spent=screen_result.time_spent,
            time_remaining=screen_result.time_remaining,
            comment=screen_result.description,
            current_remaining_estimate=screen._work_item_time_tracking.remaining_estimate,
        )
        fetch_work_logs_mock.assert_has_calls([call()])
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'update_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_update_worklog_entry(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    update_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.UPDATE,
        worklog_id='1',
        work_item_key=work_item.key,
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    update_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._update_worklog_entry('1', screen_result)  # type:ignore[func-returns-value]
        # THEN
        get_issue_mock.assert_not_called()
        update_worklog_mock.assert_called_once_with(
            issue_key_or_id=work_item.key,
            worklog_id='1',
            started=datetime.fromisoformat(screen_result.started).astimezone(timezone.utc),
            time_spent=screen_result.time_spent,
            time_remaining=screen_result.time_remaining,
            comment=screen_result.description,
            remaining_estimate=screen._work_item_time_tracking.remaining_estimate,
        )
        fetch_work_logs_mock.assert_has_calls([call(), call(fetch_time_tracking=True)])
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'update_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_update_worklog_entry_without_worklog_id(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    update_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    screen_result = LogWorkScreenResult(
        mode=LogWorkScreenMode.UPDATE,
        worklog_id='1',
        work_item_key=work_item.key,
        time_spent='1h',
        started='2026-01-01 12:30',
    )
    update_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._update_worklog_entry('', screen_result)  # type:ignore[func-returns-value]
        # THEN
        get_issue_mock.assert_not_called()
        update_worklog_mock.assert_not_called()
        fetch_work_logs_mock.assert_has_calls([call()])
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'remove_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_delete_log_entry(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    remove_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    remove_worklog_mock.return_value = APIControllerResponse()
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._delete_log_entry('1')
        # THEN
        get_issue_mock.assert_not_called()
        remove_worklog_mock.assert_called_once_with(work_item.key, '1')
        fetch_work_logs_mock.assert_has_calls([call(), call(fetch_time_tracking=True)])
        assert screen._work_logs_deleted is True
        assert result is None


@patch.object(WorkItemWorkLogScreen, '_fetch_work_logs')
@patch.object(APIController, 'remove_worklog')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_delete_log_entry_fails_to_delete(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    remove_worklog_mock: AsyncMock,
    fetch_work_logs_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(logs=[], max_results=0, start_at=0, total=0)
    )
    remove_worklog_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        result = await screen._delete_log_entry('1')
        # THEN
        get_issue_mock.assert_not_called()
        remove_worklog_mock.assert_called_once_with(work_item.key, '1')
        fetch_work_logs_mock.assert_has_calls([call()])
        assert screen._work_logs_deleted is False
        assert result is None


@patch.object(JiraApp, 'open_url')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_open_url(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    open_url_mock: Mock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(
            logs=[
                JiraWorklog(id='1', issue_id=work_item.id, author=work_item.reporter),
            ],
            max_results=1,
            start_at=0,
            total=1,
        )
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('tab')
        await pilot.press('ctrl+o')
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking == work_item.time_tracking
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        assert len(screen.work_log_items_container.children) == 1
        open_url_mock.assert_called_once()


@patch.object(JiraApp, 'open_url')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_edit_entry(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    open_url_mock: Mock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(
            logs=[
                JiraWorklog(id='1', issue_id=work_item.id, author=work_item.reporter),
            ],
            max_results=1,
            start_at=0,
            total=1,
        )
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('tab')
        await pilot.press('ctrl+e')
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking == work_item.time_tracking
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        assert len(screen.work_log_items_container.children) == 1
        assert isinstance(app.screen, LogWorkScreen)


@patch.object(WorkLogCollapsible, '_edit_worklog_entry')
@patch.object(APIController, 'get_work_item_worklog')
@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_work_log_screen_edit_entry_press_save(
    get_issue_mock: AsyncMock,
    get_work_item_worklog_mock: AsyncMock,
    edit_worklog_entry_mock: AsyncMock,
    jira_issues,
    mock_configuration,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    get_work_item_worklog_mock.return_value = APIControllerResponse(
        result=PaginatedJiraWorklog(
            logs=[
                JiraWorklog(id='1', issue_id=work_item.id, author=work_item.reporter),
            ],
            max_results=1,
            start_at=0,
            total=1,
        )
    )
    mock_configuration.jira_base_url = 'http://foo.bar'
    async with app.run_test() as pilot:
        await app.push_screen(WorkItemWorkLogScreen(work_item.key, work_item.time_tracking))
        screen = cast('WorkItemWorkLogScreen', app.screen)  # type:ignore[name-defined] # noqa: F821
        # WHEN
        await pilot.press('tab')
        await pilot.press('ctrl+e')
        await pilot.press('1')
        await pilot.press('h')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('tab')
        await pilot.press('a')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        get_issue_mock.assert_not_called()
        assert screen._work_item_time_tracking == work_item.time_tracking
        assert screen.query_one('#time-tracking-container', Horizontal) is not None
        get_work_item_worklog_mock.assert_called_once_with('key-2')
        assert len(screen.work_log_items_container.children) == 1
        assert isinstance(app.screen, WorkItemWorkLogScreen)
        edit_worklog_entry_mock.assert_called_once()
