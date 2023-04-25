from pydantic import BaseModel, Field, ValidationError

from .statement_item import Statement


class WebhookStatementData(BaseModel):
    account_id: str = Field(..., alias="account")
    """Ідентифікатор рахунку"""
    statement: Statement = Field(..., alias="statementItem")
    """"""


class WebhookData(BaseModel):
    type: str
    data: WebhookStatementData
