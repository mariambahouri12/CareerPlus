from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.application import Application


class ApplicationRepositoryPort(ABC):
    @abstractmethod
    def add(self, application: Application) -> Application:
        ...

    @abstractmethod
    def all(self) -> list[Application]:
        ...