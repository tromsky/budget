from datetime import date
from decimal import Decimal

from pony.orm import *

db = Database()
db.bind(provider="sqlite", filename="budget.db", create_db=True)


class AccountType(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    accounts = Set("Account")


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    account_type = Required(AccountType)
    name = Required(str)
    transaction_details = Set("TransactionDetail")
    budget = Optional("Budget")


class TransactionHeader(db.Entity):
    id = PrimaryKey(int, auto=True)
    effective_date = Required(date)
    note = Optional(str)
    transaction_details = Set("TransactionDetail")


class TransactionDetail(db.Entity):
    id = PrimaryKey(int, auto=True)
    account = Required(Account)
    transaction_header = Required(TransactionHeader)
    amount = Required(Decimal)
    note = Optional(str)


class Budget(db.Entity):
    id = PrimaryKey(int, auto=True)
    amount = Required(Decimal)
    account = Required(Account)


db.generate_mapping(create_tables=True)
