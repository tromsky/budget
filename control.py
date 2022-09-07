"""
Functions to get and manipulate data between front and back-end
"""

from datetime import date
from decimal import Decimal

from constants import BALANCE_ACCOUNT_TYPE, BEGINNING_BALANCE_ENTRY
from entities import *


def add_account(account_name, account_type_id):
    """
    Given an account name and account type entity, adds a new account entity
    """

    selected_account_type = AccountType.get(id=account_type_id)
    _ = Account(name=account_name, account_type=selected_account_type)

    commit()


def initialize():
    """
    Create entries for standard account types and beginning balance account
    """

    _ = AccountType(name="Expense")
    _ = AccountType(name="Income")
    _ = AccountType(name="Balance")
    sundry_type = AccountType(name="Sundry & Misc.")

    _ = Account(name=BEGINNING_BALANCE_ENTRY, account_type=sundry_type)

    commit()


def add_transaction(
    from_account, to_account, amount, effective_date=date.today(), note=None
):
    """
    Record a transaction
    """

    transaction_header = Transaction(effective_date=effective_date, note=note)
    TransactionDetail(
        transaction=transaction_header,
        account=from_account,
        amount=(-1 * Decimal(amount)),
    )
    TransactionDetail(
        transaction=transaction_header,
        account=to_account,
        amount=Decimal(amount),
    )

    commit()


def get_balance_accounts():
    """
    Get the balance accounts
    """

    return select(
        (a.id, a.name) for a in Account if a.account_type.name == BALANCE_ACCOUNT_TYPE
    )


def get_account_by_id(account_id):
    """
    Returns an account based on its id
    """

    return Account.get(id=account_id)


def get_account_by_name(account_name):
    """
    Returns an account based on its name
    """

    return Account.get(name=account_name)


def get_account_balances():
    """
    Returns the total balance of balance type accounts
    """

    return select(
        (t.account.name, sum(t.amount))
        for t in TransactionDetail
        if t.account.account_type.name == "Balance"
    )
