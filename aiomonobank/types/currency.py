from datetime import datetime

import pytz
from pydantic import BaseModel


class Currency(BaseModel):
    """Інформація про курс валют"""

    currency_code_a: str
    """Код валюти рахунку відповідно ISO 4217"""
    currency_code_b: str
    """Код валюти рахунку відповідно ISO 4217"""
    date: datetime
    """Час курсу в форматі UTC time"""
    rate_sell: float
    rate_buy: float
    rate_cross: float

    def get_time_for_timezone(self, timezone: str = 'Europe/Kyiv'):
        """
        The get_time_for_timezone function returns the current time in a given timezone.

        :param self: Represent the instance of the class
        :param timezone: str: Set the default timezone
        :return: The current time in the specified time zone
        """
        return self.date.astimezone(pytz.timezone(timezone))

    class Config:
        fields = {
            'currency_code_a': 'currencyCodeA',
            'currency_code_b': 'currencyCodeB',
            'rate_sell': 'rateSell',
            'rate_buy': 'rateBuy',
            'rate_cross': 'rateCross',
        }
