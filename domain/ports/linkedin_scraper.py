from __future__ import annotations

from abc import ABC, abstractmethod


class LinkedInScraperPort(ABC):
    @abstractmethod
    async def scrape_jobs(
        self,
        job_title: str,
        company_names: list[str] | None = None,
    ) -> list[dict]:
        ...