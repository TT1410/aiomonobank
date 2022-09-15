from pydantic import BaseModel, Field, validator, ValidationError


class Jar(BaseModel):
    id: str
    send_id: str = Field(..., alias='sendId')
    title: str
    description: str
    currency_code: int = Field(..., alias='currencyCode')
    balance: float
    goal: float

    @validator('balance', 'goal', pre=True, allow_reuse=True)
    def convert_from_integer_to_currency_sum(cls, value: int):
        return value / 100
