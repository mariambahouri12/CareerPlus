from __future__ import annotations

import logging

import psycopg2
import psycopg2.extras

from domain.entities.cv import CVVersion
from domain.ports.cv_repository import CVRepositoryPort

logger = logging.getLogger(__name__)


class PostgresCVRepository(CVRepositoryPort):
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    def _conn(self):
        return psycopg2.connect(self.db_url)

    @staticmethod
    def _row_to_cv(row: dict) -> CVVersion:
        return CVVersion(
            cv_id=row["cv_id"],
            label=row.get("label") or "",
            project_ids=list(row.get("project_ids") or []),
            file_path=row.get("file_path") or "",
            extra=dict(row.get("extra") or {}),
        )

    def all(self) -> list[CVVersion]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from cvs order by cv_id")
                rows = cur.fetchall()
        return [self._row_to_cv(r) for r in rows]

    def get(self, cv_id: str) -> CVVersion | None:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from cvs where cv_id = %s", (cv_id,))
                row = cur.fetchone()
        return self._row_to_cv(row) if row else None