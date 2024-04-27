from abc import ABC, abstractmethod


class Cache(ABC):

    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def set(self, key, value, expire):
        pass
