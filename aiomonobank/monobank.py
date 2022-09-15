from datetime import datetime, timedelta, timezone

from .base import BaseMonobank
from .types import Statement, Client


class Monobank(BaseMonobank):

    async def set_webhook(self, webhook_url: str = '') -> bool:
        '''
        Установка WebHook URL пользователя
        ~~~~~~~~~~~~~~~~~~~~~
        Для подтверждения корректности предоставляемого адреса на него посылается GET-запрос.
        Сервер должен ответить строго HTTP статус-кодом 200, и никаким другим.
        Если валидация пройдена, на заданный адрес начинают посылаться POST запросы с событиями.

        События отправляются в следующем виде:
        POST запрос на заданный адрес в формате {type:"StatementItem", data:{account:"...", statementItem:{#StatementItem}}}.
        Если пользовательский сервис не ответит в течение 5с на команду, сервис повторит попытку еще через 60 и 600 секунд.
        Если на третью попытку ответ не будет получен, функция будет отключена.
        Ответ сервера должен строго содержать код HTTP 200.

        webhook_url: `string`
        raise: когда запросы чаще 1 раза в минуту :obj:`aiomonobank.utils.exceptions.RetryAfter`

        Источник: :obj:`https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1webhook/post`
        '''
        json = {"webHookUrl": webhook_url}

        await self.request('POST', "personal/webhook", json)

        return True

    async def client_info(self) -> Client:
        '''
        Информация о клиенте

        Источник: https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1client-info/get

        raise: когда запросы чаще 1 раза в минуту :obj:`aiomonobank.utils.exceptions.RetryAfter`

        ~~~~~~~~~~~~~~~~~~~~~
        Получение информации о клиенте и перечне его счетов и банок. Ограничение на использование функции не чаще 1 раза в 60 секунд.
        '''
        client = await self.request('GET', "personal/client-info")

        return Client(**client)

    async def get_statement(self,
                            account_id: str = '0',
                            from_datetime: datetime = datetime.now() - timedelta(days=31, hours=1),
                            to_datetime: datetime = datetime.now()) -> list[Statement]:
        '''
        Выписка

        ~~~~~~~~~~~~~~~~~~~~~
        Получение выписки за время от {from} до {to} времени в секундах в формате Unix time
        Максимальное время, за которое можно получать выписку 31 сутки + 1 час (2682000 секунд)
        Ограничения на использование функции не чаще 1 раза в 60 секунд.

        account_id: `string` Идентификатор счета или банки из перечней Statement list или 0 – дефолтный счет.
        from_datetime: `string` Начало времени выписки.
        to_datetime: `string` Последнее время выписки (если нет, будет использоваться текущее время).
        raise: когда неверный account_id :obj:`aiomonobank.utils.exceptions.InvalidAccount`
        raise: когда период больше 31 дня и 1 часа :obj:`aiomonobank.utils.exceptions.PeriodError`
        raise: когда запросы чаще 1 раза в минуту :obj:`aiomonobank.utils.exceptions.RetryAfter`

        Источник: :obj:`https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get`
        '''
        from_datetime = await timestamp(from_datetime)
        to_datetime = await timestamp(to_datetime)

        path_parameters = f'/{account_id}/{from_datetime}{to_datetime}'

        statements = await self.request('GET', "personal/statement" + path_parameters)

        return [Statement(**statement) for statement in statements]


async def timestamp(date_time: datetime):
    return int(date_time.replace(tzinfo=timezone.utc).timestamp())


# DEFAULT_FILTER = ['self', 'cls']
#
#
# def generate_payload(exclude_key=None, exclude_value=None, **kwargs):
#     """
#     Generate payload
#
#     Usage: payload = generate_payload(**locals(), exclude_key=['foo'], exclude_value=['foo'])
#
#     :param exclude_key:
#     :param exclude_value:
#     :param kwargs:
#     :return: dict
#     """
#     if exclude_key is None:
#         exclude_key = []
#     if exclude_value is None:
#         exclude_value = []
#     return {key: value for key, value in kwargs.items() if
#             key not in exclude_key + DEFAULT_FILTER
#             and value not in [None] + exclude_value
#             and not key.startswith('_')}
