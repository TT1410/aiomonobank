from pydantic import BaseModel, Field, ValidationError

from .statement_item import Statement


class WebhookStatementData(BaseModel):
    account_id: str = Field(..., alias="account")
    statement: Statement = Field(..., alias="statementItem")


class WebhookData(BaseModel):
    type: str
    data: WebhookStatementData


# {
#     'type': 'StatementItem',
#     'data': {
#         'account': 'Zl7GF8QQhjkdKHhfzNbww',
#         'statementItem': {
#             'id': 'jHS2_VhQKJhKoWT-k',
#             'time': 1662905980,
#             'description': 'Термінал IBOX',
#             'mcc': 4829,
#             'originalMcc': 4829,
#             'amount': 69500,
#             'operationAmount': 69500,
#             'currencyCode': 980,
#             'commissionRate': 0,
#             'cashbackAmount': 0,
#             'balance': 19497524,
#             'hold': True
#         }
#     }
# }
