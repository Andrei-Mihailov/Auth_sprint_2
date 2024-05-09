from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    async def get(self, index, id):
        pass

    @abstractmethod
    async def search(self, index, body):
        pass
