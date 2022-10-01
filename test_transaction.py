"""
Unit tests for transaction
"""

import unittest
from datetime import date
from shutil import ExecError

from entities import (
    Account,
    AccountType,
    TransactionDetail,
    TransactionHeader,
    commit,
    db,
    db_session,
    delete,
)
from transaction import Transaction

db.bind(provider="sqlite", filename=":memory:")
db.generate_mapping(create_tables=True)


class TestTransaction(unittest.TestCase):
    @db_session
    def setUp(self):
        delete(account_type for account_type in AccountType)
        self.balance = AccountType(name="balance")
        self.expense = AccountType(name="expense")
        self.chequing = Account(name="chequing", account_type=self.balance)
        self.rent = Account(name="rent", account_type=self.expense)
        commit()

        self.transaction = Transaction(
            self.rent, self.chequing, 100, note="Test delete"
        )
        self.transaction.save()
        self.test_header_id = self.transaction._Transaction__header_id

    @db_session
    def test_create(self):

        rent = Account.get(name="rent")
        chequing = Account.get(name="chequing")

        transaction = Transaction(rent, chequing, 100, note="Hello")
        self.assertFalse(transaction.saved)
        transaction.save()

        th = TransactionHeader.get(id=transaction.header_id)

        td_1 = TransactionDetail.get(id=transaction.in_transaction_detail_id)
        td_2 = TransactionDetail.get(id=transaction.out_transaction_detail_id)

        self.assertTrue(transaction.saved)
        self.assertEqual(th.note, "Hello")
        self.assertEqual(th.effective_date, date.today())
        self.assertEqual(td_1.account.name, "rent")
        self.assertEqual(td_1.amount, 100)
        self.assertEqual(td_2.account.name, "chequing")
        self.assertEqual(td_2.amount, -100)

    @db_session
    def test_get(self):

        rent = Account.get(name="rent")
        chequing = Account.get(name="chequing")

        transaction = Transaction(rent, chequing, 100, note="Hello")
        transaction.save()
        header_id = transaction.header_id
        in_account = transaction.in_account
        out_account = transaction.out_account
        del transaction
        existing_transaction = Transaction.get(header_id)

        self.assertTrue(existing_transaction.saved)
        self.assertEqual(existing_transaction.note, "Hello")
        self.assertEqual(existing_transaction.effective_date, date.today())
        self.assertEqual(existing_transaction.amount, 100)
        self.assertEqual(in_account, rent)
        self.assertEqual(out_account, chequing)

    @db_session
    def test_delete(self):

        transaction = Transaction.get(self.test_header_id)

        transaction.delete()
        deleted_transaction = Transaction.get(self.test_header_id)

        self.assertIsNone(deleted_transaction)
        self.assertTrue(transaction.deleted)
        self.assertFalse(transaction.saved)
        self.assertIsNone(transaction.header_id)

    @db_session
    def test_delete_new_transaction(self):

        rent = Account.get(name="rent")
        chequing = Account.get(name="chequing")

        transaction = Transaction(rent, chequing, 100, note="Hello")

        self.assertRaises(ExecError, transaction.delete)

    @db_session
    def test_transaction_amount_validity(self):
        rent = Account.get(name="rent")
        chequing = Account.get(name="chequing")

        bad_transaction = Transaction(rent, chequing, "NaN", note="Hello")

        self.assertRaises(ValueError, bad_transaction.save)

    @db_session
    def test_transaction_object_equality(self):
        rent = Account.get(name="rent")
        chequing = Account.get(name="chequing")

        transaction1 = Transaction(rent, chequing, 200, note="Hello")
        transaction1.save()
        transaction1Ref = Transaction.get(transaction1.header_id)

        self.assertTrue(transaction1Ref is transaction1)


if __name__ == "__main__":
    unittest.main()
