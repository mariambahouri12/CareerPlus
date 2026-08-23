import base64
import os.path

from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def authenticate_gmail():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES,
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )

            creds = flow.run_local_server(
                port=0
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def send_email(
    recipient: str,
    subject: str,
    body: str,
):

    credentials = authenticate_gmail()

    service = build(
        "gmail",
        "v1",
        credentials=credentials,
    )

    message = MIMEText(body)

    message["to"] = recipient
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message
        },
    ).execute()

    print("Email sent successfully!")
    print("Message ID:", result["id"])


if __name__ == "__main__":

    send_email(
        recipient="meriambahouri12@gmail.com",
        subject="CareerPlus Gmail API Test",
        body=(
            "Hello,\n\n"
            "This is a test email sent using "
            "the Gmail API from CareerPlus."
        ),
    )