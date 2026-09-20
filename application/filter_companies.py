"""Use case: deterministic filter."""
from __future__ import annotations

from domain.ports.company_repository import CompanyRepositoryPort
from domain.value_objects.company_filter import CompanyFilter


class FilterCompaniesUseCase:
    def __init__(self, repo: CompanyRepositoryPort) -> None:
        self.repo = repo

    def run(self, f: CompanyFilter) -> list[dict]:
        return [c.to_dict() for c in self.repo.filter(f)]