from __future__ import annotations

from abc import ABC, abstractmethod


class CompanyRetrieverPort(ABC):
    @abstractmethod
    def search(self, query: str, retrieval_k: int = 20) -> list[dict]:
        ...