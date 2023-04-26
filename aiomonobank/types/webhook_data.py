from pydantic import BaseModel

from .statement_item import Statement


class WebhookStatementData(BaseModel):
    account_id: str
    """Ідентифікатор рахунку"""
    statement: Statement
    """Транзакція"""

    class Config:
        fields = {
            'account_id': 'account',
            'statement': 'statementItem',
        }


class WebhookData(BaseModel):
    type: str
    """Тип даних"""
    data: WebhookStatementData
