import os
from email.message import Message
from discord.webhook.sync import SyncWebhook

from chores.notification_service import NotificationProvider


class DiscordMessage(NotificationProvider):
    def __init__(self):
        WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
        if not WEBHOOK_URL:
            raise Exception("Missing DISCORD_WEBHOOK_URL environment variable")
        self.webhook = SyncWebhook.from_url(WEBHOOK_URL)

    def send(self, msg: Message):
        messages = ["@everyone: {}".format(msg["Subject"])]
        if msg.get_payload():
            messages.append(msg.get_payload())

        for message in messages:
            self.webhook.send(message)
