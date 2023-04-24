from datetime import datetime
import pytz
from pydantic import BaseModel, Field, validator, ValidationError


class Statement(BaseModel):
    id: str
    time: datetime
    description: str
    mcc: int
    original_mcc: int = Field(..., alias="originalMcc")
    hold: bool
    amount: float
    operation_amount: float = Field(..., alias="operationAmount")
    currency_code: int = Field(..., alias="currencyCode")
    commission_rate: float = Field(..., alias="commissionRate")
    cashback_amount: float = Field(..., alias="cashbackAmount")
    balance: float
    comment: str = None
    receipt_id: str = Field(None, alias="receiptId")
    counter_edrpou: str = Field(None, alias="counterEdrpou")
    counter_iban: str = Field(None, alias="counterIban")

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
