from pydantic import BaseModel

from .account import Account
from .jar import Jar


class Client(BaseModel):
    """Інформація про клієнта"""
    id: str
    """Ідентифікатор клієнта (збігається з id для send.monobank.ua)"""
    name: str
    """Ім'я клієнта"""
    webhook_url: str
    """URL для надсилання подій по зміні балансу рахунку"""
    permissions: str
    """Перелік прав, які надає сервіс (1 літера на 1 permission)."""
    accounts: list[Account]
    """Перелік доступних рахунків"""
    jars: list[Jar] = []
    """Перелік банок"""

    class Config:
        fields = {
            'client_id': 'clientId',
            'web_hook_url': 'webHookUrl',
        }
