"""
TODO
"""

from datetime import date
from decimal import Decimal

from entities import *


def initialize():
    """
    Create entries for standard account types and beginning balance account
    """

    _ = AccountType(name="Expense")
    _ = AccountType(name="Income")
    _ = AccountType(name="Balance")
    sundry_type = AccountType(name="Sundry & Misc.")

    _ = Account(name="Beginning Balance Entry", account_type=sundry_type)

    commit()


def generate_picklist(entities):
    """
    Given a set of entities in tuples with id and label or name, generate an
    order picklist that maps back to the entity ids and print the picklist
    """

    picklist = {}
    for num, entity in enumerate(entities):

        print(f"{num + 1}. {entity[1]}")
        picklist[num + 1] = entity[0]

    return picklist


def add_account():
    """
    Prompts user to create an Account
    """

    account_name = input("Account name: ")
    account_types = select((at.id, at.name) for at in AccountType)
    account_type_picklist = generate_picklist(account_types)
    selection = int(input("Select account type #: "))
    selected_account_type = AccountType.get(id=account_type_picklist[selection])
    _ = Account(name=account_name, account_type=selected_account_type)

    commit()


def add_beginning_balances():
    """
    Prompts the user to enter beginning balances
    """

    accounts = select(
        (a.id, a.name) for a in Account if a.account_type.name == "Balance"
    )
    account_picklist = generate_picklist(accounts)
    selected_to_account_id = int(input("To account #: "))
    print("")
    amount = input("Amount: ")

    to_account = Account.get(id=account_picklist[selected_to_account_id])
    from_account = Account.get(name="Beginning Balance Entry")

    beginning_balance_transaction = Transaction(
        effective_date=date.today(), note="Beginning balance entry"
    )
    _ = TransactionDetail(
        transaction=beginning_balance_transaction,
        account=from_account,
        amount=(-1 * Decimal(amount)),
    )
    _ = TransactionDetail(
        transaction=beginning_balance_transaction,
        account=to_account,
        amount=Decimal(amount),
    )

    commit()


def view_account_balances():
    """
    View how much is in balance accounts
    """

    balances = select(
        (t.account.name, sum(t.amount))
        for t in TransactionDetail
        if t.account.account_type.name == "Balance"
    )

    for balance in balances:
        print(f"{balance[0]}: ${balance[1]}")


@db_session
def setup():
    """
    Prompt user for perform setup
    """

    account_type_count = select(count(at) for at in AccountType)
    if account_type_count[:][0] == 0:
        initialize()

    while input("Add an account? (Y/n): ").lower() in ["y", "yes"]:
        add_account()

    while input("Enter beginning balances? (Y/n): ").lower() in ["y", "yes"]:
        add_beginning_balances()

    view_account_balances()


if __name__ == "__main__":
    setup()
