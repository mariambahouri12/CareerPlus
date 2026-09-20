from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Company:
    """A company record from the internal company database."""

    company_id: str
    name: str
    domain: str = ""
    website: str = ""
    founded_year: Optional[int] = None
    size: Optional[int] = None
    description: str = ""
    contacts: list[str] = field(default_factory=list)
    country: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_id": self.company_id,
            "name": self.name,
            "domain": self.domain,
            "website": self.website,
            "founded_year": self.founded_year,
            "size": self.size,
            "description": self.description,
            "contacts": list(self.contacts),
            "country": self.country,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Company":
        return cls(
            company_id=data["company_id"],
            name=data["name"],
            domain=data.get("domain", ""),
            website=data.get("website", ""),
            founded_year=data.get("founded_year"),
            size=data.get("size"),
            description=data.get("description", ""),
            contacts=list(data.get("contacts", [])),
            country=data.get("country", ""),
            extra=dict(data.get("extra", {})),
        )