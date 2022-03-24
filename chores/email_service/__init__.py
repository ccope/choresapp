from abc import ABCMeta, abstractmethod
from email.message import Message
from typing import Optional

class EmailProvider(metaclass=ABCMeta):
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
    elif name == "Discord":
        from .discord_post import DiscordMessage
        return DiscordMessage()
    raise Exception("Invalid email provider!")
