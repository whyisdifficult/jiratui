import httpx
import pytest
import respx

from jiratui.api.client import AsyncJiraClient
from jiratui.exceptions import (
    AuthorizationException,
    PermissionException,
    ResourceNotFoundException,
    ServiceInvalidRequestException,
)
from jiratui.utils.test_utilities import get_url_pattern


@pytest.fixture
def client(config_for_testing) -> AsyncJiraClient:
    return AsyncJiraClient('http://foo.bar', 'bart', '12345', config_for_testing)


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
