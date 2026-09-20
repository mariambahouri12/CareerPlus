from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CompanyFilter:
    """Structured filter for deterministic company queries."""

    country: Optional[str] = None
    size_max: Optional[int] = None
    size_min: Optional[int] = None
    founded_after: Optional[int] = None
    founded_before: Optional[int] = None
    domain_contains: Optional[str] = None
    name_contains: Optional[str] = None
    keywords: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not any([
            self.country,
            self.size_max,
            self.size_min,
            self.founded_after,
            self.founded_before,
            self.domain_contains,
            self.name_contains,
            self.keywords,
        ])