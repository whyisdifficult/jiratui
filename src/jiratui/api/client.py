from dataclasses import dataclass
import logging
from typing import Callable, cast

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


@dataclass
class SSLCertificateSettings:
    cert: str | tuple[str, str] | tuple[str, str, str] | None = None
    verify_ssl: str | bool = True


def _setup_ssl_certificates(configuration: ApplicationConfiguration) -> SSLCertificateSettings:
    cert: str | tuple[str, str] | tuple[str, str, str] | None = None
    verify_ssl: str | bool = True

    if ssl_certificate_configuration := configuration.ssl:
        verify_ssl = ssl_certificate_configuration.verify_ssl
        httpx_certificate_configuration: list[str] = []
        if certificate_path := ssl_certificate_configuration.certificate_file:
            httpx_certificate_configuration.append(certificate_path)
        if key_file := ssl_certificate_configuration.key_file:
            httpx_certificate_configuration.append(key_file)
        if password := ssl_certificate_configuration.password:
            httpx_certificate_configuration.append(password.get_secret_value())

        if verify_ssl and ssl_certificate_configuration.ca_bundle:
            verify_ssl = ssl_certificate_configuration.ca_bundle

        # expects:
        # (certificate file) or,
        # (certificate file, key file) or,
        # (certificate file, key file, password)
        cert = cast(
            str | tuple[str, str] | tuple[str, str, str], tuple(httpx_certificate_configuration)
        )

    return SSLCertificateSettings(cert=cert, verify_ssl=verify_ssl)


class JiraClient:
    """A sync HTTP client for the Jira REST API."""

    def __init__(
        self,
        base_url: str,
        api_username: str,
        api_token: str,
        configuration: ApplicationConfiguration,
    ):
        ssl_certificate_settings: SSLCertificateSettings = _setup_ssl_certificates(configuration)
        self.base_url: str = base_url.rstrip('/')
        if configuration.use_bearer_authentication:
            self.authentication: httpx.Auth = JiraTUIBearerAuth(api_token, api_username)
        else:
            self.authentication = httpx.BasicAuth(api_username, api_token.strip())
        self.client: httpx.Client = httpx.Client(
            verify=ssl_certificate_settings.verify_ssl,
            cert=ssl_certificate_settings.cert,
            timeout=None,
        )
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

    def __init__(
        self,
        base_url: str,
        api_username: str,
        api_token: str,
        configuration: ApplicationConfiguration,
    ):
        ssl_certificate_settings: SSLCertificateSettings = _setup_ssl_certificates(configuration)
        self.base_url: str = base_url.rstrip('/')
        if configuration.use_bearer_authentication:
            self.authentication: httpx.Auth = JiraTUIBearerAuth(api_token, api_username)
        else:
            self.authentication = httpx.BasicAuth(api_username, api_token.strip())
        self.client: httpx.AsyncClient = httpx.AsyncClient(
            verify=ssl_certificate_settings.verify_ssl,
            cert=ssl_certificate_settings.cert,
            timeout=None,
        )
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

        # make the request
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
