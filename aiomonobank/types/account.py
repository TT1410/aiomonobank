from pydantic import BaseModel, Field, validator, ValidationError


class Account(BaseModel):
    id: str
    send_id: str = Field(..., alias='sendId')
    balance: float
    credit_limit: float = Field(..., alias='creditLimit')
    type: str
    currency_code: int = Field(..., alias='currencyCode')
    cashback_type: str = Field(None, alias='cashbackType')
    masked_pan: list[str] = Field(..., alias='maskedPan')
    iban: str

    @validator('balance', 'credit_limit', pre=True, allow_reuse=True)
    def _convert_from_integer_to_currency_sum(cls, value: int):
        return value / 100
