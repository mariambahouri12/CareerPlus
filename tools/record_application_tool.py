"""
Optional explicit recording tool.

Normally `send_email` records the application after a successful send.
This tool exists so the agent can explicitly record an application in
edge cases (e.g. an application sent outside the tool).
"""
from datetime import datetime, timezone
from uuid import uuid4

from domain.entities.application import Application
from tools.base import BaseTool


class RecordApplicationTool(BaseTool):
    name = "record_application"
    description = (
        "Record an already-sent application. Use only when the email "
        "was sent outside the send_email tool. Normally you should not "
        "need this: send_email records applications automatically."
    )

    def __init__(self, applications_repo, **kwargs):
        self.repo = applications_repo

    def run(
        self,
        company: str,
        contact: str,
        cv_id: str,
        subject: str = "",
        status: str = "sent",
        message_id: str | None = None,
        projects_selected: list[str] | None = None,
    ):
        app = Application(
            application_id=uuid4().hex,
            company=company,
            contact=contact,
            cv_id=cv_id,
            sent_at=datetime.now(timezone.utc).isoformat(),
            subject=subject,
            status=status,
            message_id=message_id,
            projects_selected=list(projects_selected or []),
        )
        self.repo.add(app)
        return {"status": "success", "application": app.to_dict()}