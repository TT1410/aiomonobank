from typing import Optional

from pydantic import BaseModel, Field, validator, ValidationError


class Jar(BaseModel):
    id: str
    send_id: str = Field(..., alias='sendId')
    title: str
    description: str
    currency_code: int = Field(..., alias='currencyCode')
    balance: float
    goal: Optional[float]

    @validator('balance', 'goal', pre=True, allow_reuse=True)
    def _convert_from_integer_to_currency_sum(cls, value: int) -> Optional[float]:
        if value is None:
            return value

        return value / 100
