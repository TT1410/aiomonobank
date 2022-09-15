import aiohttp
import json
import ssl
import certifi
from typing import Optional

from . import api
from .api import MonobankAPIServer, MONOBANK_PRODUCTION


class BaseMonobank:

    def __init__(
            self,
            token: str,
            validate_token: Optional[bool] = True,
            server: MonobankAPIServer = MONOBANK_PRODUCTION
    ):
        """
        Create Monobank API token from https://api.monobank.ua/

        :param token: token from https://api.monobank.ua/
        :type token: :obj:`str`
        :param server: Monobank API Server endpoint.
        :type server: :obj:`MonobankAPIServer`
        raise: when token is invalid throw an :obj:`aiomonobank.utils.exceptions.ValidationError`
        """

        # Authentication
        if validate_token:
            api.check_token(token)

        self.token = token
        self.server = server

        # aiohttp main session
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_class: aiohttp.TCPConnector = aiohttp.TCPConnector
        self._connector_init = dict(ssl=ssl_context)

    async def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            connector=self._connector_class(**self._connector_init),
            json_serialize=json.dumps
        )

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = await self.get_new_session()

        if not self._session._loop.is_running():
            await self._session.close()
            self._session = await self.get_new_session()

        return self._session

    async def close(self):
        """
        Close all client sessions
        """
        if self._session:
            await self._session.close()

    async def request(self, request_type: str,
                      method: str,
                      data: Optional[dict] = None,
                      **kwargs):
        """
        Сделать запрос к Monobank API

        https://api.monobank.ua/docs/
        """
        kwargs.update({'json': data if data else {}, 'headers': {"X-Token": self.token}})

        return await api.make_request(session=await self.get_session(), server=self.server,
                                      request_type=request_type, method=method, **kwargs)
