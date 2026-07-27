import httpx
import pytest
import respx

from jiratui.api.client import AsyncJiraClient, JiraClient
from jiratui.config import ApplicationConfiguration
from jiratui.exceptions import (
    APIException,
    AuthorizationException,
    PermissionException,
    ResourceNotFoundException,
    ServiceInvalidRequestException,
)
from jiratui.utils.test_utilities import get_url_pattern


@pytest.fixture
def client(config_for_testing) -> AsyncJiraClient:
    return AsyncJiraClient('http://foo.bar', 'bart', '12345', config_for_testing)


@pytest.fixture
def read_only_client(config_for_testing) -> AsyncJiraClient:
    config_for_testing.read_only = True
    return AsyncJiraClient('http://foo.bar', 'bart', '12345', config_for_testing)


@pytest.fixture
def read_only_sync_client(config_for_testing) -> JiraClient:
    config_for_testing.read_only = True
    return JiraClient('http://foo.bar', 'bart', '12345', config_for_testing)


@pytest.mark.parametrize(
    ('method_name', 'url'),
    [
        ('post', 'issue'),
        ('post', 'custom/search'),
        ('put', 'issue/SP-1'),
        ('patch', 'issue/SP-1'),
        ('delete', 'issue/SP-1'),
    ],
)
@pytest.mark.asyncio
@respx.mock
async def test_read_only_client_blocks_mutating_requests(read_only_client, method_name, url):
    route = respx.route(method=method_name.upper(), url=get_url_pattern(url))

    with pytest.raises(APIException, match='read-only mode'):
        await read_only_client.make_request(getattr(httpx.AsyncClient, method_name), url)

    assert route.called is False


@pytest.mark.asyncio
@respx.mock
async def test_real_read_only_configuration_blocks_mutating_request(tmp_path, monkeypatch):
    config_file = tmp_path / 'config.yaml'
    config_file.write_text(
        '\n'.join(
            [
                'jira_api_username: user@example.test',
                'jira_api_token: token',
                'jira_api_base_url: https://example.atlassian.net',
                'read_only: true',
            ]
        )
    )
    monkeypatch.setenv('JIRA_TUI_CONFIG_FILE', str(config_file))
    client = AsyncJiraClient(
        'http://foo.bar',
        'user@example.test',
        'token',
        ApplicationConfiguration(),
    )
    route = respx.post(get_url_pattern('issue'))

    with pytest.raises(APIException, match='read-only mode'):
        await client.make_request(httpx.AsyncClient.post, 'issue')

    assert route.called is False


@respx.mock
def test_read_only_sync_client_blocks_mutating_requests(read_only_sync_client):
    route = respx.post(get_url_pattern('issue/SP-1/attachments'))

    with pytest.raises(APIException, match='read-only mode'):
        read_only_sync_client.make_request(httpx.post, 'issue/SP-1/attachments')

    assert route.called is False


@respx.mock
def test_read_only_sync_client_allows_get_requests(read_only_sync_client):
    route = respx.get(get_url_pattern('issue/SP-1')).mock(
        return_value=httpx.Response(200, json={'key': 'SP-1'})
    )

    response = read_only_sync_client.make_request(httpx.get, 'issue/SP-1')

    assert response == {'key': 'SP-1'}
    assert route.called is True


@pytest.mark.parametrize(
    'url',
    ['search/jql', 'search', 'search/approximate-count', 'expression/evaluate'],
)
@pytest.mark.asyncio
@respx.mock
async def test_read_only_client_allows_read_post_requests(read_only_client, url):
    route = respx.post(get_url_pattern(url)).mock(
        return_value=httpx.Response(200, json={'issues': []})
    )

    response = await read_only_client.make_request(httpx.AsyncClient.post, url)

    assert response == {'issues': []}
    assert route.called is True


@pytest.mark.asyncio
@respx.mock
async def test_read_only_client_allows_absolute_search_url(read_only_client):
    url = 'http://foo.bar/rest/api/3/search/jql'
    route = respx.post(url).mock(return_value=httpx.Response(200, json={'issues': []}))

    response = await read_only_client.make_request(httpx.AsyncClient.post, url)

    assert response == {'issues': []}
    assert route.called is True


@pytest.mark.asyncio
@respx.mock
async def test_read_only_client_allows_get_requests(read_only_client):
    route = respx.get(get_url_pattern('issue/SP-1')).mock(
        return_value=httpx.Response(200, json={'key': 'SP-1'})
    )

    response = await read_only_client.make_request(httpx.AsyncClient.get, 'issue/SP-1')

    assert response == {'key': 'SP-1'}
    assert route.called is True


@pytest.mark.parametrize(
    'status_code, expected_exception',
    [
        (400, ServiceInvalidRequestException),
        (404, ResourceNotFoundException),
        (401, AuthorizationException),
        (403, PermissionException),
    ],
)
@pytest.mark.asyncio
@respx.mock
async def test_make_request_response_with_exception(client, status_code, expected_exception):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1/statuses'))
    route.mock(
        return_value=httpx.Response(
            status_code,
            json={
                'errorMessages': ['some error message'],
                'errors': {'property-a': 'some property value here'},
                'status': 5,
            },
        )
    )
    # WHEN
    with pytest.raises(expected_exception, match='some error message') as exc_info:
        await client.make_request(httpx.AsyncClient.get, 'project/P1/statuses')
    # THEN
    assert exc_info.value.extra == {
        'url': 'http://foo.bar/project/P1/statuses',
        'status_code': status_code,
        'errorMessages': ['some error message'],
        'errors': {'property-a': 'some property value here'},
        'status': 5,
    }


@pytest.mark.asyncio
@respx.mock
async def test_make_request_response_with_exception_without_error_messages(client):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1/statuses'))
    route.mock(
        return_value=httpx.Response(
            400,
            json={
                'errorMessages': [],
                'errors': {'property-a': 'some property value here'},
                'status': 5,
            },
        )
    )
    # WHEN
    with pytest.raises(ServiceInvalidRequestException) as exc_info:
        await client.make_request(httpx.AsyncClient.get, 'project/P1/statuses')
    # THEN
    assert exc_info.value.extra == {
        'url': 'http://foo.bar/project/P1/statuses',
        'status_code': 400,
        'errorMessages': [],
        'errors': {'property-a': 'some property value here'},
        'status': 5,
    }


@pytest.mark.asyncio
@respx.mock
async def test_make_request_response_with_exception_no_json_response(client):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1/statuses'))
    route.mock(return_value=httpx.Response(400, json='non-json response'))
    # WHEN
    with pytest.raises(ServiceInvalidRequestException) as exc_info:
        await client.make_request(httpx.AsyncClient.get, 'project/P1/statuses')
    # THEN
    assert exc_info.value.extra == {
        'url': 'http://foo.bar/project/P1/statuses',
        'status_code': 400,
    }


@pytest.mark.asyncio
@respx.mock
async def test_make_request_response_204(client):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1/statuses'))
    route.mock(return_value=httpx.Response(204, json=''))
    # WHEN
    response = await client.make_request(httpx.AsyncClient.get, 'project/P1/statuses')
    # THEN
    assert response == {}


@pytest.mark.asyncio
@respx.mock
async def test_make_request_response_201(client):
    # GIVEN
    route = respx.get(get_url_pattern('project/P1/statuses'))
    route.mock(return_value=httpx.Response(201, json=None))
    # WHEN
    response = await client.make_request(httpx.AsyncClient.get, 'project/P1/statuses')
    # THEN
    assert response == {}


@pytest.mark.asyncio
@respx.mock
async def test_create_issue_with_reporter_field_fails(client):
    """Test that creating an issue with the reporter field fails with 400 error.
    This test captures the current behavior where Jira Cloud API rejects the reporter field.
    The error occurs because Jira Cloud auto-sets the reporter to the authenticated user,
    and the field cannot be manually set when it's not on the appropriate screen.
    This test should initially FAIL (RED) when the code still includes the reporter field,
    then PASS (GREEN) after the fix that makes the reporter field conditional.
    """
    # GIVEN
    route = respx.post(get_url_pattern('issue'))
    route.mock(
        return_value=httpx.Response(
            400,
            json={
                'errorMessages': [],
                'errors': {
                    'reporter': "Field 'reporter' cannot be set. It is not on the appropriate screen, or unknown."
                },
            },
        )
    )
    # THEN
    with pytest.raises(ServiceInvalidRequestException) as exc_info:
        await client.make_request(
            httpx.AsyncClient.post,
            'issue',
            data='{"fields":{"project":{"key":"TEST"},"summary":"Test issue","issuetype":{"name":"Bug"},"reporter":{"accountId":"12345"}}}',
        )
    assert exc_info.value.extra == {
        'url': 'http://foo.bar/issue',
        'status_code': 400,
        'errorMessages': [],
        'errors': {
            'reporter': "Field 'reporter' cannot be set. It is not on the appropriate screen, or unknown."
        },
    }


@pytest.mark.asyncio
@respx.mock
async def test_create_issue_without_reporter_field_succeeds(client):
    """Test that creating an issue without the reporter field succeeds.
    This test verifies the fix: when the reporter field is excluded from the payload,
    issue creation should succeed. Jira Cloud automatically sets the reporter to the
    authenticated user.
    This test should PASS both before and after the fix, demonstrating the correct
    behavior when the reporter field is not included.
    """
    # GIVEN
    route = respx.post(get_url_pattern('issue'))
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                'id': '10000',
                'key': 'TEST-1',
                'self': 'https://foo.bar/rest/api/3/issue/10000',
            },
        )
    )
    # THEN
    response = await client.make_request(
        httpx.AsyncClient.post,
        'issue',
        data='{"fields":{"project":{"key":"TEST"},"summary":"Test issue","issuetype":{"name":"Bug"}}}',
    )
    assert response == {
        'id': '10000',
        'key': 'TEST-1',
        'self': 'https://foo.bar/rest/api/3/issue/10000',
    }
