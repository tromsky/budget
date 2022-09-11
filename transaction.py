"""
TODO
"""

from datetime import date

from constants import TRANSACTION_DETAIL_TYPE_CHOICES, TransactionDetailTypes
from entities import *


class Transaction:
    """
    Class that handles creating, getting, updating and deleting transactions
    which are a combination of a TransactionHeader and pairs of
    TransactionDetails
    """

    def __init__(
        self,
        in_account,
        out_account,
        amount,
        effective_date=date.today(),
        note="",
        header_id=None,
        in_transaction_detail_id=None,
        out_transaction_detail_id=None,
    ):
        """
        Stage a transaction
        """

        self.in_account = in_account
        self.out_account = out_account
        self.effective_date = effective_date
        self.amount = amount
        self.note = note
        self.header_id = header_id
        self.in_transaction_detail_id = in_transaction_detail_id
        self.out_transaction_detail_id = out_transaction_detail_id

    def __repr__(self):
        """
        Pretty output
        """

        if self.header_id:

            return f"""
            Transaction dated {self.effective_date},
            Noted {self.note},
            ${self.amount} into {self.in_account.name} [{self.in_transaction_detail_id}]
            from {self.out_account.name} [{self.out_transaction_detail_id}], 
            header ID {self.header_id}
            """

        return f"""
            Transaction dated {self.effective_date}, 
            Noted {self.note},
            ${self.amount} into {self.in_account.name} 
            from {self.out_account.name}, 
            unsaved
            """

    def __str__(self):
        """
        Print representation as string
        """

        return self.__repr__()

    def _get(self, header_id):
        """
        Private method for getting a transaction on an existing
        object

        This _method is intented to be used after an update call
        but shares a lot in common with the class method...how to
        keep it DRY?
        """

        transaction_header = TransactionHeader.get(id=header_id)
        transaction_details = transaction_header.transaction_details
        for transaction_detail in transaction_details:
            if transaction_detail.amount < 0:
                out_account = transaction_detail.account
                out_transaction_detail_id = transaction_detail.id
            else:
                in_account = transaction_detail.account
                in_transaction_detail_id = transaction_detail.id
                amount = transaction_detail.amount

        self.in_account = in_account
        self.out_account = out_account
        self.amount = amount
        self.note = transaction_header.note
        self.effective_date = transaction_header.effective_date
        self.in_transaction_detail_id = in_transaction_detail_id
        self.out_transaction_detail_id = out_transaction_detail_id

        return self

    @classmethod
    def get(cls, header_id):
        """
        Get a transaction based on header id
        """

        transaction_header = TransactionHeader.get(id=header_id)
        transaction_details = transaction_header.transaction_details

        for transaction_detail in transaction_details:
            if transaction_detail.amount < 0:
                out_account = transaction_detail.account
                out_transaction_detail_id = transaction_detail.id
            else:
                in_account = transaction_detail.account
                in_transaction_detail_id = transaction_detail.id
                amount = transaction_detail.amount

        return cls(
            in_account,
            out_account,
            amount,
            transaction_header.effective_date,
            transaction_header.note,
            transaction_header.id,
            in_transaction_detail_id,
            out_transaction_detail_id,
        )

    def save(self):
        """
        Commit the transaction, save to the database
        """

        transaction_header = TransactionHeader(
            effective_date=self.effective_date, note=self.note
        )
        transaction_detail_in = TransactionDetail(
            transaction_header=transaction_header,
            account=self.in_account,
            amount=self.amount,
        )
        transaction_detail_out = TransactionDetail(
            transaction_header=transaction_header,
            account=self.out_account,
            amount=-1 * self.amount,
        )

        if self.valid:
            commit()

        self.header_id = transaction_header.id
        self.in_transaction_detail_id = transaction_detail_in.id
        self.out_transaction_detail_id = transaction_detail_out.id

    @property
    def valid(self):
        """
        Ensure that the transaction is valid before committing
        This probably doesn't need to be here

        TODO: Determine if this is actually needed
        """

        if self.in_account.id == self.out_account.id:
            raise ValueError("Accounts must be different on a transaction")

        return True

    def _prime_header_update(self, effective_date=None, note=None):
        """
        Creates a dictionary of header attributes to update
        """

        header_update_attributes = {}

        if effective_date:
            header_update_attributes["effective_date"] = effective_date

        if note:
            header_update_attributes["note"] = note

        return header_update_attributes

    def _prime_detail_update(self, detail_type, account=None, amount=None):
        """
        Creates a dictionary of detail attributes to update
        """

        details_attributes = {}

        detail_type = detail_type.value

        if detail_type not in TRANSACTION_DETAIL_TYPE_CHOICES:
            raise ValueError(
                f"Bad detail type {detail_type}, use one of {TRANSACTION_DETAIL_TYPE_CHOICES}"
            )

        if amount:
            if detail_type == TransactionDetailTypes.IN:
                details_attributes["amount"] = amount
            if detail_type == TransactionDetailTypes.OUT:
                details_attributes["amount"] = -1 * amount

        if account:
            details_attributes["account"] = account

        return details_attributes

    def update(
        self,
        in_account=None,
        out_account=None,
        amount=None,
        effective_date=None,
        note=None,
    ):
        """
        Update a transaction
        """

        transaction_detail_in = TransactionDetail.get(id=self.in_transaction_detail_id)
        transaction_detail_out = TransactionDetail.get(
            id=self.out_transaction_detail_id
        )
        transaction_header = TransactionHeader.get(id=self.header_id)

        header_update_attributes = self._prime_header_update(effective_date, note)
        in_details_attributes = self._prime_detail_update(
            TransactionDetailTypes.IN, in_account, amount
        )
        out_details_attributes = self._prime_detail_update(
            TransactionDetailTypes.OUT, out_account, amount
        )

        if header_update_attributes:
            transaction_header.set(**header_update_attributes)

        if in_details_attributes:
            transaction_detail_in.set(**in_details_attributes)

        if out_details_attributes:
            transaction_detail_out.set(**out_details_attributes)

        commit()

        return self._get(self.header_id)
