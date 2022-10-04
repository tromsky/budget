from weakref import WeakValueDictionary

from entities import *
from utils import *


class Cache:
    def __init__(self):
        self._cache = WeakValueDictionary()

    def add_or_update(self, id, entity):
        self._cache[id] = entity

    def retrieve(self, id):
        if id not in self._cache:
            return None

        if self._cache[id].deleted:
            return None

        return self._cache[id]
