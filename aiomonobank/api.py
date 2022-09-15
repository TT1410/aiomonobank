import logging
from dataclasses import dataclass
from http import HTTPStatus
import json

import aiohttp

from .utils import exceptions


# Main aiomonobank logger
log = logging.getLogger('aiomonobank')


@dataclass(frozen=True)
class MonobankAPIServer:
    """
    Base config for API Endpoints
    """
    base: str

    def api_url(self, method: str) -> str:
        """
        Generate URL for API methods

        :param method: API method name (case insensitive)
        :return: URL
        """
        return self.base.format(method=method)

    @classmethod
    def from_base(cls, base: str) -> 'MonobankAPIServer':
        base = base.rstrip("/")
        return cls(
            base=f"{base}/{{method}}",
        )


MONOBANK_PRODUCTION = MonobankAPIServer.from_base("https://api.monobank.ua")


def check_token(token: str) -> bool:
    """
    Validate token

    :param token:
    :return:
    """
    if not isinstance(token, str):
        message = (f"Token is invalid! "
                   f"It must be 'str' type instead of {type(token)} type.")
        raise exceptions.ValidationError(message)

    if any(x.isspace() for x in token):
        message = "Token is invalid! It can't contains spaces."
        raise exceptions.ValidationError(message)

    return True


def check_result(method_name: str, content_type: str, status_code: int, body: str):
    """
    Checks whether `result` is a valid API response.
    A result is considered invalid if:
    - The server returned an HTTP response code other than 200
    - The content of the result is invalid JSON.
    - The method call was unsuccessful (The JSON 'ok' field equals False)

    :param method_name: The name of the method called
    :param status_code: status code
    :param content_type: content type of result
    :param body: result body
    :return: The result parsed to a JSON dictionary
    :raises ApiException: if one of the above listed cases is applicable
    """
    log.debug('Response for %s: [%d] "%r"', method_name, status_code, body)

    if content_type != 'application/json':
        raise exceptions.NetworkError(f"Invalid response with content type {content_type}: \"{body}\"")

    try:
        result_json = json.loads(body)
    except ValueError:
        result_json = {}

    if status_code == HTTPStatus.OK:
        return result_json

    error_description = result_json.get('errorDescription') or body

    if status_code == HTTPStatus.BAD_REQUEST:
        raise exceptions.BadRequest.detect(error_description)
    if status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED):
        raise exceptions.Unauthorized.detect(error_description)
    elif status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise exceptions.RetryAfter
    elif error_description == "webHookUrl timeout":  # most likely the status code of this error is 408, but this is not accurate
        raise exceptions.WebhookUrlError(error_description)

    raise exceptions.MonobankError(f"{error_description} [{status_code}]")


async def make_request(session, server, request_type, method, **kwargs):
    log.debug('Make request: "%s" with data: "%r"', method, kwargs['data'])

    url = server.api_url(method=method)

    try:
        async with session.request(request_type, url, **kwargs) as response:
            return check_result(method, response.content_type, response.status, await response.text())
    except aiohttp.ClientError as e:
        raise exceptions.NetworkError(f"aiohttp client throws an error: {e.__class__.__name__}: {e}")
