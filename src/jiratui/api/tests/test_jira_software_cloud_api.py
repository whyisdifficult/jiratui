from unittest.mock import AsyncMock, call, patch

import httpx
import pytest
import respx

from jiratui.api.api import JiraSoftwareCloudAPI
from jiratui.utils.test_utilities import get_url_pattern


@pytest.mark.asyncio
@respx.mock
async def test_get_boards_with_default_parameters(jira_api_software_cloud: JiraSoftwareCloudAPI):
    # GIVEN
    route = respx.get(get_url_pattern('board'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': False,
                'maxResults': 2,
                'startAt': 1,
                'total': 5,
                'values': [
                    {'id': 84, 'name': 'scrum board', 'type': 'scrum'},
                    {'id': 92, 'name': 'kanban board', 'type': 'kanban'},
                ],
            },
        )
    )
    # WHEN
    result = await jira_api_software_cloud.get_boards()
    # THEN
    assert route.calls.last.request.url.path == '/rest/agile/1.0/board'
    assert route.calls.last.request.url.params.get('maxResults') == '100'
    assert set(route.calls.last.request.url.params.keys()) == {'maxResults'}
    assert result == {
        'isLast': False,
        'maxResults': 2,
        'startAt': 1,
        'total': 5,
        'values': [
            {'id': 84, 'name': 'scrum board', 'type': 'scrum'},
            {'id': 92, 'name': 'kanban board', 'type': 'kanban'},
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_boards_with_parameters(jira_api_software_cloud: JiraSoftwareCloudAPI):
    # GIVEN
    route = respx.get(get_url_pattern('board'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': False,
                'maxResults': 2,
                'startAt': 1,
                'total': 5,
                'values': [
                    {'id': 84, 'name': 'scrum board', 'type': 'scrum'},
                    {'id': 92, 'name': 'kanban board', 'type': 'kanban'},
                ],
            },
        )
    )
    # WHEN
    result = await jira_api_software_cloud.get_boards(
        offset=1, limit=10, project_key_or_id='P1', board_name='scrum board', board_type='scrum'
    )
    # THEN
    assert route.calls.last.request.url.path == '/rest/agile/1.0/board'
    assert route.calls.last.request.url.params.get('maxResults') == '10'
    assert route.calls.last.request.url.params.get('startAt') == '1'
    assert route.calls.last.request.url.params.get('type') == 'scrum'
    assert route.calls.last.request.url.params.get('name') == 'scrum board'
    assert route.calls.last.request.url.params.get('projectKeyOrId') == 'P1'
    assert set(route.calls.last.request.url.params.keys()) == {
        'maxResults',
        'startAt',
        'type',
        'name',
        'projectKeyOrId',
    }
    assert result == {
        'isLast': False,
        'maxResults': 2,
        'startAt': 1,
        'total': 5,
        'values': [
            {'id': 84, 'name': 'scrum board', 'type': 'scrum'},
            {'id': 92, 'name': 'kanban board', 'type': 'kanban'},
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_board_sprints_with_default_parameters(
    jira_api_software_cloud: JiraSoftwareCloudAPI,
):
    # GIVEN
    route = respx.get(get_url_pattern('board/1/sprint'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': False,
                'maxResults': 2,
                'startAt': 1,
                'total': 5,
                'values': [
                    {
                        'id': 37,
                        'state': 'closed',
                        'name': 'sprint 1',
                        'startDate': '2015-04-11T15:22:00.000+10:00',
                        'endDate': '2015-04-20T01:22:00.000+10:00',
                        'completeDate': '2015-04-20T11:04:00.000+10:00',
                        'originBoardId': 5,
                        'goal': 'sprint 1 goal',
                    },
                    {'id': 72, 'state': 'future', 'name': 'sprint 2', 'goal': 'sprint 2 goal'},
                ],
            },
        )
    )
    # WHEN
    result = await jira_api_software_cloud.get_board_sprints(1)
    # THEN
    assert route.calls.last.request.url.path == '/rest/agile/1.0/board/1/sprint'
    assert route.calls.last.request.url.params.get('maxResults') == '100'
    assert set(route.calls.last.request.url.params.keys()) == {'maxResults'}
    assert result == {
        'isLast': False,
        'maxResults': 2,
        'startAt': 1,
        'total': 5,
        'values': [
            {
                'id': 37,
                'state': 'closed',
                'name': 'sprint 1',
                'startDate': '2015-04-11T15:22:00.000+10:00',
                'endDate': '2015-04-20T01:22:00.000+10:00',
                'completeDate': '2015-04-20T11:04:00.000+10:00',
                'originBoardId': 5,
                'goal': 'sprint 1 goal',
            },
            {'id': 72, 'state': 'future', 'name': 'sprint 2', 'goal': 'sprint 2 goal'},
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_board_sprints_with_parameters(jira_api_software_cloud: JiraSoftwareCloudAPI):
    # GIVEN
    route = respx.get(get_url_pattern('board/1/sprint'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': False,
                'maxResults': 2,
                'startAt': 1,
                'total': 5,
                'values': [
                    {
                        'id': 37,
                        'state': 'closed',
                        'name': 'sprint 1',
                        'startDate': '2015-04-11T15:22:00.000+10:00',
                        'endDate': '2015-04-20T01:22:00.000+10:00',
                        'completeDate': '2015-04-20T11:04:00.000+10:00',
                        'originBoardId': 5,
                        'goal': 'sprint 1 goal',
                    },
                    {'id': 72, 'state': 'future', 'name': 'sprint 2', 'goal': 'sprint 2 goal'},
                ],
            },
        )
    )
    # WHEN
    await jira_api_software_cloud.get_board_sprints(1, offset=1, limit=10, state='closed,future')
    # THEN
    assert route.calls.last.request.url.path == '/rest/agile/1.0/board/1/sprint'
    assert route.calls.last.request.url.params.get('maxResults') == '10'
    assert route.calls.last.request.url.params.get('state') == 'closed,future'
    assert route.calls.last.request.url.params.get('startAt') == '1'
    assert set(route.calls.last.request.url.params.keys()) == {'maxResults', 'state', 'startAt'}


@patch.object(JiraSoftwareCloudAPI, 'get_board_sprints')
@pytest.mark.asyncio
async def test_get_boards_sprints_with_default_parameters(
    get_board_sprints_mock: AsyncMock, jira_api_software_cloud: JiraSoftwareCloudAPI
):
    # GIVEN
    get_board_sprints_mock.side_effect = [
        {'isLast': False, 'maxResults': 10, 'startAt': 0, 'total': 0, 'values': []},
        {
            'isLast': False,
            'maxResults': 1,
            'startAt': 1,
            'total': 1,
            'values': [
                {
                    'id': 37,
                    'state': 'closed',
                    'name': 'sprint 1',
                    'startDate': '2015-04-11T15:22:00.000+10:00',
                    'endDate': '2015-04-20T01:22:00.000+10:00',
                    'completeDate': '2015-04-20T11:04:00.000+10:00',
                    'originBoardId': 5,
                    'goal': 'sprint 1 goal',
                }
            ],
        },
    ]
    # WHEN
    result = await jira_api_software_cloud.get_boards_sprints([1, 2])
    # THEN
    assert result == [
        {
            'id': 37,
            'state': 'closed',
            'name': 'sprint 1',
            'startDate': '2015-04-11T15:22:00.000+10:00',
            'endDate': '2015-04-20T01:22:00.000+10:00',
            'completeDate': '2015-04-20T11:04:00.000+10:00',
            'originBoardId': 5,
            'goal': 'sprint 1 goal',
        }
    ]
    get_board_sprints_mock.assert_has_calls([call(1, state=None), call(2, state=None)])


@patch.object(JiraSoftwareCloudAPI, 'get_board_sprints')
@pytest.mark.asyncio
async def test_get_boards_sprints_with_parameters(
    get_board_sprints_mock: AsyncMock, jira_api_software_cloud: JiraSoftwareCloudAPI
):
    # GIVEN
    get_board_sprints_mock.side_effect = [
        {'isLast': False, 'maxResults': 10, 'startAt': 0, 'total': 0, 'values': []},
        {
            'isLast': False,
            'maxResults': 1,
            'startAt': 1,
            'total': 1,
            'values': [
                {
                    'id': 37,
                    'state': 'closed',
                    'name': 'sprint 1',
                    'startDate': '2015-04-11T15:22:00.000+10:00',
                    'endDate': '2015-04-20T01:22:00.000+10:00',
                    'completeDate': '2015-04-20T11:04:00.000+10:00',
                    'originBoardId': 5,
                    'goal': 'sprint 1 goal',
                }
            ],
        },
    ]
    # WHEN
    result = await jira_api_software_cloud.get_boards_sprints([1, 2], state='active,future')
    # THEN
    assert result == [
        {
            'id': 37,
            'state': 'closed',
            'name': 'sprint 1',
            'startDate': '2015-04-11T15:22:00.000+10:00',
            'endDate': '2015-04-20T01:22:00.000+10:00',
            'completeDate': '2015-04-20T11:04:00.000+10:00',
            'originBoardId': 5,
            'goal': 'sprint 1 goal',
        }
    ]
    get_board_sprints_mock.assert_has_calls(
        [call(1, state='active,future'), call(2, state='active,future')]
    )


@patch.object(JiraSoftwareCloudAPI, 'get_board_sprints')
@patch.object(JiraSoftwareCloudAPI, 'get_boards')
@pytest.mark.asyncio
async def test_get_project_sprints_with_default_parameters(
    get_boards_mock: AsyncMock,
    get_board_sprints_mock: AsyncMock,
    jira_api_software_cloud: JiraSoftwareCloudAPI,
):
    # GIVEN
    get_boards_mock.return_value = {
        'isLast': False,
        'maxResults': 2,
        'startAt': 1,
        'total': 5,
        'values': [
            {'id': 84, 'name': 'scrum board', 'type': 'scrum'},
            {'id': 92, 'name': 'kanban board', 'type': 'kanban'},
        ],
    }
    get_board_sprints_mock.side_effect = [
        {'isLast': False, 'maxResults': 10, 'startAt': 0, 'total': 0, 'values': []},
        {
            'isLast': False,
            'maxResults': 1,
            'startAt': 1,
            'total': 1,
            'values': [
                {
                    'id': 37,
                    'state': 'closed',
                    'name': 'sprint 1',
                    'startDate': '2015-04-11T15:22:00.000+10:00',
                    'endDate': '2015-04-20T01:22:00.000+10:00',
                    'completeDate': '2015-04-20T11:04:00.000+10:00',
                    'originBoardId': 5,
                    'goal': 'sprint 1 goal',
                }
            ],
        },
    ]
    # WHEN
    result = await jira_api_software_cloud.get_project_sprints('P1')
    # THEN
    assert result == [
        {
            'id': 37,
            'state': 'closed',
            'name': 'sprint 1',
            'startDate': '2015-04-11T15:22:00.000+10:00',
            'endDate': '2015-04-20T01:22:00.000+10:00',
            'completeDate': '2015-04-20T11:04:00.000+10:00',
            'originBoardId': 5,
            'goal': 'sprint 1 goal',
        }
    ]
    get_boards_mock.assert_awaited_once()
    get_board_sprints_mock.assert_has_calls([call(84, state=None), call(92, state=None)])


@patch.object(JiraSoftwareCloudAPI, 'get_board_sprints')
@patch.object(JiraSoftwareCloudAPI, 'get_boards')
@pytest.mark.asyncio
async def test_get_project_sprints_with_parameters(
    get_boards_mock: AsyncMock,
    get_board_sprints_mock: AsyncMock,
    jira_api_software_cloud: JiraSoftwareCloudAPI,
):
    # GIVEN
    get_boards_mock.return_value = {
        'isLast': False,
        'maxResults': 2,
        'startAt': 1,
        'total': 5,
        'values': [
            {'id': 84, 'name': 'scrum board', 'type': 'scrum'},
            {'id': 92, 'name': 'kanban board', 'type': 'kanban'},
        ],
    }
    get_board_sprints_mock.side_effect = [
        {'isLast': False, 'maxResults': 10, 'startAt': 0, 'total': 0, 'values': []},
        {
            'isLast': False,
            'maxResults': 1,
            'startAt': 1,
            'total': 1,
            'values': [
                {
                    'id': 37,
                    'state': 'closed',
                    'name': 'sprint 1',
                    'startDate': '2015-04-11T15:22:00.000+10:00',
                    'endDate': '2015-04-20T01:22:00.000+10:00',
                    'completeDate': '2015-04-20T11:04:00.000+10:00',
                    'originBoardId': 5,
                    'goal': 'sprint 1 goal',
                }
            ],
        },
    ]
    # WHEN
    result = await jira_api_software_cloud.get_project_sprints('P1', state='active,future')
    # THEN
    assert result == [
        {
            'id': 37,
            'state': 'closed',
            'name': 'sprint 1',
            'startDate': '2015-04-11T15:22:00.000+10:00',
            'endDate': '2015-04-20T01:22:00.000+10:00',
            'completeDate': '2015-04-20T11:04:00.000+10:00',
            'originBoardId': 5,
            'goal': 'sprint 1 goal',
        }
    ]
    get_boards_mock.assert_awaited_once()
    get_board_sprints_mock.assert_has_calls(
        [call(84, state='active,future'), call(92, state='active,future')]
    )


@patch.object(JiraSoftwareCloudAPI, 'get_board_sprints')
@patch.object(JiraSoftwareCloudAPI, 'get_boards')
@pytest.mark.asyncio
async def test_get_project_sprints_no_project_boards_found(
    get_boards_mock: AsyncMock,
    get_board_sprints_mock: AsyncMock,
    jira_api_software_cloud: JiraSoftwareCloudAPI,
):
    # GIVEN
    get_boards_mock.return_value = {
        'isLast': False,
        'maxResults': 2,
        'startAt': 1,
        'total': 5,
        'values': [],
    }
    # WHEN
    result = await jira_api_software_cloud.get_project_sprints('P1')
    # THEN
    assert result == []
    get_boards_mock.assert_awaited_once()
    get_board_sprints_mock.assert_not_called()
