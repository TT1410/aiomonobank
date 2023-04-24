from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
from http import HTTPMethod  # noqa

from .base import BaseMonobank
from .types import Statement, Client


class Monobank(BaseMonobank):
    base_path = "personal"

    def _api_path(self, path: str) -> str:
        """
        The api_path function is a helper function that takes in a path and returns the full url to the API endpoint.

        :param self: Represent the instance of the class
        :param path: str: Join the base_path and path together
        :return: The base path + the path
        """
        return urljoin(self.base_path, path)

    async def set_webhook(self, webhook_url: str = '') -> bool:
        """
        Установка WebHook URL пользователя:
            Для подтверждения корректности предоставляемого адреса на него посылается GET-запрос.
            Сервер должен ответить строго HTTP статус-кодом 200, и никаким другим.
            Если валидация пройдена, на заданный адрес начинают посылаться POST запросы с событиями.

        События отправляются в следующем виде:
            POST запрос на заданный адрес в формате {type:"StatementItem", data:{account:"...", statementItem:{#StatementItem}}}.
            Если пользовательский сервис не ответит в течение 5с на команду, сервис повторит попытку еще через 60 и 600 секунд.
            Если на третью попытку ответ не будет получен, функция будет отключена.
            Ответ сервера должен строго содержать код HTTP 200.

        :param webhook_url: str:
        :raise aiomonobank.utils.exceptions.RetryAfter: когда запросы чаще 1 раза в минуту

        Источник: :obj:`https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1webhook/post`
        """
        await self.request(
            HTTPMethod.POST,
            self._api_path("webhook"),
            json={"webHookUrl": webhook_url}
        )

        return True

    async def client_info(self) -> Client:
        """
        Информация о клиенте:
            Получение информации о клиенте и перечне его счетов и банок.

        Ограничение на использование функции не чаще 1 раза в 60 секунд.

        Источник: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1client-info/get

        :raise aiomonobank.utils.exceptions.RetryAfter: когда запросы чаще 1 раза в минуту
        """
        client = await self.request(
            HTTPMethod.GET,
            self._api_path("client-info")
        )

        return Client(**client)

    async def get_statement(self,
                            account_id: str = '0',
                            from_datetime: datetime = None,
                            to_datetime: datetime = None) -> list[Statement]:
        """
        Выписка:
            Получение выписки за время от {from} до {to} времени в формате UTC time.
            Максимальное время, за которое можно получать выписку 31 сутки + 1 час.

        Ограничения на использование функции не чаще 1 раза в 60 секунд.

        Источник: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get

        :param account_id: str: Идентификатор счета или банки из перечней Statement list или 0 – дефолтный счет.
        :param from_datetime: datetime: Начало времени выписки.
        :param to_datetime: datetime: Последнее время выписки (если нет, будет использоваться текущее время).
        :raise aiomonobank.utils.exceptions.InvalidAccount: когда неверный account_id
        :raise aiomonobank.utils.exceptions.PeriodError: когда период больше 31 дня и 1 часа
        :raise aiomonobank.utils.exceptions.RetryAfter: когда запросы чаще 1 раза в минуту
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
            self._api_path("statement" + path_params)
        )

        return [Statement(**statement) for statement in statements]


async def timestamp(date_time: datetime) -> int:
    """
    The timestamp function takes a datetime object and returns the number of seconds since the Unix epoch.

    :param date_time: datetime: Specify the datetime object that will be passed to the function
    :return: The number of seconds since the epoch
    """
    return int(date_time.replace(tzinfo=timezone.utc).timestamp())
