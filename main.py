"""
Main program loop
"""

from constants import BEGINNING_BALANCE_ENTRY
from control import (
    add_account,
    add_transaction,
    get_account_balances,
    get_account_by_id,
    get_account_by_name,
    get_balance_accounts,
    initialize,
    prime_transaction_header,
)
from entities import *


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


def create_account():
    """
    Prompts user to create an Account
    """

    account_name = input("Account name: ")
    account_types = select((at.id, at.name) for at in AccountType)
    account_type_picklist = generate_picklist(account_types)
    selection = int(input("Select account type #: "))

    add_account(account_name, account_type_picklist[selection])


def add_beginning_balances():
    """
    Prompts the user to enter beginning balances
    """

    accounts = get_balance_accounts()
    account_picklist = generate_picklist(accounts)
    selected_to_account_id = int(input("To account #: "))
    print("")
    amount = input("Amount: ")

    to_account = get_account_by_id(account_picklist[selected_to_account_id])
    from_account = get_account_by_name(BEGINNING_BALANCE_ENTRY)

    transaction_header = prime_transaction_header(note=BEGINNING_BALANCE_ENTRY)
    add_transaction(transaction_header, from_account, to_account, amount)


def view_account_balances():
    """
    View how much is in balance accounts
    """

    balances = get_account_balances()

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
        create_account()

    while input("Enter beginning balances? (Y/n): ").lower() in ["y", "yes"]:
        add_beginning_balances()

    view_account_balances()


if __name__ == "__main__":
    setup()
