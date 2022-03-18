from abc import ABCMeta, abstractmethod
from email.message import Message
from typing import Optional

class EmailProvider(metaclass=ABCMeta):
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def send(self, message: Message):
        pass


def get_email_provider(name: Optional[str]) -> EmailProvider:
    if name == "AWS":
        from .aws import SesEmail
        return SesEmail()
    elif name == "Google":
        from .gmail import GMailEmail
        return GMailEmail()
    raise Exception("Invalid email provider!")
