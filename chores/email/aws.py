import boto3

from mypy_boto3_ses import SESClient

from chores.email import EmailProvider


class SesEmail(EmailProvider):
    def init(self):
        self.client: SESClient = boto3.client('ses')

    def send(self, msg):
        self.client.send_raw_email(msg.as_string())
