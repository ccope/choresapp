import base64
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from chores.email import EmailProvider

SCOPES = ["https://www.googleapis.com/auth/gmail.send/"]

class GMailEmail(EmailProvider):
    def init(self):
        self.creds = None
        self.service = None
        self.user_id = 'me'

    def refresh_auth(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if not self.creds and os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
            self.service = None
        if not self.service:
            try:
                # Call the Gmail API
                self.service = build('gmail', 'v1', credentials=self.creds)
            except HttpError as error:
                print(f'ERROR: {error}')
                raise error


    def send(self, msg):
        self.refresh_auth()
        serialized_message = {'raw': base64.urlsafe_b64encode(msg.as_string())}
        try:
            message = (self.service.users().messages().send(userId=self.user_id, body=serialized_message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
        except HttpError as e:
            print('An error occurred: %s' % e)
