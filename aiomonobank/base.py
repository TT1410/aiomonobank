import json
import ssl
import certifi
from typing import Optional
from http import HTTPMethod  # noqa

import aiohttp
from aiohttp import hdrs

from . import api
from .api import MonobankAPIServer, MONOBANK_PRODUCTION


class BaseMonobank:
    def __init__(
            self,
            token: str,
            validate_token: Optional[bool] = True,
            connections_limit: Optional[int] = None,
            server: MonobankAPIServer = MONOBANK_PRODUCTION
    ) -> None:
        """
        Create Monobank API token from https://api.monobank.ua/

        :param token: str: token from https://api.monobank.ua/
        :param server: MonobankAPIServer: Monobank API Server endpoint.
        :raise aiomonobank.utils.exceptions.ValidationError: when the token is invalid
        """
        # Authentication
        if validate_token:
            api.check_token(token)

        self._token = token
        self.server = server

        # aiohttp main session
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_class: aiohttp.TCPConnector = aiohttp.TCPConnector  # noqa
        self._connector_init = dict(limit=connections_limit, ssl=ssl_context)

    async def get_new_session(self) -> aiohttp.ClientSession:
        """
        The get_new_session function is a coroutine that returns an aiohttp.ClientSession object with the following properties:
            - The headers are set to accept JSON and include the token for authentication.
            - The connector is set to use our custom connector class, which we will define in just a moment.
            - json_serialize is set to use Python's built-in json module.

        :param self: Access the attributes and methods of the class
        :return: A new aiohttp
        """
        return aiohttp.ClientSession(
            headers={
                hdrs.ACCEPT: "application/json",
                "X-Token": self._token
            },
            connector=self._connector_class(**self._connector_init),
            json_serialize=json.dumps
        )

    async def get_session(self) -> aiohttp.ClientSession:
        """
        The get_session function is a coroutine that returns an aiohttp.ClientSession object.

        :param self: Refer to the current object
        :return: A client session object
        """
        if self._session is None or self._session.closed:
            self._session = await self.get_new_session()

        if not self._session._loop.is_running():  # noqa
            await self._session.close()
            self._session = await self.get_new_session()

        return self._session

    async def close(self):
        """
        Close all client sessions
        """
        if self._session:
            await self._session.close()

    async def request(self,
                      http_method: HTTPMethod,
                      path: str,
                      **kwargs) -> dict:
        """
        The request function is a wrapper around the make_request function in
        the api module. It takes an http method, a path, and any other arguments
        that are required for making the request (such as data or params). The
        request function will then return the response from make_request.

        :param self: Represent the instance of the class
        :param http_method: HTTPMethod: Specify the type of request that is being made
        :param path: str: Specify the path of the request
        :param **kwargs: Pass in any number of keyword arguments
        :return: A dictionary of data
        """
        return await api.make_request(
            session=await self.get_session(),
            server=self.server,
            http_method=http_method,
            api_path=path,
            **kwargs
        )

    async def __aenter__(self):
        await self.get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

