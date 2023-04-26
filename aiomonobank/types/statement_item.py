from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel, validator


class Statement(BaseModel):
    id: str
    """Унікальний id транзакції"""
    time: datetime
    """Час транзакції в секундах в форматі UTC time"""
    description: str
    """Опис транзакцій"""
    mcc: int
    """Код типу транзакції (Merchant Category Code), відповідно ISO 18245"""
    original_mcc: int
    """Оригінальний код типу транзакції (Merchant Category Code), відповідно ISO 18245"""
    hold: bool
    """Статус блокування суми (детальніше https://en.wikipedia.org/wiki/Authorization_hold)"""
    amount: float
    """Сума у валюті рахунку"""
    operation_amount: float
    """Сума у валюті транзакції"""
    currency_code: int
    """Код валюти рахунку відповідно ISO 4217"""
    commission_rate: float
    """Розмір комісії"""
    cashback_amount: float
    """Розмір кешбеку"""
    balance: float
    """Баланс рахунку в мінімальних одиницях валюти (копійках, центах)"""
    comment: Optional[str]
    """Коментар до переказу, уведений користувачем. Якщо не вказаний, поле буде відсутнім"""
    receipt_id: Optional[str]
    """Номер квитанції для check.gov.ua. Поле може бути відсутнім"""
    invoice_id: Optional[str]
    """Номер квитанції ФОПа, приходить у випадку якщо це операція із зарахуванням коштів"""
    counter_edrpou: Optional[str]
    """ЄДРПОУ контрагента, присутній лише для елементів виписки рахунків ФОП"""
    counter_iban: Optional[str]
    """IBAN контрагента, присутній лише для елементів виписки рахунків ФОП"""
    counter_name: Optional[str]
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

    class Config:
        fields = {
            'original_mcc': 'originalMcc',
            'operation_amount': 'operationAmount',
            'currency_code': 'currencyCode',
            'commission_rate': 'commissionRate',
            'cashback_amount': 'cashbackAmount',
            'receipt_id': 'receiptId',
            'invoice_id': 'invoiceId',
            'counter_edrpou': 'counterEdrpou',
            'counter_iban': 'counterIban',
            'counter_name': 'counterName',
        }
