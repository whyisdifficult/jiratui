import logging
import ssl
from typing import Any, Callable

import httpx

from jiratui.config import ApplicationConfiguration
from jiratui.constants import LOGGER_NAME
from jiratui.exceptions import (
    AuthorizationException,
    PermissionException,
    ResourceNotFoundException,
    ServiceInvalidRequestException,
    ServiceInvalidResponseException,
    ServiceUnavailableException,
)


class JiraTUIBearerAuth(httpx.Auth):
    def __init__(self, token: str, username: str | None = None):
        self.token = token

    def auth_flow(self, request):
        request.headers['Authorization'] = f'Bearer {self.token.strip()}'
        yield request


def _setup_ssl_certificates(
    configuration: ApplicationConfiguration,
) -> ssl.SSLContext | bool | None:
    """
    Returns a value that can be passed to the `verify` kwarg of an httpx client
    Either:
        False to disable verification,
        True if no SSL config block is defined (default behavior),
        or an instance of ssl.SSLContext with client cert/key/CA loaded (if specified. Otherwise, an SSLContext with the default CA bundle).
    """
    if ssl_certificate_configuration := configuration.ssl:
        if ssl_certificate_configuration.verify_ssl is False:
            return False
        ctx = ssl.create_default_context(cafile=ssl_certificate_configuration.ca_bundle)
        # Only load the client cert if certificate_file is set
        # `load_cert_chain` is safe to run even if key_file is None or password is None
        if ssl_certificate_configuration.certificate_file:
            ctx.load_cert_chain(
                certfile=ssl_certificate_configuration.certificate_file,
                keyfile=ssl_certificate_configuration.key_file,
                password=ssl_certificate_configuration.password.get_secret_value()
                if ssl_certificate_configuration.password
                else None,
            )

        return ctx
    return True


class JiraTUIAsyncHTTPClient:
    """An async HTTP client for the Jira RETS API.

    This is useful for operations in endpoints that do not return JSON data, e.g. for downloading file attachments.
    """

    def __init__(
        self,
        base_url: str,
        api_username: str,
        api_token: str,
        configuration: ApplicationConfiguration,
    ):
        ssl_certificate_settings = _setup_ssl_certificates(configuration)
        self.base_url: str = base_url.rstrip('/')
        if configuration.use_bearer_authentication:
            self.authentication: httpx.Auth = JiraTUIBearerAuth(api_token, api_username)
        elif configuration.use_cert_authentication:
            self.authentication = None
        else:
            self.authentication = httpx.BasicAuth(api_username, api_token.strip())
        self.client: httpx.AsyncClient = httpx.AsyncClient(
            verify=ssl_certificate_settings,
            timeout=None,
        )
        self.logger = logging.getLogger(LOGGER_NAME)

    @staticmethod
    def set_headers(headers: dict | None = None) -> dict:
        default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
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
    ) -> Any | None:
        headers = self.set_headers(headers)
        url = self.get_resource_url(url)

        try:
            response: httpx.Response = await method(
                self.client,
                url=url,
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
            # see https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#status-codes
            error_details: dict | None = self._parse_error_response(response)

            extra = {
                'url': url,
                'status_code': response.status_code,
            }

            message = str(e)
            if error_details is not None and isinstance(error_details, dict):
                if error_details.get('errorMessages', []):
                    message = error_details.get('errorMessages', [])[0]
                extra.update(**error_details)

            self.logger.error(message, extra=extra)
            if response.status_code == 404:
                raise ResourceNotFoundException(message, extra=extra) from e
            if response.status_code == 401:
                raise AuthorizationException(message, extra=extra) from e
            if response.status_code == 403:
                raise PermissionException(message, extra=extra) from e
            raise ServiceInvalidRequestException(message, extra=extra) from e

        if response.status_code == 204:
            return self._empty_response(response)

        try:
            return self._parse_response(response)
        except Exception as e:
            if response.status_code == 201:
                return self._empty_response(response)
            log_msg = f'{e.__class__.__name__}: {e}.'
            self.logger.error(log_msg, extra={'url': url, 'status_code': response.status_code})
            raise ServiceInvalidResponseException(log_msg, extra={}) from e

    @staticmethod
    def _parse_error_response(response: httpx.Response) -> dict | None:
        return None

    def _empty_response(self, response: httpx.Response) -> Any:
        return ''

    def _parse_response(self, response: httpx.Response) -> Any:
        return response.content


class JiraClient:
    """A sync JSON client for the Jira REST API.

    This is useful for endpoints that support JSON but do not support async operations, e.g. uploading file attachments.
    """

    def __init__(
        self,
        base_url: str,
        api_username: str,
        api_token: str,
        configuration: ApplicationConfiguration,
    ):
        ssl_certificate_settings = _setup_ssl_certificates(configuration)
        self.base_url: str = base_url.rstrip('/')
        if configuration.use_bearer_authentication:
            self.authentication: httpx.Auth = JiraTUIBearerAuth(api_token, api_username)
        elif configuration.use_cert_authentication:
            self.authentication = None
        else:
            self.authentication = httpx.BasicAuth(api_username, api_token.strip())
        self.client: httpx.Client = httpx.Client(
            verify=ssl_certificate_settings,
            timeout=None,
        )
        self.logger = logging.getLogger(LOGGER_NAME)

    @staticmethod
    def set_headers(headers: dict | None = None) -> dict:
        default_headers = {
            'Accept': 'application/json',
        }
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
            # see https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#status-codes
            error_details: dict | None = self._parse_error_response(response)

            extra = {
                'url': url,
                'status_code': response.status_code,
            }

            message = str(e)
            if error_details is not None and isinstance(error_details, dict):
                if error_details.get('errorMessages', []):
                    message = error_details.get('errorMessages', [])[0]
                extra.update(**error_details)

            self.logger.error(message, extra=extra)
            if response.status_code == 404:
                raise ResourceNotFoundException(message, extra=extra) from e
            if response.status_code == 401:
                raise AuthorizationException(message, extra=extra) from e
            if response.status_code == 403:
                raise PermissionException(message, extra=extra) from e
            raise ServiceInvalidRequestException(message, extra=extra) from e

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

    @staticmethod
    def _parse_error_response(response: httpx.Response) -> dict | None:
        try:
            return response.json()
        except Exception:
            return None


class AsyncJiraClient(JiraTUIAsyncHTTPClient):
    """Async JSON client for the Jira REST API."""

    @staticmethod
    def set_headers(headers: dict | None = None) -> dict:
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if headers:
            default_headers.update(headers)
        return default_headers

    @staticmethod
    def _parse_error_response(response: httpx.Response) -> dict | None:
        try:
            return response.json()
        except Exception:
            return None

    def _empty_response(self, response: httpx.Response) -> Any:
        return {}

    def _parse_response(self, response: httpx.Response) -> Any:
        return response.json()
