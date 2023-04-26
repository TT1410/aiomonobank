from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, validator


class AccountTypeEnum(StrEnum):
    BLACK = "black"
    WHITE = "white"
    PLATINUM = "platinum"
    IRON = "iron"
    FOP = "fop"
    YELLOW = "yellow"
    EAID = "eAid"


class CashbackType(StrEnum):
    NONE = "None"
    UAH = "UAH"
    MILES = "Miles"


class Account(BaseModel):
    """Рахунок клієнта"""
    id: str
    """Ідентифікатор рахунку"""
    send_id: str
    """Ідентифікатор для сервісу https://send.monobank.ua/{sendId}"""
    balance: float
    """Баланс рахунку в мінімальних одиницях валюти (копійках, центах)"""
    credit_limit: float
    """Кредитний ліміт"""
    type: AccountTypeEnum
    """Тип рахунку"""
    currency_code: int
    """Код валюти рахунку відповідно ISO 4217"""
    cashback_type: Optional[CashbackType]
    """Тип кешбеку який нараховується на рахунок"""
    masked_pan: list[str]
    """Перелік замаскованих номерів карт (більше одного може бути у преміальних карт)"""
    iban: str
    """IBAN рахунку"""

    @validator('balance', 'credit_limit', pre=True, allow_reuse=True)
    def _convert_from_integer_to_currency_sum(cls, value: int):
        return value / 100

    class Config:
        fields = {
            'send_id': 'sendId',
            'credit_limit': 'creditLimit',
            'currency_code': 'currencyCode',
            'cashback_type': 'cashbackType',
            'masked_pan': 'maskedPan',
        }
