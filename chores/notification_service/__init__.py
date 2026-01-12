from abc import ABCMeta, abstractmethod
from email.message import Message
from typing import Optional


class NotificationProvider(metaclass=ABCMeta):
    @abstractmethod
    def send(self, message: Message):
        pass


def get_notification_provider(name: Optional[str]) -> NotificationProvider:
    if name == "AWS":
        from .aws import SesEmail

        return SesEmail()
    elif name == "Google":
        from .gmail import GMailEmail

        return GMailEmail()
    elif name == "Discord":
        from .discord_post import DiscordMessage

        return DiscordMessage()
    elif name == "None" or not name:
        # Dummy provider for testing
        class DummyProvider(NotificationProvider):
            def send(self, message: Message):
                print(f"Dummy send: {message.get('Subject')}")
        return DummyProvider()
    raise Exception("Invalid notification provider!")
