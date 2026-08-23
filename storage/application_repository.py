import json
from pathlib import Path
from typing import Dict, List


class ApplicationRepository:
    """
    Store job applications in a local JSON file.
    """

    def __init__(
        self,
        file_path: str = "data/applications.json",
    ):
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self._save([])

    def _load(self) -> List[Dict]:
        with open(
            self.file_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _save(self, applications: List[Dict]) -> None:
        with open(
            self.file_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                applications,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def add(
        self,
        company: str,
        email: str,
        sent_at: str,
        spontaneous: bool = True,
        status: str = "pending",
    ) -> Dict:

        application = {
            "company": company,
            "email": email,
            "sent_at": sent_at,
            "spontaneous": spontaneous,
            "status": status,
        }

        applications = self._load()

        applications.append(application)

        self._save(applications)

        return application