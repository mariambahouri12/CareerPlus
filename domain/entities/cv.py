from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CVVersion:
    """A CV version. The LLM never generates one — it only selects one."""

    cv_id: str
    label: str
    project_ids: list[str] = field(default_factory=list)
    file_path: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cv_id": self.cv_id,
            "label": self.label,
            "project_ids": list(self.project_ids),
            "file_path": self.file_path,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CVVersion":
        return cls(
            cv_id=data["cv_id"],
            label=data.get("label", ""),
            project_ids=list(data.get("project_ids", [])),
            file_path=data.get("file_path", ""),
            extra=dict(data.get("extra", {})),
        )