from pydantic import BaseModel, Field, ValidationError

from .account import Account
from .jar import Jar


class Client(BaseModel):
    id: str = Field(..., alias='clientId')
    name: str
    webhook_url: str = Field(..., alias='webHookUrl')
    permissions: str
    accounts: list[Account]
    jars: list[Jar] = []
