from unittest.mock import AsyncMock, Mock, patch

import pytest

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraUser, Votes
from jiratui.widgets.screens.votes import WorkItemVotesScreen


@patch.object(APIController, 'get_work_item_votes')
@pytest.mark.asyncio
async def test_open_voting_screen_user_has_voted(
    get_work_item_votes_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_votes_mock.return_value = APIControllerResponse(
        success=True,
        result=Votes(
            has_voted=True,
            votes=1,
            voters=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test():
        screen = WorkItemVotesScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Votes - WI-1'
        assert screen.vote_status_field.content == 'Voted'
        assert screen.vote_status_field.styles.display == 'block'
        assert screen.voting_enabled is False
        assert screen.unvoting_enabled is True
        assert screen.datatable.border_subtitle == '1 votes'


@patch.object(APIController, 'get_work_item_votes')
@pytest.mark.asyncio
async def test_open_voting_screen_user_has_not_voted_with_voters(
    get_work_item_votes_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_votes_mock.return_value = APIControllerResponse(
        success=True,
        result=Votes(
            has_voted=False,
            votes=1,
            voters=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test():
        screen = WorkItemVotesScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Votes - WI-1'
        assert screen.vote_status_field.content == ''
        assert screen.vote_status_field.styles.display == 'none'
        assert screen.datatable.border_title == 'Voters'
        assert screen.datatable.border_subtitle == '1 votes'
        assert len(screen.datatable.rows) == 1
        get_work_item_votes_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_votes')
@pytest.mark.asyncio
async def test_open_voting_screen_user_has_not_voted_without_voters(
    get_work_item_votes_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_votes_mock.return_value = APIControllerResponse(
        success=True,
        result=Votes(
            has_voted=False,
            votes=0,
            voters=[],
        ),
    )
    async with app.run_test():
        screen = WorkItemVotesScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Votes - WI-1'
        assert screen.vote_status_field.content == ''
        assert screen.vote_status_field.styles.display == 'none'
        assert not screen.datatable.display
        assert not screen.datatable.border_title
        assert not screen.datatable.border_subtitle
        assert len(screen.datatable.rows) == 0
        assert screen.message.content == 'The work item does not have votes yet.'
        assert screen.voting_enabled is True
        assert screen.unvoting_enabled is False
        get_work_item_votes_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_votes')
@pytest.mark.asyncio
async def test_open_voting_screen_fetching_voting_data_fails(
    get_work_item_votes_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_votes_mock.return_value = APIControllerResponse(success=False)
    async with app.run_test():
        screen = WorkItemVotesScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        # THEN
        assert screen.vertical_container.border_title == 'Votes - WI-1'
        assert screen.vote_status_field.content == ''
        assert screen.vote_status_field.styles.display == 'none'
        assert not screen.datatable.display
        assert not screen.datatable.border_title
        assert not screen.datatable.border_subtitle
        assert len(screen.datatable.rows) == 0
        assert screen.message.content == 'Failed to retrieve voting data'
        assert screen.message.display is True
        assert screen.voting_enabled is True
        assert screen.unvoting_enabled is False
        get_work_item_votes_mock.assert_awaited_once_with(issue_id_or_key='WI-1')


@patch.object(APIController, 'get_work_item_votes')
@pytest.mark.asyncio
async def test_open_voting_screen_user_wants_to_vote(
    get_work_item_votes_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_votes_mock.return_value = APIControllerResponse(
        success=True,
        result=Votes(
            has_voted=False,
            votes=1,
            voters=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test() as pilot:
        screen = WorkItemVotesScreen('WI-1')
        await app.push_screen(screen)
        screen.dismiss = Mock()
        # WHEN
        await pilot.press('a')
        # THEN
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
        assert screen.dismiss.call_args[0][0].vote is True
        assert screen.dismiss.call_args[0][0].update is True


@patch.object(APIController, 'get_work_item_votes')
@pytest.mark.asyncio
async def test_open_voting_screen_user_wants_to_unvote(
    get_work_item_votes_mock: AsyncMock, jira_issues, app
):
    # GIVEN
    get_work_item_votes_mock.return_value = APIControllerResponse(
        success=True,
        result=Votes(
            has_voted=True,
            votes=1,
            voters=[
                JiraUser(
                    account_id='5b10a2844c20165700ede21g',
                    active=False,
                    display_name='Bart',
                )
            ],
        ),
    )
    async with app.run_test() as pilot:
        screen = WorkItemVotesScreen('WI-1')
        await app.push_screen(screen)
        screen.dismiss = Mock()
        # WHEN
        await pilot.press('x')
        # THEN
        assert screen.dismiss.call_args[0][0].work_item_key == 'WI-1'
        assert screen.dismiss.call_args[0][0].vote is False
        assert screen.dismiss.call_args[0][0].update is True
