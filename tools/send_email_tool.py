from application.send_application import SendApplicationUseCase
from tools.base import BaseTool


class SendEmailTool(BaseTool):
    name = "send_email"
    description = (
        "Send a personalized application email and record the "
        "application. Requires explicit user confirmation before use."
    )

    def __init__(self, email_sender, applications_repo, **kwargs):
        self.use_case = SendApplicationUseCase(
            email_sender=email_sender,
            applications=applications_repo,
        )

    def run(
        self,
        recipient: str,
        subject: str,
        body: str,
        company: str,
        cv_id: str,
        company_id: str | None = None,
        projects_selected: list[str] | None = None,
    ):
        return self.use_case.run(
            company=company,
            contact=recipient,
            subject=subject,
            body=body,
            cv_id=cv_id,
            company_id=company_id,
            projects_selected=projects_selected,
        )