"""
Constants
"""

from enum import Enum

BALANCE_ACCOUNT_TYPE = "Balance"
BEGINNING_BALANCE_ENTRY = "Beginning Balance Entry"


class TransactionDetailTypes(Enum):
    IN = "in"
    OUT = "out"


TRANSACTION_DETAIL_TYPE_CHOICES = {
    v.value for v in dict(TransactionDetailTypes.__members__).values()
}
