"""
Use case: send a prepared application.

Order matters (requirement 11): the email is sent FIRST; the
application record is created ONLY after the send succeeds.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from domain.entities.application import Application
from domain.ports.application_repository import ApplicationRepositoryPort
from domain.ports.email_sender import EmailSenderPort

logger = logging.getLogger(__name__)


class SendApplicationUseCase:
    def __init__(
        self,
        email_sender: EmailSenderPort,
        applications: ApplicationRepositoryPort,
    ) -> None:
        self.email_sender = email_sender
        self.applications = applications

    def run(
        self,
        company: str,
        contact: str,
        subject: str,
        body: str,
        cv_id: str,
        company_id: str | None = None,
        projects_selected: list[str] | None = None,
    ) -> dict:
        # 1. Send
        try:
            result = self.email_sender.send(
                recipient=contact,
                subject=subject,
                body=body,
            )
        except Exception as exc:
            logger.error("Email send failed for %s: %s", company, exc)
            return {
                "status": "error",
                "message": f"Email delivery failed: {exc}",
                "company": company,
                "contact": contact,
            }

        # 2. Record application (only after successful send)
        application = Application(
            application_id=uuid.uuid4().hex,
            company=company,
            company_id=company_id,
            contact=contact,
            cv_id=cv_id,
            sent_at=datetime.now(timezone.utc).isoformat(),
            subject=subject,
            status="sent",
            message_id=result.get("message_id"),
            projects_selected=list(projects_selected or []),
        )
        self.applications.add(application)

        return {
            "status": "success",
            "message": "Email sent and application recorded.",
            "message_id": result.get("message_id"),
            "recipient": contact,
            "application": application.to_dict(),
        }