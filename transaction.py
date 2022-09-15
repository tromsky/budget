"""
TODO
"""

from datetime import date
from weakref import WeakValueDictionary

from entities import *


class Transaction:
    """
    Class that handles creating, getting, updating and deleting transactions
    which are a combination of a TransactionHeader and pairs of
    TransactionDetails
    """

    _cache = WeakValueDictionary()

    def __new__(cls, *_, **kwargs):
        """
        Override new
        If an object with the same header id exists return that object
        """

        header_id = kwargs.get("__header_id")
        obj = cls._cache.get(header_id)

        if not obj:
            obj = object.__new__(cls)
            cls._cache[header_id] = obj

        return obj

    def __init__(
        self,
        in_account,
        out_account,
        amount,
        *_,
        **kwargs,
    ):
        """
        Stage a transaction
        """

        self.in_account = in_account
        self.out_account = out_account
        self.effective_date = kwargs.get("effective_date", date.today())
        self.amount = amount
        self.note = kwargs.get("note", "")
        # private vars
        self.__header_id = kwargs.get("__header_id")
        self.__in_transaction_detail_id = kwargs.get("__in_transaction_detail_id")
        self.__out_transaction_detail_id = kwargs.get("__out_transaction_detail_id")

        print(self)

    def __repr__(self):
        """
        Pretty output
        """

        if self.__header_id:

            return f"""
            Transaction dated {self.effective_date},
            Noted {self.note},
            ${self.amount} into {self.in_account.name} [{self.__in_transaction_detail_id}]
            from {self.out_account.name} [{self.__out_transaction_detail_id}], 
            header ID {self.__header_id}
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
            effective_date=transaction_header.effective_date,
            note=transaction_header.note,
            __header_id=transaction_header.id,
            __in_transaction_detail_id=in_transaction_detail_id,
            __out_transaction_detail_id=out_transaction_detail_id,
        )

    def save(self):
        """
        Commit the transaction, save to the database
        If the object exists in the database, update it
        """

        if self.__header_id:
            self._update()
        else:

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

            self.__header_id = transaction_header.id
            self.__in_transaction_detail_id = transaction_detail_in.id
            self.__out_transaction_detail_id = transaction_detail_out.id

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

    def _update(self):
        """
        Update a transaction by writing current state back to the database
        """

        transaction_detail_in = TransactionDetail.get(
            id=self.__in_transaction_detail_id
        )
        transaction_detail_out = TransactionDetail.get(
            id=self.__out_transaction_detail_id
        )
        transaction_header = TransactionHeader.get(id=self.__header_id)

        transaction_header.set(effective_date=self.effective_date, note=self.note)

        transaction_detail_in.set(account=self.in_account, amount=self.amount)
        transaction_detail_out.set(account=self.out_account, amount=-1 * self.amount)

        return self
