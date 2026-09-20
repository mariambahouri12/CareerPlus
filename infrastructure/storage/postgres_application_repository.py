from __future__ import annotations

import logging

import psycopg2
import psycopg2.extras

from domain.entities.application import Application
from domain.ports.application_repository import ApplicationRepositoryPort

logger = logging.getLogger(__name__)


class PostgresApplicationRepository(ApplicationRepositoryPort):
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    def _conn(self):
        return psycopg2.connect(self.db_url)

    @staticmethod
    def _row_to_application(row: dict) -> Application:
        return Application(
            application_id=row.get("application_id"),
            company=row["company"],
            company_id=row.get("company_id"),
            contact=row["contact"],
            cv_id=row["cv_id"],
            sent_at=row["sent_at"].isoformat() if row.get("sent_at") else "",
            subject=row.get("subject") or "",
            status=row.get("status") or "pending",
            message_id=row.get("message_id"),
            projects_selected=list(row.get("projects_selected") or []),
            error=row.get("error"),
            extra=dict(row.get("extra") or {}),
        )

    def add(self, application: Application) -> Application:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into applications (
                        application_id, company, company_id, contact, cv_id,
                        sent_at, subject, status, message_id,
                        projects_selected, error, extra
                    ) values (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        application.application_id,
                        application.company,
                        application.company_id,
                        application.contact,
                        application.cv_id,
                        application.sent_at,
                        application.subject,
                        application.status,
                        application.message_id,
                        application.projects_selected,
                        application.error,
                        psycopg2.extras.Json(application.extra),
                    ),
                )
            conn.commit()
        logger.info("Recorded application for %s (cv=%s)", application.company, application.cv_id)
        return application

    def all(self) -> list[Application]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from applications order by sent_at desc")
                rows = cur.fetchall()
        return [self._row_to_application(r) for r in rows]