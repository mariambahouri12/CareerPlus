from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.company import Company
from domain.value_objects.company_filter import CompanyFilter


class CompanyRepositoryPort(ABC):
    @abstractmethod
    def get_by_id(self, company_id: str) -> Company | None:
        ...

    @abstractmethod
    def get_by_name(self, name: str) -> Company | None:
        ...

    @abstractmethod
    def filter(self, f: CompanyFilter) -> list[Company]:
        ...

    @abstractmethod
    def all(self) -> list[Company]:
        ...

    @abstractmethod
    def list_contacts(self, company_id: str) -> list[str]:
        ...