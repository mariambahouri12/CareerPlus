from __future__ import annotations

import logging

import psycopg2
import psycopg2.extras

from domain.entities.project import Project
from domain.ports.project_repository import ProjectRepositoryPort

logger = logging.getLogger(__name__)


class PostgresProjectRepository(ProjectRepositoryPort):
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    def _conn(self):
        return psycopg2.connect(self.db_url)

    @staticmethod
    def _row_to_project(row: dict) -> Project:
        return Project(
            project_id=row["project_id"],
            name=row["name"],
            short_description=row.get("short_description") or "",
            detailed_description=row.get("detailed_description") or "",
            technologies=list(row.get("technologies") or []),
            ai_concepts=list(row.get("ai_concepts") or []),
            domain=row.get("domain") or "",
            keywords=list(row.get("keywords") or []),
            skills=list(row.get("skills") or []),
            relevance_tags=list(row.get("relevance_tags") or []),
            extra=dict(row.get("extra") or {}),
        )

    def all(self) -> list[Project]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from projects order by name")
                rows = cur.fetchall()
        return [self._row_to_project(r) for r in rows]

    def get(self, project_id: str) -> Project | None:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from projects where project_id = %s", (project_id,))
                row = cur.fetchone()
        return self._row_to_project(row) if row else None

    def search_by_keywords(self, keywords: list[str]) -> list[Project]:
        if not keywords:
            return self.all()

        # Score in Python: number of keywords matched across all text fields.
        projects = self.all()
        kws = [k.lower() for k in keywords]

        def score(p: Project) -> int:
            blob = " ".join([
                p.name, p.domain, p.short_description, p.detailed_description,
                " ".join(p.technologies), " ".join(p.ai_concepts),
                " ".join(p.keywords), " ".join(p.skills),
                " ".join(p.relevance_tags),
            ]).lower()
            return sum(1 for k in kws if k in blob)

        scored = [(p, score(p)) for p in projects]
        scored = [(p, s) for p, s in scored if s > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]