import logging
from dataclasses import dataclass
from http import HTTPStatus, HTTPMethod  # noqa
import json
from urllib.parse import urljoin

import aiohttp

from .utils import exceptions

# Main aiomonobank logger
log = logging.getLogger('aiomonobank')


@dataclass(frozen=True)
class MonobankAPIServer:
    """
    Base config for API Endpoints
    """
    base_url: str

    def api_url(self, api_path: str) -> str:
        """
        The api_url function takes a string as an argument and returns a string.
        The returned string is the base url for the api with the api_path appended to it.

        :param self: Represent the instance of the class
        :param api_path: str: Specify the path of the api
        :return: The base url with the api_path appended to it
        """
        return urljoin(self.base_url, api_path)

    @classmethod
    def from_base(cls, base: str) -> 'MonobankAPIServer':
        """
        The from_base function is a class method that allows you to create an instance of the MonobankAPIServer
        class by providing only the base URL for the API server. This is useful if you want to use a different
        Monobank API server than what's provided in this library, or if you're using your own local development
        server. The from_base function will automatically add /{{api_path}} to whatever base URL string it receives,
        so that all requests are properly routed.

        :param cls: Refer to the class itself
        :param base: str: Specify the base url of the api
        :return: A monobank api server object with the base attribute set to the value of
        """
        return cls(
            base_url=base.rstrip("/"),
        )


MONOBANK_PRODUCTION = MonobankAPIServer.from_base("https://api.monobank.ua")


def check_token(token: str) -> bool:
    """
    The check_token function checks if the token is valid.

    :param token: str: Specify the type of the parameter
    :return: True if the token is valid and raises an exception otherwise
    """
    if not isinstance(token, str):
        raise exceptions.ValidationError(f"Token is invalid! It must be 'str' type instead of {type(token)} type.")

    if any(x.isspace() for x in token):
        raise exceptions.ValidationError("Token is invalid! It can't contains spaces.")

    return True


def check_result(api_path: str, content_type: str, status_code: int, body: str) -> dict:
    """
    The check_result function is used to check the response from Monobank API.
    It checks if the content type of the response is application/json, and if it's not - raises a NetworkError exception.
    If it's OK, then we try to parse JSON from body of our request and store it in result_json variable.
    Then we check status code: if everything is OK (200), then return result_json; otherwise raise an appropriate exception.

    :param api_path: str: Specify the path to the api method
    :param content_type: str: Check the content type of the response
    :param status_code: int: Check the status code of the response
    :param body: str: Pass the body of the response from monobank api
    :return: The dictionary with the following keys if the status code is 200
    """
    log.debug('Response for %s: [%d] "%r"', api_path, status_code, body)

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


async def make_request(
        session: aiohttp.ClientSession,
        server: MonobankAPIServer,
        http_method: HTTPMethod,
        api_path: str,
        **kwargs
) -> dict:
    """
    The make_request function is a helper function that makes an HTTP request to the server.
    It takes in the following parameters:
        session - The aiohttp ClientSession object used for making requests.
        server - The Server object containing information about the API endpoint and authentication credentials.
        http_method - A string representing which HTTP method to use (e.g., 'GET', 'POST', etc.)  This should be one of
        those defined in constants/HTTP_METHODS, but it can also be any other valid HTTP method if you want to extend
        this library's functionality beyond what is provided by Monobank.

    :param session: aiohttp.ClientSession: Make the request
    :param server: MonobankAPIServer: Get the url of the api endpoint
    :param http_method: HTTPStatus: Specify the http method to use
    :param api_path: str: Log the request and response
    :param **kwargs: Pass a variable number of keyword arguments to the function
    :return: A dictionary
    """
    log.debug('Make request: "%s" with data: "%r"', api_path, kwargs.get('json', {}))

    url = server.api_url(api_path=api_path)

    try:
        async with session.request(http_method, url, **kwargs) as response:
            return check_result(api_path, response.content_type, response.status, await response.text())
    except aiohttp.ClientError as e:
        raise exceptions.NetworkError(f"aiohttp client throws an error: {e.__class__.__name__}: {e}")
