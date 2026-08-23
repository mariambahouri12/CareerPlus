import base64
from datetime import datetime, timezone
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from storage.application_repository import ApplicationRepository


class SendEmailTool:
    """
    Tool responsible for sending emails through Gmail API.
    """

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ):
        self.credentials_path = credentials_path
        self.token_path = token_path

        self.service = self._authenticate()

        self.application_repository = (
            ApplicationRepository()
        )

    def _authenticate(self):

        credentials = (
            Credentials.from_authorized_user_file(
                self.token_path,
                self.SCOPES,
            )
        )

        return build(
            "gmail",
            "v1",
            credentials=credentials,
        )

    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        company: str,
        spontaneous: bool = True,
    ):

        # -----------------------------------------
        # 1. Create email
        # -----------------------------------------

        message = EmailMessage()

        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        encoded_message = (
            base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()
        )

        # -----------------------------------------
        # 2. Send email
        # -----------------------------------------

        result = (
            self.service
            .users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": encoded_message
                },
            )
            .execute()
        )

        # -----------------------------------------
        # 3. Record application
        # -----------------------------------------

        sent_at = datetime.now(
            timezone.utc
        ).isoformat()

        application = (
            self.application_repository.add(
                company=company,
                email=recipient,
                sent_at=sent_at,
                spontaneous=spontaneous,
                status="pending",
            )
        )

        # -----------------------------------------
        # 4. Return result
        # -----------------------------------------

        return {
            "status": "success",
            "message": "Email sent successfully.",
            "message_id": result.get("id"),
            "recipient": recipient,
            "application": application,
        }