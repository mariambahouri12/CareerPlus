from application.prepare_application import PrepareApplicationUseCase
from tools.base import BaseTool


class GenerateApplicationEmailTool(BaseTool):
    name = "prepare_application"
    description = (
        "Prepare a personalized spontaneous application for a company. "
        "Returns a preview (recipient, selected CV, selected projects, "
        "subject and body). Nothing is sent — the user must confirm."
    )

    def __init__(self, companies_repo, projects_repo, cvs_repo, llm, **kwargs):
        self.use_case = PrepareApplicationUseCase(
            companies=companies_repo,
            projects=projects_repo,
            cvs=cvs_repo,
            llm=llm,
        )

    def run(self, company_name: str, recipient: str | None = None):
        return self.use_case.run(company_name=company_name, recipient=recipient)