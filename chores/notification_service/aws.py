import boto3

from mypy_boto3_ses import SESClient

from chores.notification_service import NotificationProvider


class SesEmail(NotificationProvider):
    def __init__(self):
        self.client: SESClient = boto3.client("ses")

    def send(self, msg):
        self.client.send_raw_email(msg.as_string())
