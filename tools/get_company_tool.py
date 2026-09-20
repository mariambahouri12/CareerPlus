from tools.base import BaseTool


class GetCompanyTool(BaseTool):
    name = "get_company"
    description = (
        "Retrieve a single company record by exact name. Use when the "
        "user mentions a specific company."
    )

    def __init__(self, companies_repo, **kwargs):
        self.repo = companies_repo

    def run(self, name: str):
        c = self.repo.get_by_name(name)
        if not c:
            return {"status": "not_found", "message": f"Company '{name}' not found."}
        return {"status": "success", "company": c.to_dict()}