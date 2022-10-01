from weakref import WeakValueDictionary

from entities import *
from utils import *


class Cache:
    def __init__(self):
        self._cache = WeakValueDictionary()

    def add_or_update(self, transaction):
        self._cache[transaction.header_id] = transaction

    def retrieve(self, header_id):
        if header_id in self._cache:
            if self._cache[header_id].deleted:
                return None
            else:
                return self._cache[header_id]
