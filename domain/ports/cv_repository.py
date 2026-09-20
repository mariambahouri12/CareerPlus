from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.cv import CVVersion


class CVRepositoryPort(ABC):
    @abstractmethod
    def all(self) -> list[CVVersion]:
        ...

    @abstractmethod
    def get(self, cv_id: str) -> CVVersion | None:
        ...