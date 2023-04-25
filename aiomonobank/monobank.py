from datetime import datetime, timedelta, timezone
from typing import Optional
from http import HTTPMethod  # noqa

from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer

from .api import MonobankAPIServer, MONOBANK_PRODUCTION
from .base import BaseMonobank
from .types import Statement, Client, Currency


class MonoPublic(BaseMonobank):
    """
    Загальна інформація що надається без авторизації.

    Джерело: https://api.monobank.ua/docs/#tag/Publichni-dani
    """
    def __init__(self, connections_limit: Optional[int] = None,
                 server: MonobankAPIServer = MONOBANK_PRODUCTION, **kwargs) -> None:
        super().__init__(
            token=kwargs.get('token', ''),
            validate_token=kwargs.get('validate_token', False),
            connections_limit=connections_limit,
            server=server
        )

    @cached(ttl=300, cache=Cache.MEMORY, serializer=PickleSerializer())
    async def get_currency(self) -> list[Currency]:
        """
        Отримання курсів валют:
            Отримати базовий перелік курсів валют monobank.
            Інформація кешується та оновлюється не частіше 1 разу на 5 хвилин.

        Джерело: https://api.monobank.ua/docs/#tag/Publichni-dani/paths/~1bank~1currency/get

        :return: A list of currency objects
        """
        currency = await self.request(
            HTTPMethod.GET,
            "/bank/currency"
        )

        return [Currency(**cur) for cur in currency]


class MonoPersonal(MonoPublic):
    """
    Інформація, що надається тільки за наявністю token-а доступу, який клієнт може отримати
    в особистому кабінеті https://api.monobank.ua/

    Джерело: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani
    """
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
        super().__init__(
            token=token,
            validate_token=validate_token,
            connections_limit=connections_limit,
            server=server
        )

    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Встановлення URL користувача:
            Для підтвердження коректності наданої адреси, на неї надсилається GET-запит.
            Сервер має відповісти строго HTTP статус-кодом 200, і ніяким іншим.
            Якщо валідацію пройдено, на задану адресу починають надсилатися POST запити з подіями.

        Події надсилаються у наступному вигляді:
            POST запит на задану адресу у форматі {type:"StatementItem", data:{account:"...", statementItem:{#StatementItem}}}.
            Якщо сервіс користувача не відповість протягом 5с на команду, сервіс повторить спробу ще через 60 та 600 секунд.
            Якщо на третю спробу відповідь отримана не буде, функція буде вимкнута.
            Відповідь сервера має строго містити HTTP статус-код 200.

        :param webhook_url: str:
        :raise aiomonobank.utils.exceptions.RetryAfter: якщо запити частіше 1 разу в хвилину

        Джерело: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1webhook/post
        """
        await self.request(
            HTTPMethod.POST,
            "/personal/webhook",
            json={"webHookUrl": webhook_url}
        )

        return True

    async def get_client_info(self) -> Client:
        """
        Інформація про клієнта:
            Отримання інформації про клієнта та переліку його рахунків і банок.

        Обмеження на використання функції не частіше ніж 1 раз у 60 секунд.

        Джерело: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1client-info/get

        :raise aiomonobank.utils.exceptions.RetryAfter: якщо запити частіше 1 разу в хвилину
        """
        client = await self.request(
            HTTPMethod.GET,
            "/personal/client-info"
        )

        return Client(**client)

    async def get_statement(self,
                            account_id: str = '0',
                            from_datetime: datetime = None,
                            to_datetime: datetime = None) -> list[Statement]:
        """
        Виписка:
            Отримання виписки за час від {from_datetime} до {to_datetime} часу в секундах у форматі UTC time.
            Максимальний час, за який можливо отримати виписку — 31 доба + 1 година

        Обмеження на використання функції — не частіше ніж 1 раз на 60 секунд.

        Джерело: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get

        :param account_id: str: Ідентифікатор рахунку або банки з переліків Statement list або 0 - дефолтний рахунок.
        :param from_datetime: datetime: Початок часу виписки.
        :param to_datetime: datetime: Останній час виписки (якщо відсутній, буде використовуватись поточний час).
        :raise aiomonobank.utils.exceptions.InvalidAccount: якщо некоректний account_id
        :raise aiomonobank.utils.exceptions.PeriodError: якщо період більше 31 дня та 1 години
        :raise aiomonobank.utils.exceptions.RetryAfter: якщо запити частіше 1 разу в хвилину
        """
        from_datetime = await timestamp(
            from_datetime or datetime.utcnow() - timedelta(days=31, hours=1)
        )
        to_datetime = await timestamp(
            to_datetime or datetime.utcnow()
        )

        path_params = f'/{account_id}/{from_datetime}/{to_datetime}'

        statements = await self.request(
            HTTPMethod.GET,
            "/personal/statement" + path_params
        )

        return [Statement(**statement) for statement in statements]


async def timestamp(date_time: datetime) -> int:
    """
    The timestamp function takes a datetime object and returns the number of seconds since the Unix epoch.

    :param date_time: datetime: Specify the datetime object that will be passed to the function
    :return: The number of seconds since the epoch
    """
    return int(date_time.replace(tzinfo=timezone.utc).timestamp())
