from __future__ import annotations

import base64
import logging
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from domain.exceptions import EmailDeliveryError
from domain.ports.email_sender import EmailSenderPort

logger = logging.getLogger(__name__)


class GmailSender(EmailSenderPort):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        return build("gmail", "v1", credentials=creds)

    def send(self, recipient: str, subject: str, body: str) -> dict:
        try:
            message = EmailMessage()
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(body)
            encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()

            result = (
                self.service.users().messages()
                .send(userId="me", body={"raw": encoded})
                .execute()
            )
        except Exception as exc:
            raise EmailDeliveryError(f"Gmail send failed: {exc}") from exc

        return {
            "status": "success",
            "message_id": result.get("id"),
            "recipient": recipient,
        }