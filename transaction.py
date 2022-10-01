"""
TODO
"""


from datetime import date
from email import header
from shutil import ExecError
from weakref import WeakValueDictionary

from entities import *
from utils import *


class Transaction:
    """
    Class that handles creating, getting, updating, and deleteing transactions
    which are a combination of a TransactionHeader and pairs of
    TransactionDetails
    """

    # cached so factories return the same object reference
    _cache = WeakValueDictionary()
    __tracked_attrs = [
        "in_account",
        "out_account",
        "amount",
        "note",
        "effective_date",
    ]

    def __new__(cls, *_, **kwargs):
        """
        Override new
        If an object with the same header id exists return that object
        """

        # TODO: If you
        #   1. create a new Transaction
        #   2. save it
        #   3. get a transaction with the same header id
        # the objects will not be equal but if you get get two Transactions
        # with the same header id, they will be...

        header_id = kwargs.get("__header_id")
        obj = cls._cache.get(header_id)

        if not obj:
            obj = object.__new__(cls)

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
        self.saved = kwargs.get("__saved", False)
        self.deleted = kwargs.get("__deleted", False)
        # private vars
        self.__header_id = kwargs.get("__header_id")
        self.__in_transaction_detail_id = kwargs.get("__in_transaction_detail_id")
        self.__out_transaction_detail_id = kwargs.get("__out_transaction_detail_id")

        print(self)

    @property
    def header_id(self):
        """
        Transaction Header ID
        """
        return self.__header_id

    @property
    def in_transaction_detail_id(self):
        """
        Transaction Detail In ID
        """
        return self.__in_transaction_detail_id

    @property
    def out_transaction_detail_id(self):
        """
        Transaction Detail Out ID
        """
        return self.__out_transaction_detail_id

    def __setattr__(self, key, value):
        if key in self.__tracked_attrs:
            setattr(self, "saved", False)
        super().__setattr__(key, value)

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
            Saved: {self.saved}
            """

        return f"""
            Transaction dated {self.effective_date}, 
            Noted {self.note},
            ${self.amount} into {self.in_account.name} 
            from {self.out_account.name}, 
            Saved: {self.saved}
            """

    def __str__(self):
        """
        Print representation as string
        """

        return self.__repr__()

    @classmethod
    @db_session
    def get(cls, header_id):
        """
        Get a transaction based on header id
        """
        if cls._cache[header_id]:
            return cls._cache[header_id]

        transaction_header = TransactionHeader.get(id=header_id)
        if not transaction_header:
            # no results
            return None

        transaction_details = transaction_header.transaction_details

        for transaction_detail in transaction_details:
            if transaction_detail.amount < 0:
                out_account = transaction_detail.account
                out_transaction_detail_id = transaction_detail.id
                out_transaction_detail_id = transaction_detail.id
            else:
                in_account = transaction_detail.account
                in_transaction_detail_id = transaction_detail.id
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
            __saved=True,
        )

    @db_session
    def save(self):
        """
        Commit the transaction, save to the database
        If the object exists in the database, update it
        If the object exists in the database, update it
        """

        if self.saved:
            raise ValueError(f"Transaction {self.__header_id} has already been saved")

        try:
            self.valid
        except ValueError as e:
            raise e

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

            commit()

            self.__header_id = transaction_header.id
            self.__in_transaction_detail_id = transaction_detail_in.id
            self.__out_transaction_detail_id = transaction_detail_out.id

        self.saved = "True"
        self._cache[self.header_id] = self

    def reverse(self):
        """
        Reverses a transaction while keeping its records
        """

        if not self.__header_id:
            raise ExecError("Cannot revserse an unsaved transaciton")

        self.in_account, self.out_account = self.out_account, self.in_account
        self.saved = False
        self.note = f"Reversing transaction for {self.__header_id}"
        self.effective_date = date.today()
        self.__header_id = None
        self.__in_transaction_detail_id = None
        self.__out_transaction_detail_id = None

        return self

    @db_session
    def delete(self):
        """
        Hard delete transaction
        """

        if not self.__header_id:
            raise ExecError("Cannot delete and unsaved transaction")

        transaction_header = TransactionHeader.get(id=self.__header_id)
        transaction_header.delete()  # cascade deletes the details
        commit()

        self.deleted = True
        self.saved = False
        self.__header_id = None
        self.__in_transaction_detail_id = None
        self.__out_transaction_detail_id = None

    @property
    def valid(self):
        """
        Ensure that the transaction is valid before committing
        This probably doesn't need to be here

        TODO: Determine if this is actually needed

        TODO: Determine if this is actually needed
        """

        if self.in_account.id == self.out_account.id:
            raise ValueError("Accounts must be different on a transaction")

        if not is_number(self.amount):
            raise ValueError("Amount must be a number")

        return True

    @db_session
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
