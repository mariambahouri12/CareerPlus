from __future__ import annotations

import logging
from typing import Any

import psycopg2
import psycopg2.extras

from domain.entities.company import Company
from domain.ports.company_repository import CompanyRepositoryPort
from domain.value_objects.company_filter import CompanyFilter

logger = logging.getLogger(__name__)


class PostgresCompanyRepository(CompanyRepositoryPort):
    """
    Postgres-backed company repository (works with Supabase).
    """

    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    def _conn(self):
        return psycopg2.connect(self.db_url)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _row_to_company(row: dict) -> Company:
        return Company(
            company_id=row["company_id"],
            name=row["name"],
            domain=row.get("domain") or "",
            website=row.get("website") or "",
            founded_year=row.get("founded_year"),
            size=row.get("size"),
            description=row.get("description") or "",
            contacts=list(row.get("contacts") or []),
            country=row.get("country") or "",
            extra=dict(row.get("extra") or {}),
        )

    # ------------------------------------------------------------------ #
    def get_by_id(self, company_id: str) -> Company | None:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from companies where company_id = %s", (company_id,))
                row = cur.fetchone()
        return self._row_to_company(row) if row else None

    def get_by_name(self, name: str) -> Company | None:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from companies where lower(name) = lower(%s)", (name.strip(),))
                row = cur.fetchone()
        return self._row_to_company(row) if row else None

    def all(self) -> list[Company]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select * from companies order by name")
                rows = cur.fetchall()
        return [self._row_to_company(r) for r in rows]

    def list_contacts(self, company_id: str) -> list[str]:
        c = self.get_by_id(company_id)
        return list(c.contacts) if c else []

    def filter(self, f: CompanyFilter) -> list[Company]:
        clauses: list[str] = []
        params: list[Any] = []

        if f.country:
            clauses.append("lower(country) = lower(%s)")
            params.append(f.country)
        if f.size_max is not None:
            clauses.append("size is not null and size <= %s")
            params.append(f.size_max)
        if f.size_min is not None:
            clauses.append("size is not null and size >= %s")
            params.append(f.size_min)
        if f.founded_after is not None:
            clauses.append("founded_year is not null and founded_year >= %s")
            params.append(f.founded_after)
        if f.founded_before is not None:
            clauses.append("founded_year is not null and founded_year <= %s")
            params.append(f.founded_before)
        if f.domain_contains:
            clauses.append("lower(domain) like lower(%s)")
            params.append(f"%{f.domain_contains}%")
        if f.name_contains:
            clauses.append("lower(name) like lower(%s)")
            params.append(f"%{f.name_contains}%")
        if f.keywords:
            clauses.append("(lower(description) || ' ' || lower(domain)) similar to %s")
            params.append("%(" + "|".join(k.lower() for k in f.keywords) + ")%")

        sql = "select * from companies"
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by name"

        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        return [self._row_to_company(r) for r in rows]