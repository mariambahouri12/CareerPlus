from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.project import Project


class ProjectRepositoryPort(ABC):
    @abstractmethod
    def all(self) -> list[Project]:
        ...

    @abstractmethod
    def get(self, project_id: str) -> Project | None:
        ...

    @abstractmethod
    def search_by_keywords(self, keywords: list[str]) -> list[Project]:
        ...