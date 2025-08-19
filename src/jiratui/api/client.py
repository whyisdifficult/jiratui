import logging
from typing import Callable

import httpx

from jiratui.constants import LOGGER_NAME
from jiratui.exceptions import (
    AuthorizationException,
    PermissionException,
    ResourceNotFoundException,
    ServiceInvalidRequestException,
    ServiceInvalidResponseException,
    ServiceUnavailableException,
)


class JiraClient:
    """A sync HTTP client for the Jira REST API."""

    def __init__(self, base_url: str, api_username: str, api_token: str):
        self.base_url: str = base_url.rstrip('/')
        self.client: httpx.Client = httpx.Client(timeout=None)
        self.authentication = httpx.BasicAuth(api_username, api_token)
        self.logger = logging.getLogger(LOGGER_NAME)

    @staticmethod
    def set_headers(headers: dict | None = None) -> dict:
        default_headers = {
            'Accept': 'application/json',
        }
        # important: https://requests.readthedocs.io/en/latest/user/quickstart/#more-complicated-post-requests
        if headers:
            default_headers.update(headers)
        return default_headers

    def get_resource_url(self, resource: str) -> str:
        return f'{self.base_url}/{resource}'

    def make_request(
        self,
        method: Callable,
        url: str,
        headers: dict | None = None,
        timeout: int = 55,
        **kwargs,
    ) -> dict | list | None:
        headers = self.set_headers(headers)
        url = self.get_resource_url(url)

        try:
            response: httpx.Response = method(
                url, headers=headers, timeout=timeout, auth=self.authentication, **kwargs
            )
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as e:
            msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(msg, extra={'url': url})
            raise ServiceUnavailableException(msg, extra={'url': url}) from e

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(msg, extra={'url': url, 'status_code': response.status_code})
            if response.status_code == 404:
                raise ResourceNotFoundException(str(e)) from e
            if response.status_code == 401:
                raise AuthorizationException(str(e)) from e
            if response.status_code == 403:
                raise PermissionException(str(e)) from e
            raise ServiceInvalidRequestException(
                msg, extra={'status_code': response.status_code}
            ) from e

        if response.status_code == 204:
            return {}

        try:
            response_json = response.json()
        except Exception as e:
            if response.status_code == 201:
                return {}
            # This may happen if nginx responds with an error page or on calling ping
            log_msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(log_msg, extra={'url': url, 'status_code': response.status_code})
            raise ServiceInvalidResponseException(log_msg, extra={}) from e

        return response_json


class AsyncJiraClient:
    """Async HTTP client for the Jira REST API."""

    def __init__(self, base_url: str, api_username: str, api_token: str):
        self.base_url: str = base_url.rstrip('/')
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=None)
        self.authentication = httpx.BasicAuth(api_username, api_token)
        self.logger = logging.getLogger(LOGGER_NAME)

    @staticmethod
    def set_headers(headers: dict | None = None) -> dict:
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        # important: https://requests.readthedocs.io/en/latest/user/quickstart/#more-complicated-post-requests
        if headers:
            default_headers.update(headers)
        return default_headers

    def get_resource_url(self, resource: str) -> str:
        return f'{self.base_url}/{resource}'

    async def close_async_client(self):
        # httpx.AsyncClient.aclose must be awaited!
        await self.client.aclose()

    async def make_request(
        self,
        method: Callable,
        url: str,
        headers: dict | None = None,
        timeout: int = 55,
        **kwargs,
    ) -> dict | list | None:
        headers = self.set_headers(headers)
        url = self.get_resource_url(url)

        try:
            response: httpx.Response = await method(
                self.client,
                url,
                headers=headers,
                timeout=timeout,
                auth=self.authentication,
                **kwargs,
            )
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as e:
            msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(msg, extra={'url': url})
            raise ServiceUnavailableException(msg, extra={'url': url}) from e

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(msg, extra={'url': url, 'status_code': response.status_code})
            if response.status_code == 404:
                raise ResourceNotFoundException(
                    'The requested resource was not found',
                    extra={
                        'error_message': str(e),
                        'status_code': 404,
                    },
                ) from e
            if response.status_code == 401:
                raise AuthorizationException(
                    'Authorization is required to access the requested resource.',
                    extra={
                        'error_message': str(e),
                        'status_code': 401,
                    },
                ) from e
            if response.status_code == 403:
                raise PermissionException(
                    'Missing required permission to access the requested resource.',
                    extra={
                        'error_message': str(e),
                        'status_code': 403,
                    },
                ) from e
            raise ServiceInvalidRequestException(
                msg, extra={'status_code': response.status_code}
            ) from e

        if response.status_code == 204:
            return {}

        try:
            response_json = response.json()
        except Exception as e:
            if response.status_code == 201:
                return {}
            # This may happen if nginx responds with an error page or on calling ping
            log_msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(log_msg, extra={'url': url, 'status_code': response.status_code})
            raise ServiceInvalidResponseException(log_msg, extra={}) from e

        return response_json
