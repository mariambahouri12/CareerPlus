import json
from pathlib import Path
from typing import List, Dict


class JobRepository:
    """Persistent storage for scraped job offers."""

    def __init__(self, path: str = "data/jobs.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, jobs: List[Dict]) -> None:
        """Save jobs to JSON."""

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                jobs,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def load(self) -> List[Dict]:
        """Load jobs from JSON."""

        if not self.path.exists():
            return []

        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)