from abc import ABCMeta, abstractmethod
from email.message import Message

class EmailProvider(metaclass=ABCMeta):
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def send(self, message: Message):
        pass


