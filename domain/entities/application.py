from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Application:
    """A recorded job application."""

    company: str
    contact: str
    cv_id: str
    sent_at: str
    application_id: Optional[str] = None
    subject: str = ""
    status: str = "pending"
    company_id: Optional[str] = None
    message_id: Optional[str] = None
    projects_selected: list[str] = field(default_factory=list)
    error: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "company": self.company,
            "company_id": self.company_id,
            "contact": self.contact,
            "cv_id": self.cv_id,
            "sent_at": self.sent_at,
            "subject": self.subject,
            "status": self.status,
            "message_id": self.message_id,
            "projects_selected": list(self.projects_selected),
            "error": self.error,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Application":
        return cls(
            application_id=data.get("application_id"),
            company=data["company"],
            company_id=data.get("company_id"),
            contact=data["contact"],
            cv_id=data["cv_id"],
            sent_at=data["sent_at"],
            subject=data.get("subject", ""),
            status=data.get("status", "pending"),
            message_id=data.get("message_id"),
            projects_selected=list(data.get("projects_selected", [])),
            error=data.get("error"),
            extra=dict(data.get("extra", {})),
        )