from unittest.mock import AsyncMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraIssueSearchResponse
from jiratui.widgets.screens.clone import CloneWorkItemRequest, CloneWorkItemScreen


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_clone_screen(get_issue_mock: AsyncMock, jira_issues, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    async with app.run_test():
        screen = CloneWorkItemScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.summary.value == jira_issues[1].summary
        assert screen.summary.disabled is False
        assert screen.clone_button.disabled is False


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_clone_screen_source_item_not_found(get_issue_mock: AsyncMock, jira_issues, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(result=JiraIssueSearchResponse(issues=[]))
    async with app.run_test():
        screen = CloneWorkItemScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.summary.value == ''
        assert screen.summary.disabled is True
        assert screen.clone_button.disabled is True


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_clone_screen_source_item_not_found_with_error(
    get_issue_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        screen = CloneWorkItemScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.summary.value == ''
        assert screen.summary.disabled is True
        assert screen.clone_button.disabled is True


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_clone_screen_press_clone_button(get_issue_mock: AsyncMock, jira_issues, app):
    # GIVEN
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    async with app.run_test() as pilot:
        screen = CloneWorkItemScreen('WI-1')
        screen.dismiss = Mock()
        # WHEN
        await app.push_screen(screen)
        await pilot.press('a')
        await pilot.press('tab')
        await pilot.press('enter')
        # THEN
        assert isinstance(screen.dismiss.call_args[0][0], CloneWorkItemRequest)
        assert screen.dismiss.call_args[0][0].summary == 'qwertya'
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
