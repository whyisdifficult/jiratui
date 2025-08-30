import json
from unittest.mock import Mock, patch

import httpx
import pytest
import respx

from jiratui.api.api import JiraAPI
from jiratui.api.utils import build_issue_search_jql
from jiratui.models import WorkItemsSearchOrderBy
from jiratui.utils.test_utilities import get_url_pattern, load_json_response


@pytest.mark.asyncio
@respx.mock
async def test_status(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('status'))
    route.mock(return_value=httpx.Response(200, json=[]))

    # WHEN
    result = await jira_api.status()
    # THEN
    assert route.called
    assert route.calls.last.request.url.path == '/rest/api/3/status'
    assert result == []


@pytest.mark.asyncio
@respx.mock
async def test_get_project_statuses(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1/statuses'))
    route.mock(
        return_value=httpx.Response(200, json=load_json_response(__file__, 'project_statuses.json'))
    )

    # WHEN
    result = await jira_api.get_project_statuses('P1')
    # THEN
    assert route.called
    assert isinstance(result, list)
    assert result == [
        {
            'id': '3',
            'name': 'Task',
            'statuses': [
                {
                    'description': 'The issue is currently being worked on.',
                    'id': '10000',
                    'name': 'In Progress',
                }
            ],
            'subtask': False,
        }
    ]


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_types_for_user(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issuetype'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    'description': 'A task that needs to be done.',
                    'id': '3',
                    'name': 'Task',
                    'subtask': False,
                }
            ],
        )
    )

    # WHEN
    result = await jira_api.get_issue_types_for_user()
    # THEN
    assert route.called
    assert isinstance(result, list)
    assert result == [
        {
            'description': 'A task that needs to be done.',
            'id': '3',
            'name': 'Task',
            'subtask': False,
        }
    ]


@pytest.mark.asyncio
@respx.mock
async def test_get_statuses(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('statuses/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'statuses.json'),
        )
    )

    # WHEN
    result = await jira_api.get_statuses('P1')
    # THEN
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert 'projectId=' in request_url
    assert isinstance(result, dict)
    assert result == {
        'isLast': True,
        'maxResults': 2,
        'nextPage': 'https://your-domain.atlassian.net/rest/api/3/statuses/search?startAt=2&maxResults=2',
        'startAt': 0,
        'total': 5,
        'values': [
            {
                'description': 'The issue is resolved',
                'id': '1000',
                'name': 'Finished',
                'scope': {'project': {'id': '1'}, 'type': 'PROJECT'},
                'statusCategory': 'DONE',
            }
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_statuses_with_offset_and_limit(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('statuses/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'statuses.json'),
        )
    )

    # WHEN
    result = await jira_api.get_statuses('P1', 3, 15)
    # THEN
    request_url = str(route.calls.last.request.url)
    assert 'startAt=3' in request_url
    assert 'maxResults=15' in request_url
    assert 'projectId=P1' in request_url
    assert isinstance(result, dict)
    assert result == {
        'isLast': True,
        'maxResults': 2,
        'nextPage': 'https://your-domain.atlassian.net/rest/api/3/statuses/search?startAt=2&maxResults=2',
        'startAt': 0,
        'total': 5,
        'values': [
            {
                'description': 'The issue is resolved',
                'id': '1000',
                'name': 'Finished',
                'scope': {'project': {'id': '1'}, 'type': 'PROJECT'},
                'statusCategory': 'DONE',
            }
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_project(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'project.json'),
        )
    )

    # WHEN
    result = await jira_api.get_project('P1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/project/P1'
    assert isinstance(result, dict)
    assert result == {
        'assigneeType': 'PROJECT_LEAD',
        'components': [
            {
                'ari': 'ari:cloud:compass:fdb3fdec-4e70-be56-11ee-0242ac120002:component/fdb3fdec-4e70-11ee-be56-0242ac120002/fdb3fdec-11ee-4e70-be56-0242ac120002',
                'assignee': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                    'self': 'https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g',
                },
                'assigneeType': 'PROJECT_LEAD',
                'description': 'This is a Jira component',
                'id': '10000',
                'isAssigneeTypeValid': False,
                'lead': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                    'self': 'https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g',
                },
                'metadata': {'icon': 'https://www.example.com/icon.png'},
                'name': 'Component 1',
                'project': 'HSP',
                'projectId': 10000,
                'realAssignee': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                    'self': 'https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g',
                },
                'realAssigneeType': 'PROJECT_LEAD',
                'self': 'https://your-domain.atlassian.net/rest/api/3/component/10000',
            }
        ],
        'description': 'This project was created as an example for REST.',
        'email': 'from-jira@example.com',
        'id': '10000',
        'insight': {'lastIssueUpdateTime': '2021-04-22T05:37:05.000+0000', 'totalIssueCount': 100},
        'issueTypes': [
            {
                'avatarId': 1,
                'description': 'A task that needs to be done.',
                'hierarchyLevel': 0,
                'iconUrl': 'https://your-domain.atlassian.net/secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype",',
                'id': '3',
                'name': 'Task',
                'self': 'https://your-domain.atlassian.net/rest/api/3/issueType/3',
                'subtask': False,
            },
            {
                'avatarId': 10002,
                'description': 'A problem with the software.',
                'entityId': '9d7dd6f7-e8b6-4247-954b-7b2c9b2a5ba2',
                'hierarchyLevel': 0,
                'iconUrl': 'https://your-domain.atlassian.net/secure/viewavatar?size=xsmall&avatarId=10316&avatarType=issuetype",',
                'id': '1',
                'name': 'Bug',
                'scope': {'project': {'id': '10000'}, 'type': 'PROJECT'},
                'self': 'https://your-domain.atlassian.net/rest/api/3/issueType/1',
                'subtask': False,
            },
        ],
        'key': 'EX',
        'lead': {
            'accountId': '5b10a2844c20165700ede21g',
            'accountType': 'atlassian',
            'active': False,
            'displayName': 'Mia Krystof',
            'key': '',
            'name': '',
            'self': 'https://your-domain.atlassian.net/rest/api/3/user?accountId=5b10a2844c20165700ede21g',
        },
        'name': 'Example',
        'projectCategory': {
            'description': 'First Project Category',
            'id': '10000',
            'name': 'FIRST',
            'self': 'https://your-domain.atlassian.net/rest/api/3/projectCategory/10000',
        },
        'properties': {'propertyKey': 'propertyValue'},
        'roles': {
            'Developers': 'https://your-domain.atlassian.net/rest/api/3/project/EX/role/10000'
        },
        'self': 'https://your-domain.atlassian.net/rest/api/3/project/EX',
        'simplified': False,
        'style': 'classic',
        'url': 'https://www.example.com',
        'versions': [],
    }


@pytest.mark.asyncio
@respx.mock
async def test_user_assignable_search_value_error(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/assignable/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[],
        )
    )

    # WHEN/THEN
    with pytest.raises(
        ValueError, match='One of these parameters is required: project_id, issue_id, issue_key'
    ):
        await jira_api.user_assignable_search()


@pytest.mark.asyncio
@respx.mock
async def test_user_assignable_search(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/assignable/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'assignable_users_search.json'),
        )
    )

    # WHEN
    result = await jira_api.user_assignable_search('P1')
    # THEN
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=50' in request_url
    assert 'query=' not in request_url
    assert 'issueKey=' not in request_url
    assert 'issueId=' not in request_url
    assert 'project=P1' in request_url
    assert isinstance(result, dict)
    assert result == {
        'accountId': '5b10a2844c20165700ede21g',
        'accountType': 'atlassian',
        'active': True,
        'applicationRoles': {'items': [], 'size': 1},
        'displayName': 'Mia Krystof',
        'emailAddress': 'mia@example.com',
        'groups': {'items': [], 'size': 3},
        'key': '',
        'name': '',
        'timeZone': 'Australia/Sydney',
    }


@pytest.mark.asyncio
@respx.mock
async def test_user_assignable_search_with_multiple_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/assignable/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'assignable_users_search.json'),
        )
    )

    # WHEN
    result = await jira_api.user_assignable_search(
        'P1',
        offset=3,
        limit=10,
        query='q',
        issue_key='k1',
        issue_id='2',
    )
    # THEN
    request_url = str(route.calls.last.request.url)
    assert 'startAt=3' in request_url
    assert 'maxResults=10' in request_url
    assert 'query=q' in request_url
    assert 'issueKey=k1' in request_url
    assert 'issueId=2' in request_url
    assert 'project=P1' in request_url
    assert isinstance(result, dict)
    assert result == {
        'accountId': '5b10a2844c20165700ede21g',
        'accountType': 'atlassian',
        'active': True,
        'applicationRoles': {'items': [], 'size': 1},
        'displayName': 'Mia Krystof',
        'emailAddress': 'mia@example.com',
        'groups': {'items': [], 'size': 3},
        'key': '',
        'name': '',
        'timeZone': 'Australia/Sydney',
    }


@pytest.mark.asyncio
@respx.mock
async def test_user_assignable_multi_projects_with_multiple_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/assignable/multiProjectSearch'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[load_json_response(__file__, 'assignable_users_search.json')],
        )
    )

    # WHEN
    result = await jira_api.user_assignable_multi_projects(
        ['P1', 'P2'], offset=3, limit=10, query='q'
    )
    # THEN
    request_url = str(route.calls.last.request.url)
    assert 'startAt=3' in request_url
    assert 'maxResults=10' in request_url
    assert 'query=q' in request_url
    assert 'projectKeys=P1%2CP2' in request_url
    assert isinstance(result, list)
    assert result == [
        {
            'accountId': '5b10a2844c20165700ede21g',
            'accountType': 'atlassian',
            'active': True,
            'applicationRoles': {'items': [], 'size': 1},
            'displayName': 'Mia Krystof',
            'emailAddress': 'mia@example.com',
            'groups': {'items': [], 'size': 3},
            'key': '',
            'name': '',
            'timeZone': 'Australia/Sydney',
        }
    ]


@pytest.mark.asyncio
@respx.mock
async def test_user_assignable_multi_projects_without_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/assignable/multiProjectSearch'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[],
        )
    )
    # WHEN
    result = await jira_api.user_assignable_multi_projects()
    # THEN
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert 'query=' not in request_url
    assert 'projectKeys=' not in request_url
    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
@respx.mock
async def test_get_issue(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/task-1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'issue.json'),
        )
    )
    # WHEN
    result = await jira_api.get_issue('task-1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/task-1'
    request_url = str(route.calls.last.request.url)
    assert 'properties=' not in request_url
    assert 'fields=' not in request_url
    assert 'expand=editmeta' in request_url
    assert isinstance(result, dict)
    assert result == {
        'fields': {
            'attachment': [
                {
                    'author': {
                        'accountId': '5b10a2844c20165700ede21g',
                        'accountType': 'atlassian',
                        'active': False,
                        'displayName': 'Mia Krystof',
                        'key': '',
                        'name': '',
                    },
                    'content': 'https://your-domain.atlassian.net/jira/rest/api/3/attachment/content/10000',
                    'created': '2022-10-06T07:32:47.000+0000',
                    'filename': 'picture.jpg',
                    'id': 10000,
                    'mimeType': 'image/jpeg',
                    'size': 23123,
                }
            ],
            'sub-tasks': [
                {
                    'id': '10000',
                    'outwardIssue': {
                        'fields': {'status': {'name': 'Open'}},
                        'id': '10003',
                        'key': 'ED-2',
                    },
                    'type': {'id': '10000', 'inward': 'Parent', 'name': '', 'outward': 'Sub-task'},
                }
            ],
            'description': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': 'Main order flow broken'}],
                    }
                ],
            },
            'project': {
                'id': '10000',
                'insight': {
                    'lastIssueUpdateTime': '2021-04-22T05:37:05.000+0000',
                    'totalIssueCount': 100,
                },
                'key': 'EX',
                'name': 'Example',
                'projectCategory': {
                    'description': 'First Project Category',
                    'id': '10000',
                    'name': 'FIRST',
                },
                'simplified': False,
                'style': 'classic',
            },
            'comment': [
                {
                    'author': {
                        'accountId': '5b10a2844c20165700ede21g',
                        'active': False,
                        'displayName': 'Mia Krystof',
                    },
                    'body': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': 'Lorem ipsum.'}],
                            }
                        ],
                    },
                    'created': '2021-01-17T12:34:00.000+0000',
                    'id': '10000',
                    'updateAuthor': {
                        'accountId': '5b10a2844c20165700ede21g',
                        'active': False,
                        'displayName': 'Mia Krystof',
                    },
                    'updated': '2021-01-18T23:45:00.000+0000',
                    'visibility': {
                        'identifier': 'Administrators',
                        'type': 'role',
                        'value': 'Administrators',
                    },
                }
            ],
            'issuelinks': [
                {
                    'id': '10001',
                    'outwardIssue': {
                        'fields': {'status': {'name': 'Open'}},
                        'id': '10004L',
                        'key': 'PR-2',
                    },
                    'type': {
                        'id': '10000',
                        'inward': 'depends on',
                        'name': 'Dependent',
                        'outward': 'is depended by',
                    },
                },
                {
                    'id': '10002',
                    'inwardIssue': {
                        'fields': {'status': {'name': 'Open'}},
                        'id': '10004',
                        'key': 'PR-3',
                    },
                    'type': {
                        'id': '10000',
                        'inward': 'depends on',
                        'name': 'Dependent',
                        'outward': 'is depended by',
                    },
                },
            ],
            'worklog': [
                {
                    'author': {
                        'accountId': '5b10a2844c20165700ede21g',
                        'active': False,
                        'displayName': 'Mia Krystof',
                    },
                    'comment': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': 'I did some work here.'}],
                            }
                        ],
                    },
                    'id': '100028',
                    'issueId': '10002',
                    'started': '2021-01-17T12:34:00.000+0000',
                    'timeSpent': '3h 20m',
                    'timeSpentSeconds': 12000,
                    'updateAuthor': {
                        'accountId': '5b10a2844c20165700ede21g',
                        'active': False,
                        'displayName': 'Mia Krystof',
                    },
                    'updated': '2021-01-18T23:45:00.000+0000',
                    'visibility': {
                        'identifier': '276f955c-63d7-42c8-9520-92d01dca0625',
                        'type': 'group',
                        'value': 'jira-developers',
                    },
                }
            ],
            'updated': 1,
            'timetracking': {
                'originalEstimate': '10m',
                'originalEstimateSeconds': 600,
                'remainingEstimate': '3m',
                'remainingEstimateSeconds': 200,
                'timeSpent': '6m',
                'timeSpentSeconds': 400,
            },
        },
        'id': '10002',
        'key': 'ED-1',
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_with_multiple_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/task-1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={},
        )
    )
    # WHEN
    await jira_api.get_issue('task-1', 'f1,f2', 'p1,p2')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/task-1'
    request_url = str(route.calls.last.request.url)
    assert 'properties=p1%2Cp2' in request_url
    assert 'fields=f1%2Cf2' in request_url
    assert 'expand=editmeta' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_remote_links(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/task-1/remotelink'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'issue_remote_links.json'),
        )
    )
    # WHEN
    result = await jira_api.get_issue_remote_links('task-1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/task-1/remotelink'
    request_url = str(route.calls.last.request.url)
    assert 'globalId=' not in request_url
    assert isinstance(result, list)
    assert result == [
        {
            'application': {'name': 'My Acme Tracker', 'type': 'com.acme.tracker'},
            'globalId': 'system=http://www.mycompany.com/support&id=1',
            'id': 10000,
            'object': {
                'status': {'resolved': True},
                'summary': 'Customer support issue',
                'title': 'TSTSUP-111',
                'url': 'http://www.mycompany.com/support?id=1',
            },
            'relationship': 'causes',
        },
        {
            'application': {'name': 'My Acme Tester', 'type': 'com.acme.tester'},
            'globalId': 'system=http://www.anothercompany.com/tester&id=1234',
            'id': 10001,
            'object': {
                'status': {'resolved': False},
                'summary': 'Test that the submit button saves the item',
                'title': 'Test Case #1234',
                'url': 'http://www.anothercompany.com/tester/testcase/1234',
            },
            'relationship': 'is tested by',
        },
    ]


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_remote_links_by_global_id(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/task-1/remotelink'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'issue_remote_links.json'),
        )
    )
    # WHEN
    result = await jira_api.get_issue_remote_links(
        'task-1',
        'system=http://www.mycompany.com/support&id=1',
    )
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/task-1/remotelink'
    request_url = str(route.calls.last.request.url)
    assert 'globalId=system%3Dhttp%3A%2F%2Fwww.mycompany.com%2Fsupport%26id%3D1' in request_url
    assert isinstance(result, list)
    assert result == [
        {
            'application': {'name': 'My Acme Tracker', 'type': 'com.acme.tracker'},
            'globalId': 'system=http://www.mycompany.com/support&id=1',
            'id': 10000,
            'object': {
                'status': {'resolved': True},
                'summary': 'Customer support issue',
                'title': 'TSTSUP-111',
                'url': 'http://www.mycompany.com/support?id=1',
            },
            'relationship': 'causes',
        },
        {
            'application': {'name': 'My Acme Tester', 'type': 'com.acme.tester'},
            'globalId': 'system=http://www.anothercompany.com/tester&id=1234',
            'id': 10001,
            'object': {
                'status': {'resolved': False},
                'summary': 'Test that the submit button saves the item',
                'title': 'Test Case #1234',
                'url': 'http://www.anothercompany.com/tester/testcase/1234',
            },
            'relationship': 'is tested by',
        },
    ]


@pytest.mark.asyncio
@respx.mock
async def test_delete_issue_remote_link(jira_api: JiraAPI):
    # GIVEN
    route = respx.delete(get_url_pattern('issue/task-1/remotelink/link-1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'issue_remote_links.json'),
        )
    )
    # WHEN
    await jira_api.delete_issue_remote_link(
        'task-1',
        'link-1',
    )
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/task-1/remotelink/link-1'


@pytest.mark.asyncio
@respx.mock
async def test_evaluate_expression(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('expression/evaluate'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'evaluate_expression.json'),
        )
    )
    # WHEN
    result = await jira_api.evaluate_expression('user=bart')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/expression/evaluate'
    assert json.loads(route.calls.last.request.content) == {'expression': 'user=bart'}
    assert result == {
        'value': "The expression's result. This value can be any JSON, not necessarily a String",
        'meta': {
            'complexity': {
                'steps': {'value': 1, 'limit': 10000},
                'expensiveOperations': {'value': 3, 'limit': 10},
                'beans': {'value': 0, 'limit': 1000},
                'primitiveValues': {'value': 1, 'limit': 10000},
            },
            'issues': {'jql': {'nextPageToken': 'EgQIlMIC', 'isLast': False}},
        },
    }


@pytest.mark.asyncio
@respx.mock
async def test_evaluate_expression_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('expression/evaluate'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.evaluate_expression('user=bart', issue_key='Task-1', project_key='P1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/expression/evaluate'
    assert json.loads(route.calls.last.request.content) == {
        'expression': 'user=bart',
        'issue': {'key': 'Task-1'},
        'project': {'key': 'P1'},
    }


@pytest.mark.asyncio
@respx.mock
async def test_server_info(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('serverInfo'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'baseUrl': 'https://your-domain.atlassian.net',
                'buildDate': '2020-03-26T22:20:59.000+0000',
                'buildNumber': 582,
                'defaultLocale': {'locale': 'en_AU'},
                'displayUrl': 'https://instance.jira.your-domain.com',
                'displayUrlConfluence': 'https://instance.confluence.your-domain.com',
                'displayUrlServicedeskHelpCenter': 'https://instance.help.your-domain.com',
                'scmInfo': '1f51473f5c7b75c1a69a0090f4832cdc5053702a',
                'serverTime': '2020-03-31T16:43:50.000+0000',
                'serverTimeZone': 'Australia/Sydney',
                'serverTitle': 'My Jira instance',
                'version': '1001.0.0-SNAPSHOT',
                'versionNumbers': [5, 0, 0],
            },
        )
    )
    # WHEN
    result = await jira_api.server_info()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/serverInfo'
    assert result == {
        'baseUrl': 'https://your-domain.atlassian.net',
        'buildDate': '2020-03-26T22:20:59.000+0000',
        'buildNumber': 582,
        'defaultLocale': {'locale': 'en_AU'},
        'displayUrl': 'https://instance.jira.your-domain.com',
        'displayUrlConfluence': 'https://instance.confluence.your-domain.com',
        'displayUrlServicedeskHelpCenter': 'https://instance.help.your-domain.com',
        'scmInfo': '1f51473f5c7b75c1a69a0090f4832cdc5053702a',
        'serverTime': '2020-03-31T16:43:50.000+0000',
        'serverTimeZone': 'Australia/Sydney',
        'serverTitle': 'My Jira instance',
        'version': '1001.0.0-SNAPSHOT',
        'versionNumbers': [5, 0, 0],
    }


@pytest.mark.asyncio
@respx.mock
async def test_myself(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('myself'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'accountId': '5b10a2844c20165700ede21g',
                'accountType': 'atlassian',
                'active': True,
                'applicationRoles': {'items': [], 'size': 1},
                'displayName': 'Mia Krystof',
                'emailAddress': 'mia@example.com',
                'groups': {'items': [], 'size': 3},
                'key': '',
                'name': '',
                'timeZone': 'Australia/Sydney',
            },
        )
    )
    # WHEN
    result = await jira_api.myself()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/myself'
    assert result == {
        'accountId': '5b10a2844c20165700ede21g',
        'accountType': 'atlassian',
        'active': True,
        'applicationRoles': {'items': [], 'size': 1},
        'displayName': 'Mia Krystof',
        'emailAddress': 'mia@example.com',
        'groups': {'items': [], 'size': 3},
        'key': '',
        'name': '',
        'timeZone': 'Australia/Sydney',
    }


@pytest.mark.asyncio
@respx.mock
async def test_search_users(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('users/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                },
                {
                    'accountId': '5b10ac8d82e05b22cc7d4ef5',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Emma Richards',
                    'key': '',
                    'name': '',
                },
            ],
        )
    )
    # WHEN
    result = await jira_api.search_users()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/users/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert result == [
        {
            'accountId': '5b10a2844c20165700ede21g',
            'accountType': 'atlassian',
            'active': False,
            'displayName': 'Mia Krystof',
            'key': '',
            'name': '',
        },
        {
            'accountId': '5b10ac8d82e05b22cc7d4ef5',
            'accountType': 'atlassian',
            'active': False,
            'displayName': 'Emma Richards',
            'key': '',
            'name': '',
        },
    ]


@pytest.mark.asyncio
@respx.mock
async def test_search_users_with_offset_and_limit(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('users/search'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.search_users(10, 50)
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/users/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=10' in request_url
    assert 'maxResults=50' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_user_search(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                },
                {
                    'accountId': '5b10ac8d82e05b22cc7d4ef5',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Emma Richards',
                    'key': '',
                    'name': '',
                },
            ],
        )
    )
    # WHEN
    result = await jira_api.user_search()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/user/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert 'username=' not in request_url
    assert 'query=' not in request_url
    assert result == [
        {
            'accountId': '5b10a2844c20165700ede21g',
            'accountType': 'atlassian',
            'active': False,
            'displayName': 'Mia Krystof',
            'key': '',
            'name': '',
        },
        {
            'accountId': '5b10ac8d82e05b22cc7d4ef5',
            'accountType': 'atlassian',
            'active': False,
            'displayName': 'Emma Richards',
            'key': '',
            'name': '',
        },
    ]


@pytest.mark.asyncio
@respx.mock
async def test_user_search_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                },
                {
                    'accountId': '5b10ac8d82e05b22cc7d4ef5',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Emma Richards',
                    'key': '',
                    'name': '',
                },
            ],
        )
    )
    # WHEN
    await jira_api.user_search('bart.simpson', 'bart', 2, 15)
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/user/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=2' in request_url
    assert 'maxResults=15' in request_url
    assert 'username=bart.simpson' in request_url
    assert 'query=bart' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_user_search_with_empty_query(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('user/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    'accountId': '5b10a2844c20165700ede21g',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Mia Krystof',
                    'key': '',
                    'name': '',
                },
                {
                    'accountId': '5b10ac8d82e05b22cc7d4ef5',
                    'accountType': 'atlassian',
                    'active': False,
                    'displayName': 'Emma Richards',
                    'key': '',
                    'name': '',
                },
            ],
        )
    )
    # WHEN
    await jira_api.user_search('bart.simpson', '', 2, 15)
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/user/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=2' in request_url
    assert 'maxResults=15' in request_url
    assert 'username=bart.simpson' in request_url
    assert 'query=' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_get_groups_in_bulk(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('group/bulk'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': True,
                'maxResults': 10,
                'startAt': 0,
                'total': 2,
                'values': [
                    {'groupId': '276f955c-63d7-42c8-9520-92d01dca0625', 'name': 'jdog-developers'},
                    {'groupId': '6e87dc72-4f1f-421f-9382-2fee8b652487', 'name': 'juvenal-bot'},
                ],
            },
        )
    )
    # WHEN
    result = await jira_api.get_groups_in_bulk()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/group/bulk'
    assert result == {
        'isLast': True,
        'maxResults': 10,
        'startAt': 0,
        'total': 2,
        'values': [
            {'groupId': '276f955c-63d7-42c8-9520-92d01dca0625', 'name': 'jdog-developers'},
            {'groupId': '6e87dc72-4f1f-421f-9382-2fee8b652487', 'name': 'juvenal-bot'},
        ],
    }
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert 'groupId=' not in request_url
    assert 'groupName=' not in request_url


@pytest.mark.asyncio
@respx.mock
async def test_get_groups_in_bulk_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('group/bulk'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.get_groups_in_bulk(
        offset=2, limit=10, groups_ids=['1', '2'], groups_names=['g1', 'g2']
    )
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/group/bulk'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=2' in request_url
    assert 'maxResults=10' in request_url
    assert 'groupId=1%2C2' in request_url
    assert 'groupName=g1%2Cg2' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_get_users_in_group(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('group/member'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': False,
                'maxResults': 2,
                'nextPage': 'https://your-domain.atlassian.net/rest/api/3/group/member?groupId=276f955c-63d7-42c8-9520-92d01dca0625&includeInactiveUsers=false&startAt=4&maxResults=2',
                'startAt': 3,
                'total': 5,
                'values': [
                    {
                        'accountId': '5b10a2844c20165700ede21g',
                        'accountType': 'atlassian',
                        'active': True,
                        'avatarUrls': {},
                        'displayName': 'Mia',
                        'emailAddress': 'mia@example.com',
                        'key': '',
                        'name': '',
                        'timeZone': 'Australia/Sydney',
                    },
                    {
                        'accountId': '5b10a0effa615349cb016cd8',
                        'accountType': 'atlassian',
                        'active': False,
                        'avatarUrls': {},
                        'displayName': 'Will',
                        'emailAddress': 'will@example.com',
                        'key': '',
                        'name': '',
                        'timeZone': 'Australia/Sydney',
                    },
                ],
            },
        )
    )
    # WHEN
    result = await jira_api.get_users_in_group('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/group/member'
    assert result == {
        'isLast': False,
        'maxResults': 2,
        'nextPage': 'https://your-domain.atlassian.net/rest/api/3/group/member?groupId=276f955c-63d7-42c8-9520-92d01dca0625&includeInactiveUsers=false&startAt=4&maxResults=2',
        'startAt': 3,
        'total': 5,
        'values': [
            {
                'accountId': '5b10a2844c20165700ede21g',
                'accountType': 'atlassian',
                'active': True,
                'avatarUrls': {},
                'displayName': 'Mia',
                'emailAddress': 'mia@example.com',
                'key': '',
                'name': '',
                'timeZone': 'Australia/Sydney',
            },
            {
                'accountId': '5b10a0effa615349cb016cd8',
                'accountType': 'atlassian',
                'active': False,
                'avatarUrls': {},
                'displayName': 'Will',
                'emailAddress': 'will@example.com',
                'key': '',
                'name': '',
                'timeZone': 'Australia/Sydney',
            },
        ],
    }
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert 'groupId=1' in request_url
    assert 'groupName=' not in request_url
    assert 'includeInactiveUsers=false' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_get_users_in_group_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('group/member'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.get_users_in_group(offset=2, limit=10, group_id='1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/group/member'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=2' in request_url
    assert 'maxResults=10' in request_url
    assert 'groupId=1' in request_url
    assert 'includeInactiveUsers=false' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_add_comment(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('issue/1/comment'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={},
        )
    )
    # WHEN
    result = await jira_api.add_comment('1', 'Hello')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/comment'
    assert json.loads(route.calls.last.request.content) == {
        'body': {
            'content': [{'content': [{'text': 'Hello', 'type': 'text'}], 'type': 'paragraph'}],
            'type': 'doc',
            'version': 1,
        }
    }
    assert result == {}


@pytest.mark.asyncio
@respx.mock
async def test_get_comment(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/comment/2'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'author': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'body': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Lorem ipsum'}]}
                    ],
                },
                'created': '2021-01-17T12:34:00.000+0000',
                'id': '10000',
                'updateAuthor': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'updated': '2021-01-18T23:45:00.000+0000',
                'visibility': {
                    'identifier': 'Administrators',
                    'type': 'role',
                    'value': 'Administrators',
                },
            },
        )
    )
    # WHEN
    result = await jira_api.get_comment('1', '2')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/comment/2'
    assert result == {
        'author': {
            'accountId': '5b10a2844c20165700ede21g',
            'active': False,
            'displayName': 'Mia Krystof',
        },
        'body': {
            'type': 'doc',
            'version': 1,
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Lorem ipsum'}]}
            ],
        },
        'created': '2021-01-17T12:34:00.000+0000',
        'id': '10000',
        'updateAuthor': {
            'accountId': '5b10a2844c20165700ede21g',
            'active': False,
            'displayName': 'Mia Krystof',
        },
        'updated': '2021-01-18T23:45:00.000+0000',
        'visibility': {'identifier': 'Administrators', 'type': 'role', 'value': 'Administrators'},
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_comments(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/comment'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'comments': [
                    {
                        'author': {
                            'accountId': '5b10a2844c20165700ede21g',
                            'active': False,
                            'displayName': 'Mia Krystof',
                        },
                        'body': {
                            'type': 'doc',
                            'version': 1,
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [{'type': 'text', 'text': 'Lorem ipsum'}],
                                }
                            ],
                        },
                        'created': '2021-01-17T12:34:00.000+0000',
                        'id': '10000',
                        'updateAuthor': {
                            'accountId': '5b10a2844c20165700ede21g',
                            'active': False,
                            'displayName': 'Mia Krystof',
                        },
                        'updated': '2021-01-18T23:45:00.000+0000',
                        'visibility': {
                            'identifier': 'Administrators',
                            'type': 'role',
                            'value': 'Administrators',
                        },
                    }
                ],
                'maxResults': 1,
                'startAt': 0,
                'total': 1,
            },
        )
    )
    # WHEN
    result = await jira_api.get_comments('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/comment'
    assert result == {
        'comments': [
            {
                'author': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'body': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Lorem ipsum'}]}
                    ],
                },
                'created': '2021-01-17T12:34:00.000+0000',
                'id': '10000',
                'updateAuthor': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'updated': '2021-01-18T23:45:00.000+0000',
                'visibility': {
                    'identifier': 'Administrators',
                    'type': 'role',
                    'value': 'Administrators',
                },
            }
        ],
        'maxResults': 1,
        'startAt': 0,
        'total': 1,
    }
    request_url = str(route.calls.last.request.url)
    assert 'orderBy=-created' in request_url
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url


@pytest.mark.asyncio
@respx.mock
async def test_get_comments_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/comment'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.get_comments('1', 1, 20)
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/comment'
    request_url = str(route.calls.last.request.url)
    assert 'orderBy=-created' in request_url
    assert 'startAt=1' in request_url
    assert 'maxResults=20' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_delete_comment(jira_api: JiraAPI):
    # GIVEN
    route = respx.delete(get_url_pattern('issue/task-1/comment/comment-1'))
    route.mock(
        return_value=httpx.Response(
            204,
            json={},
        )
    )
    # WHEN
    await jira_api.delete_comment('task-1', 'comment-1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/task-1/comment/comment-1'


@pytest.mark.asyncio
@respx.mock
async def test_issue_edit_metadata(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/editmeta'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'fields': {
                    'summary': {
                        'allowedValues': ['red', 'blue'],
                        'defaultValue': 'red',
                        'hasDefaultValue': False,
                        'key': 'field_key',
                        'name': 'My Multi Select',
                        'operations': ['set', 'add'],
                        'required': False,
                        'schema': {
                            'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                            'customId': 10001,
                            'items': 'option',
                            'type': 'array',
                        },
                    }
                }
            },
        )
    )
    # WHEN
    result = await jira_api.issue_edit_metadata('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/editmeta'
    assert result == {
        'fields': {
            'summary': {
                'allowedValues': ['red', 'blue'],
                'defaultValue': 'red',
                'hasDefaultValue': False,
                'key': 'field_key',
                'name': 'My Multi Select',
                'operations': ['set', 'add'],
                'required': False,
                'schema': {
                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                    'customId': 10001,
                    'items': 'option',
                    'type': 'array',
                },
            }
        }
    }


@pytest.mark.asyncio
@respx.mock
async def test_create_work_item(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('issue'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'id': '10000',
                'key': 'ED-24',
                'transition': {
                    'status': 200,
                    'errorCollection': {'errorMessages': [], 'errors': {}},
                },
            },
        )
    )
    # WHEN
    result = await jira_api.create_work_item({'assignee': {'id': '12345'}})
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue'
    assert json.loads(route.calls.last.request.content) == {'fields': {'assignee': {'id': '12345'}}}
    assert result == {
        'id': '10000',
        'key': 'ED-24',
        'transition': {'status': 200, 'errorCollection': {'errorMessages': [], 'errors': {}}},
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_transitions(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/transitions'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'transitions': [
                    {
                        'fields': {
                            'summary': {
                                'allowedValues': ['red', 'blue'],
                                'defaultValue': 'red',
                                'hasDefaultValue': False,
                                'key': 'field_key',
                                'name': 'My Multi Select',
                                'operations': ['set', 'add'],
                                'required': False,
                                'schema': {
                                    'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                                    'customId': 10001,
                                    'items': 'option',
                                    'type': 'array',
                                },
                            }
                        },
                        'hasScreen': False,
                        'id': '2',
                        'isAvailable': True,
                        'isConditional': False,
                        'isGlobal': False,
                        'isInitial': False,
                        'name': 'Close Issue',
                        'to': {
                            'description': 'The issue is currently being worked on.',
                            'id': '10000',
                            'name': 'In Progress',
                            'statusCategory': {
                                'colorName': 'yellow',
                                'id': 1,
                                'key': 'in-flight',
                                'name': 'In Progress',
                            },
                        },
                    }
                ]
            },
        )
    )
    # WHEN
    result = await jira_api.transitions('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/transitions'
    assert result == {
        'transitions': [
            {
                'fields': {
                    'summary': {
                        'allowedValues': ['red', 'blue'],
                        'defaultValue': 'red',
                        'hasDefaultValue': False,
                        'key': 'field_key',
                        'name': 'My Multi Select',
                        'operations': ['set', 'add'],
                        'required': False,
                        'schema': {
                            'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect',
                            'customId': 10001,
                            'items': 'option',
                            'type': 'array',
                        },
                    }
                },
                'hasScreen': False,
                'id': '2',
                'isAvailable': True,
                'isConditional': False,
                'isGlobal': False,
                'isInitial': False,
                'name': 'Close Issue',
                'to': {
                    'description': 'The issue is currently being worked on.',
                    'id': '10000',
                    'name': 'In Progress',
                    'statusCategory': {
                        'colorName': 'yellow',
                        'id': 1,
                        'key': 'in-flight',
                        'name': 'In Progress',
                    },
                },
            }
        ]
    }


@pytest.mark.asyncio
@respx.mock
async def test_transition_issue(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('issue/1/transitions'))
    route.mock(
        return_value=httpx.Response(
            204,
            json=None,
        )
    )
    # WHEN
    await jira_api.transition_issue('1', '2')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/transitions'
    assert json.loads(route.calls.last.request.content) == {'transition': '2'}


@pytest.mark.asyncio
@respx.mock
async def test_create_issue_link_inward(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('issueLink'))
    route.mock(
        return_value=httpx.Response(
            204,
            json=None,
        )
    )
    # WHEN
    await jira_api.create_issue_link('1', '2', 'inward', '8')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issueLink'
    assert json.loads(route.calls.last.request.content) == {
        'type': {'id': '8'},
        'inwardIssue': {'key': '2'},
        'outwardIssue': {'key': '1'},
    }


@pytest.mark.asyncio
@respx.mock
async def test_create_issue_link_outward(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('issueLink'))
    route.mock(
        return_value=httpx.Response(
            204,
            json=None,
        )
    )
    # WHEN
    await jira_api.create_issue_link('1', '2', 'outward', '7')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issueLink'
    assert json.loads(route.calls.last.request.content) == {
        'type': {'id': '7'},
        'inwardIssue': {'key': '1'},
        'outwardIssue': {'key': '2'},
    }


@pytest.mark.asyncio
@respx.mock
async def test_issue_link_types(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issueLinkType'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'issueLinkTypes': [
                    {
                        'id': '1000',
                        'inward': 'Duplicated by',
                        'name': 'Duplicate',
                        'outward': 'Duplicates',
                    },
                    {'id': '1010', 'inward': 'Blocked by', 'name': 'Blocks', 'outward': 'Blocks'},
                ]
            },
        )
    )
    # WHEN
    result = await jira_api.issue_link_types()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issueLinkType'
    assert result == {
        'issueLinkTypes': [
            {'id': '1000', 'inward': 'Duplicated by', 'name': 'Duplicate', 'outward': 'Duplicates'},
            {'id': '1010', 'inward': 'Blocked by', 'name': 'Blocks', 'outward': 'Blocks'},
        ]
    }


@pytest.mark.asyncio
@respx.mock
async def test_delete_issue_link(jira_api: JiraAPI):
    # GIVEN
    route = respx.delete(get_url_pattern('issueLink/1'))
    route.mock(return_value=httpx.Response(204, json=None))
    # WHEN
    await jira_api.delete_issue_link('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issueLink/1'


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_create_meta(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/createmeta/P1/issuetypes/1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'fields': [
                    {
                        'fieldId': 'assignee',
                        'hasDefaultValue': False,
                        'key': 'assignee',
                        'name': 'Assignee',
                        'operations': ['set'],
                        'required': True,
                    }
                ],
                'maxResults': 1,
                'startAt': 0,
                'total': 1,
            },
        )
    )
    # WHEN
    result = await jira_api.get_issue_create_meta('P1', '1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/createmeta/P1/issuetypes/1'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=0' in request_url
    assert 'maxResults=' not in request_url
    assert result == {
        'fields': [
            {
                'fieldId': 'assignee',
                'hasDefaultValue': False,
                'key': 'assignee',
                'name': 'Assignee',
                'operations': ['set'],
                'required': True,
            }
        ],
        'maxResults': 1,
        'startAt': 0,
        'total': 1,
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_create_meta_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/createmeta/P1/issuetypes/1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'fields': [
                    {
                        'fieldId': 'assignee',
                        'hasDefaultValue': False,
                        'key': 'assignee',
                        'name': 'Assignee',
                        'operations': ['set'],
                        'required': True,
                    }
                ],
                'maxResults': 1,
                'startAt': 0,
                'total': 1,
            },
        )
    )
    # WHEN
    result = await jira_api.get_issue_create_meta('P1', '1', 3, 50)
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/createmeta/P1/issuetypes/1'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=3' in request_url
    assert 'maxResults=50' in request_url
    assert result == {
        'fields': [
            {
                'fieldId': 'assignee',
                'hasDefaultValue': False,
                'key': 'assignee',
                'name': 'Assignee',
                'operations': ['set'],
                'required': True,
            }
        ],
        'maxResults': 1,
        'startAt': 0,
        'total': 1,
    }


@pytest.mark.asyncio
@respx.mock
async def test_delete_attachment(jira_api: JiraAPI):
    # GIVEN
    route = respx.delete(get_url_pattern('attachment/1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'issue_remote_links.json'),
        )
    )
    # WHEN
    await jira_api.delete_attachment('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/attachment/1'


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_work_log(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/worklog'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'maxResults': 1,
                'startAt': 0,
                'total': 1,
                'worklogs': [
                    {
                        'author': {
                            'accountId': '5b10a2844c20165700ede21g',
                            'active': False,
                            'displayName': 'Mia Krystof',
                        },
                        'comment': {
                            'type': 'doc',
                            'version': 1,
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [{'type': 'text', 'text': 'I did some work here.'}],
                                }
                            ],
                        },
                        'id': '100028',
                        'issueId': '10002',
                        'started': '2021-01-17T12:34:00.000+0000',
                        'timeSpent': '3h 20m',
                        'timeSpentSeconds': 12000,
                        'updateAuthor': {
                            'accountId': '5b10a2844c20165700ede21g',
                            'active': False,
                            'displayName': 'Mia Krystof',
                        },
                        'updated': '2021-01-18T23:45:00.000+0000',
                        'visibility': {
                            'identifier': '276f955c-63d7-42c8-9520-92d01dca0625',
                            'type': 'group',
                            'value': 'jira-developers',
                        },
                    }
                ],
            },
        )
    )
    # WHEN
    result = await jira_api.get_issue_work_log('1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/worklog'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert result == {
        'maxResults': 1,
        'startAt': 0,
        'total': 1,
        'worklogs': [
            {
                'author': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'comment': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'I did some work here.'}],
                        }
                    ],
                },
                'id': '100028',
                'issueId': '10002',
                'started': '2021-01-17T12:34:00.000+0000',
                'timeSpent': '3h 20m',
                'timeSpentSeconds': 12000,
                'updateAuthor': {
                    'accountId': '5b10a2844c20165700ede21g',
                    'active': False,
                    'displayName': 'Mia Krystof',
                },
                'updated': '2021-01-18T23:45:00.000+0000',
                'visibility': {
                    'identifier': '276f955c-63d7-42c8-9520-92d01dca0625',
                    'type': 'group',
                    'value': 'jira-developers',
                },
            }
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_work_log_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('issue/1/worklog'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.get_issue_work_log('1', 1, 10)
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/worklog'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=1' in request_url
    assert 'maxResults=10' in request_url


@pytest.mark.asyncio
@respx.mock
async def test_update_issue(jira_api: JiraAPI):
    # GIVEN
    route = respx.put(get_url_pattern('issue/1'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={},
        )
    )
    # WHEN
    result = await jira_api.update_issue('1', {'summary': 'test summary'})
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1'
    assert json.loads(route.calls.last.request.content) == {'update': {'summary': 'test summary'}}
    request_url = str(route.calls.last.request.url)
    assert 'returnIssue=true' in request_url
    assert result == {}


@patch('jiratui.api.api.build_issue_search_jql')
@pytest.mark.asyncio
@respx.mock
async def test_search_issues(build_issue_search_jql_mock: Mock, jira_api: JiraAPI):
    # GIVEN
    build_issue_search_jql_mock.return_value = ''
    route = respx.post(get_url_pattern('search/jql'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={},
        )
    )
    # WHEN
    result = await jira_api.search_issues()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/search/jql'
    assert json.loads(route.calls.last.request.content) == {'jql': '', 'maxResults': 30}
    assert result == {}


@patch('jiratui.api.api.build_issue_search_jql')
@pytest.mark.asyncio
@respx.mock
async def test_search_issues_with_parameters(build_issue_search_jql_mock: Mock, jira_api: JiraAPI):
    # GIVEN
    build_issue_search_jql_mock.return_value = 'query'
    route = respx.post(get_url_pattern('search/jql'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={},
        )
    )
    # WHEN
    result = await jira_api.search_issues(limit=10, fields=['f1', 'f2'], next_page_token='token1')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/search/jql'
    assert json.loads(route.calls.last.request.content) == {
        'jql': 'query',
        'maxResults': 10,
        'fields': ['f1', 'f2'],
        'nextPageToken': 'token1',
    }
    assert result == {}


@pytest.mark.asyncio
@respx.mock
async def test_search_projects(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('project/search'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                'isLast': False,
                'maxResults': 2,
                'nextPage': 'https://your-domain.atlassian.net/rest/api/3/project/search?startAt=2&maxResults=2',
                'startAt': 0,
                'total': 7,
                'values': [
                    {
                        'id': '10000',
                        'insight': {
                            'lastIssueUpdateTime': '2021-04-22T05:37:05.000+0000',
                            'totalIssueCount': 100,
                        },
                        'key': 'EX',
                        'name': 'Example',
                        'projectCategory': {
                            'description': 'First Project Category',
                            'id': '10000',
                            'name': 'FIRST',
                        },
                        'simplified': False,
                        'style': 'classic',
                    },
                    {
                        'id': '10001',
                        'insight': {
                            'lastIssueUpdateTime': '2021-04-22T05:37:05.000+0000',
                            'totalIssueCount': 100,
                        },
                        'key': 'ABC',
                        'name': 'Alphabetical',
                        'projectCategory': {
                            'description': 'First Project Category',
                            'id': '10000',
                            'name': 'FIRST',
                        },
                        'simplified': False,
                        'style': 'classic',
                    },
                ],
            },
        )
    )
    # WHEN
    result = await jira_api.search_projects()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/project/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=' not in request_url
    assert 'maxResults=' not in request_url
    assert 'orderBy=' not in request_url
    assert 'query=' not in request_url
    assert 'keys=' not in request_url
    assert result == {
        'isLast': False,
        'maxResults': 2,
        'nextPage': 'https://your-domain.atlassian.net/rest/api/3/project/search?startAt=2&maxResults=2',
        'startAt': 0,
        'total': 7,
        'values': [
            {
                'id': '10000',
                'insight': {
                    'lastIssueUpdateTime': '2021-04-22T05:37:05.000+0000',
                    'totalIssueCount': 100,
                },
                'key': 'EX',
                'name': 'Example',
                'projectCategory': {
                    'description': 'First Project Category',
                    'id': '10000',
                    'name': 'FIRST',
                },
                'simplified': False,
                'style': 'classic',
            },
            {
                'id': '10001',
                'insight': {
                    'lastIssueUpdateTime': '2021-04-22T05:37:05.000+0000',
                    'totalIssueCount': 100,
                },
                'key': 'ABC',
                'name': 'Alphabetical',
                'projectCategory': {
                    'description': 'First Project Category',
                    'id': '10000',
                    'name': 'FIRST',
                },
                'simplified': False,
                'style': 'classic',
            },
        ],
    }


@pytest.mark.asyncio
@respx.mock
async def test_search_projects_with_parameters(jira_api: JiraAPI):
    # GIVEN
    route = respx.get(get_url_pattern('project/search'))
    route.mock(return_value=httpx.Response(200, json={}))
    # WHEN
    await jira_api.search_projects(
        offset=1, limit=5, query='query-value', order_by='id', keys=['k1', 'k2']
    )
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/project/search'
    request_url = str(route.calls.last.request.url)
    assert 'startAt=1' in request_url
    assert 'maxResults=5' in request_url
    assert 'orderBy=id' in request_url
    assert 'query=query-value' in request_url
    assert 'keys=k1%2Ck2' in request_url


def test_build_issue_search_jql():
    # WHEN
    result = build_issue_search_jql()
    # THEN
    assert result == ''


def test_build_issue_search_jql_with_jql_query():
    # WHEN
    result = build_issue_search_jql(jql_query='q1')
    # THEN
    assert result == 'q1'


def test_build_issue_search_jql_with_jql_query_and_fields():
    # WHEN
    result = build_issue_search_jql(jql_query='q1', project_key='P1')
    # THEN
    assert result == 'project = P1 and q1'


def test_build_issue_search_jql_with_jql_query_and_fields_and_orderby():
    # WHEN
    result = build_issue_search_jql(
        jql_query='q1', project_key='P1', order_by=WorkItemsSearchOrderBy.KEY_ASC
    )
    # THEN
    assert result == 'project = P1 and q1 order by key asc'


def test_build_issue_search_jql_no_jql_query_and_fields_and_orderby():
    # WHEN
    result = build_issue_search_jql(order_by=WorkItemsSearchOrderBy.KEY_ASC)
    # THEN
    assert result == 'order by key asc'


@pytest.mark.asyncio
@respx.mock
async def test_create_issue_remote_link(jira_api: JiraAPI):
    # GIVEN
    route = respx.post(get_url_pattern('issue/1/remotelink'))
    route.mock(
        return_value=httpx.Response(
            200,
            json=load_json_response(__file__, 'evaluate_expression.json'),
        )
    )
    # WHEN
    await jira_api.create_issue_remote_link('1', 'http://foo.bar', 'test')
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/issue/1/remotelink'
    assert json.loads(route.calls.last.request.content) == {
        'object': {
            'title': 'test',
            'url': 'http://foo.bar',
        }
    }


@patch('jiratui.api.api.build_issue_search_jql')
@pytest.mark.asyncio
@respx.mock
async def test_work_items_search_approximate_count(
    build_issue_search_jql_mock: Mock, jira_api: JiraAPI
):
    # GIVEN
    build_issue_search_jql_mock.return_value = 'key=value'
    route = respx.post(get_url_pattern('search/approximate-count'))
    route.mock(
        return_value=httpx.Response(
            200,
            json={'key': 'data'},
        )
    )
    # WHEN
    result = await jira_api.work_items_search_approximate_count()
    # THEN
    assert route.calls.last.request.url.path == '/rest/api/3/search/approximate-count'
    assert json.loads(route.calls.last.request.content) == {'jql': 'key=value'}
    assert result == {'key': 'data'}
