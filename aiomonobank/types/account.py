from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, validator


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
    send_id: str = Field(..., alias='sendId')
    """Ідентифікатор для сервісу https://send.monobank.ua/{sendId}"""
    balance: float
    """Баланс рахунку в мінімальних одиницях валюти (копійках, центах)"""
    credit_limit: float = Field(..., alias='creditLimit')
    """Кредитний ліміт"""
    type: AccountTypeEnum
    """Тип рахунку"""
    currency_code: int = Field(..., alias='currencyCode')
    """Код валюти рахунку відповідно ISO 4217"""
    cashback_type: Optional[CashbackType] = Field(None, alias='cashbackType')
    """Тип кешбеку який нараховується на рахунок"""
    masked_pan: list[str] = Field(..., alias='maskedPan')
    """Перелік замаскованих номерів карт (більше одного може бути у преміальних карт)"""
    iban: str
    """IBAN рахунку"""

    @validator('balance', 'credit_limit', pre=True, allow_reuse=True)
    def _convert_from_integer_to_currency_sum(cls, value: int):
        return value / 100
