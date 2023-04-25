from datetime import datetime

from pydantic import BaseModel, Field, validator


class Currency(BaseModel):
    """Інформація про курс валют"""

    currency_code_a: str = Field(..., alias='currencyCodeA')
    """Код валюти рахунку відповідно ISO 4217"""
    currency_code_b: str = Field(..., alias='currencyCodeB')
    """Код валюти рахунку відповідно ISO 4217"""
    date: datetime
    """Час курсу в форматі UTC time"""
    rate_sell: float = Field(..., alias='rateSell')
    rate_buy: float = Field(..., alias='rateBuy')
    rate_cross: float = Field(..., alias='rateCross')

    # @validator('balance', 'credit_limit', pre=True, allow_reuse=True)
    # def _convert_from_integer_to_currency_sum(cls, value: int):
    #     return value / 100
