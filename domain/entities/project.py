from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Project:
    """A project in the internal project knowledge base."""

    project_id: str
    name: str
    short_description: str = ""
    detailed_description: str = ""
    technologies: list[str] = field(default_factory=list)
    ai_concepts: list[str] = field(default_factory=list)
    domain: str = ""
    keywords: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    relevance_tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "short_description": self.short_description,
            "detailed_description": self.detailed_description,
            "technologies": list(self.technologies),
            "ai_concepts": list(self.ai_concepts),
            "domain": self.domain,
            "keywords": list(self.keywords),
            "skills": list(self.skills),
            "relevance_tags": list(self.relevance_tags),
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        return cls(
            project_id=data["project_id"],
            name=data["name"],
            short_description=data.get("short_description", ""),
            detailed_description=data.get("detailed_description", ""),
            technologies=list(data.get("technologies", [])),
            ai_concepts=list(data.get("ai_concepts", [])),
            domain=data.get("domain", ""),
            keywords=list(data.get("keywords", [])),
            skills=list(data.get("skills", [])),
            relevance_tags=list(data.get("relevance_tags", [])),
            extra=dict(data.get("extra", {})),
        )