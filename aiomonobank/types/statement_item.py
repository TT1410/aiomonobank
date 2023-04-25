from datetime import datetime
import pytz
from pydantic import BaseModel, Field, validator


class Statement(BaseModel):
    id: str
    """Унікальний id транзакції"""
    time: datetime
    """Час транзакції в секундах в форматі UTC time"""
    description: str
    """Опис транзакцій"""
    mcc: int
    """Код типу транзакції (Merchant Category Code), відповідно ISO 18245"""
    original_mcc: int = Field(..., alias="originalMcc")
    """Оригінальний код типу транзакції (Merchant Category Code), відповідно ISO 18245"""
    hold: bool
    """Статус блокування суми (детальніше https://en.wikipedia.org/wiki/Authorization_hold)"""
    amount: float
    """Сума у валюті рахунку"""
    operation_amount: float = Field(..., alias="operationAmount")
    """Сума у валюті транзакції"""
    currency_code: int = Field(..., alias="currencyCode")
    """Код валюти рахунку відповідно ISO 4217"""
    commission_rate: float = Field(..., alias="commissionRate")
    """Розмір комісії"""
    cashback_amount: float = Field(..., alias="cashbackAmount")
    """Розмір кешбеку"""
    balance: float
    """Баланс рахунку в мінімальних одиницях валюти (копійках, центах)"""
    comment: str = None
    """Коментар до переказу, уведений користувачем. Якщо не вказаний, поле буде відсутнім"""
    receipt_id: str = Field(None, alias="receiptId")
    """Номер квитанції для check.gov.ua. Поле може бути відсутнім"""
    invoice_id: str = Field(None, alias="invoiceId")
    """Номер квитанції ФОПа, приходить у випадку якщо це операція із зарахуванням коштів"""
    counter_edrpou: str = Field(None, alias="counterEdrpou")
    """ЄДРПОУ контрагента, присутній лише для елементів виписки рахунків ФОП"""
    counter_iban: str = Field(None, alias="counterIban")
    """IBAN контрагента, присутній лише для елементів виписки рахунків ФОП"""
    counter_name: str = Field(None, alias="counterName")
    """Найменування контрагента"""

    @validator('amount', 'operation_amount', 'cashback_amount', 'commission_rate', 'cashback_amount', 'balance',
               pre=True, allow_reuse=True)
    def _convert_from_integer_to_currency_sum(cls, value: int):
        return value / 100

    def get_time_for_timezone(self, timezone: str = 'Europe/Kyiv'):
        """
        The get_time_for_timezone function returns the current time in a given timezone.

        :param self: Represent the instance of the class
        :param timezone: str: Set the default timezone
        :return: The current time in the specified time zone
        """
        return self.time.astimezone(pytz.timezone(timezone))
