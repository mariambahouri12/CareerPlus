"""Use case: structured search over the internal company DB."""
from __future__ import annotations

from domain.ports.company_repository import CompanyRepositoryPort
from domain.value_objects.company_filter import CompanyFilter


class SearchCompaniesUseCase:
    def __init__(self, repo: CompanyRepositoryPort) -> None:
        self.repo = repo

    def run(self, f: CompanyFilter) -> list[dict]:
        if f.is_empty():
            return [c.to_dict() for c in self.repo.all()]
        return [c.to_dict() for c in self.repo.filter(f)]