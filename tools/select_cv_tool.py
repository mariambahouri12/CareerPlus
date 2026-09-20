from tools.base import BaseTool


class SelectCVTool(BaseTool):
    name = "select_cv"
    description = (
        "Select the most appropriate existing CV version for a set of "
        "project IDs. The LLM must never generate a CV — only select "
        "an existing one."
    )

    def __init__(self, cvs_repo, **kwargs):
        self.repo = cvs_repo

    def run(self, project_ids: list[str] | None = None, company_description: str = ""):
        project_ids = project_ids or []
        best, best_score = None, -1
        for cv in self.repo.all():
            overlap = len(set(cv.project_ids) & set(project_ids))
            if overlap > best_score:
                best_score = overlap
                best = cv
        if not best:
            return {"status": "error", "message": "No CV versions available."}
        return {"status": "success", "cv": best.to_dict()}