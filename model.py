from datetime import datetime

from pydantic import BaseModel, confloat


class DepositWithdraw(BaseModel):
    client: str
    amount: confloat(ge=0.00)
    description: str


class BankStatement(BaseModel):
    client: str
    since: datetime
    till: datetime


