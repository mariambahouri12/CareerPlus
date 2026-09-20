from tools.base import BaseTool


class GetProjectsTool(BaseTool):
    name = "get_projects"
    description = (
        "Return projects from the internal knowledge base whose "
        "keywords match the given list. The LLM must only mention "
        "projects returned by this tool."
    )

    def __init__(self, projects_repo, **kwargs):
        self.repo = projects_repo

    def run(self, keywords: list[str] | None = None, limit: int = 5):
        if keywords:
            projects = self.repo.search_by_keywords(keywords)
        else:
            projects = self.repo.all()
        return {
            "status": "success",
            "count": len(projects[:limit]),
            "projects": [p.to_dict() for p in projects[:limit]],
        }