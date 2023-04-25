from pydantic import BaseModel, Field, constr

from .account import Account
from .jar import Jar


class Client(BaseModel):
    """Інформація про клієнта"""
    id: str = Field(..., alias='clientId')
    """Ідентифікатор клієнта (збігається з id для send.monobank.ua)"""
    name: str
    """Ім'я клієнта"""
    webhook_url: str = Field(..., alias='webHookUrl')
    """URL для надсилання подій по зміні балансу рахунку"""
    permissions: str
    """Перелік прав, які надає сервіс (1 літера на 1 permission)."""
    accounts: list[Account]
    """Перелік доступних рахунків"""
    jars: list[Jar] = []
    """Перелік банок"""
