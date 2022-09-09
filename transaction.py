"""
TODO
"""

from datetime import date

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

    def __repr__(self):
        """
        Pretty output
        """

        if self.header_id:

            return f"""
            Transaction dated {self.effective_date}, 
            ${self.amount} into {self.in_account.name} 
            from {self.out_account.name}, 
            header ID {self.header_id}
            """

        return f"""
            Transaction dated {self.effective_date}, 
            ${self.amount} into {self.in_account.name} 
            from {self.out_account.name}, 
            unsaved
            """

    def __str__(self):
        """
        Print representation as string
        """

        return self.__repr__()

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
            else:
                in_account = transaction_detail.account
                amount = transaction_detail.amount

        return cls(
            in_account,
            out_account,
            amount,
            transaction_header.effective_date,
            transaction_header.note,
            transaction_header.id,
        )

    def save(self):
        """
        Commit the transaction, save to the database
        """

        transaction_header = TransactionHeader(
            effective_date=self.effective_date, note=self.note
        )
        TransactionDetail(
            transaction_header=transaction_header,
            account=self.in_account,
            amount=self.amount,
        )
        TransactionDetail(
            transaction_header=transaction_header,
            account=self.out_account,
            amount=-1 * self.amount,
        )

        if self.valid:
            commit()

        self.header_id = transaction_header.id

    @property
    def valid(self):
        """
        Ensure that the transaction is valid before committing
        This probably doesn't need to be here
        """

        if self.in_account.id == self.out_account.id:
            raise ValueError("Accounts must be different on a transaction")

        return True
