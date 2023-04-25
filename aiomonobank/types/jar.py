from typing import Optional

from pydantic import BaseModel, Field, validator


class Jar(BaseModel):
    """Банка клієнта"""
    id: str
    """Ідентифікатор банки"""
    send_id: str = Field(..., alias='sendId')
    """Ідентифікатор для сервісу https://send.monobank.ua/{sendId}"""
    title: str
    """Назва банки"""
    description: str
    """Опис банки"""
    currency_code: int = Field(..., alias='currencyCode')
    """Код валюти банки відповідно ISO 4217"""
    balance: float
    """Баланс банки"""
    goal: Optional[float]
    """Цільова сума для накопичення в банці"""

    @validator('balance', 'goal', pre=True, allow_reuse=True)
    def _convert_from_integer_to_currency_sum(cls, value: int) -> Optional[float]:
        if value is None:
            return value

        return value / 100
