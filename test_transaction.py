"""
Unit tests for transaction
"""

import unittest
from datetime import date

from entities import (
    Account,
    AccountType,
    TransactionDetail,
    TransactionHeader,
    commit,
    db,
    db_session,
)
from transaction import Transaction

db.bind(provider="sqlite", filename=":memory:")
db.generate_mapping(create_tables=True)


class TestTransaction(unittest.TestCase):
    def setUp(self):
        pass

    @db_session
    def test_create(self):

        balance = AccountType(name="balance")
        expense = AccountType(name="expense")
        chequing = Account(name="chequing", account_type=balance)
        rent = Account(name="rent", account_type=expense)
        commit()

        transaction = Transaction(rent, chequing, 100, note="Hello")
        self.assertFalse(transaction.saved)
        transaction.save()

        th = TransactionHeader.get(id=transaction._Transaction__header_id)

        td_1 = TransactionDetail.get(
            id=transaction._Transaction__in_transaction_detail_id
        )
        td_2 = TransactionDetail.get(
            id=transaction._Transaction__out_transaction_detail_id
        )

        self.assertTrue(transaction.saved)
        self.assertEqual(th.note, "Hello")
        self.assertEqual(th.effective_date, date.today())
        self.assertEqual(td_1.account.name, "rent")
        self.assertEqual(td_1.amount, 100)
        self.assertEqual(td_2.account.name, "chequing")
        self.assertEqual(td_2.amount, -100)

    @db_session
    def test_get(self):

        balance = AccountType(name="balance")
        expense = AccountType(name="expense")
        chequing = Account(name="chequing", account_type=balance)
        rent = Account(name="rent", account_type=expense)
        commit()

        transaction = Transaction(rent, chequing, 100, note="Hello")
        transaction.save()
        header_id = transaction._Transaction__header_id

        existing_transaction = Transaction.get(header_id)

        self.assertTrue(existing_transaction.saved)
        self.assertEqual(existing_transaction.note, "Hello")
        self.assertEqual(existing_transaction.effective_date, date.today())
        self.assertEqual(existing_transaction.amount, 100)


if __name__ == "__main__":
    unittest.main()
