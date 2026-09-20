"""
Use case: prepare a personalized application for one company.

Does NOT send anything. Returns a preview:
    - the selected CV id
    - the selected projects
    - the generated email subject + body
    - the recipient
The user must confirm before `send_application` runs.
"""
from __future__ import annotations

import logging

from domain.entities.application import Application
from domain.exceptions import CompanyNotFoundError
from domain.ports.company_repository import CompanyRepositoryPort
from domain.ports.cv_repository import CVRepositoryPort
from domain.ports.project_repository import ProjectRepositoryPort

logger = logging.getLogger(__name__)


class PrepareApplicationUseCase:
    def __init__(
        self,
        companies: CompanyRepositoryPort,
        projects: ProjectRepositoryPort,
        cvs: CVRepositoryPort,
        llm,
    ) -> None:
        self.companies = companies
        self.projects = projects
        self.cvs = cvs
        self.llm = llm

    # ------------------------------------------------------------------ #
    def run(
        self,
        company_name: str,
        recipient: str | None = None,
    ) -> dict:
        company = self.companies.get_by_name(company_name)
        if not company:
            raise CompanyNotFoundError(f"Company '{company_name}' not found.")

        contact = recipient or (company.contacts[0] if company.contacts else "")
        if not contact:
            return {
                "status": "error",
                "message": "No contact email available for this company.",
                "company": company.to_dict(),
            }

        # 1. Select most relevant projects
        keywords = self._keywords_from_company(company.description + " " + company.domain)
        relevant_projects = self.projects.search_by_keywords(keywords)[:3]
        if not relevant_projects:
            relevant_projects = self.projects.all()[:2]

        # 2. Select best CV
        selected_cv = self._select_cv(relevant_projects)

        # 3. Generate email body
        subject, body = self._generate_email(company, relevant_projects, selected_cv)

        return {
            "status": "prepared",
            "company": company.to_dict(),
            "recipient": contact,
            "cv_id": selected_cv.cv_id if selected_cv else "",
            "cv_label": selected_cv.label if selected_cv else "",
            "projects_selected": [p.project_id for p in relevant_projects],
            "projects_names": [p.name for p in relevant_projects],
            "subject": subject,
            "body": body,
        }

    # ------------------------------------------------------------------ #
    def _keywords_from_company(self, text: str) -> list[str]:
        tokens = [t.strip(".,;:()").lower() for t in text.split()]
        stop = {"the", "a", "an", "and", "or", "of", "for", "with", "in", "on", "to", "our", "we"}
        return [t for t in tokens if len(t) > 3 and t not in stop][:12]

    def _select_cv(self, relevant_projects):
        project_ids = {p.project_id for p in relevant_projects}
        best = None
        best_score = -1
        for cv in self.cvs.all():
            overlap = len(set(cv.project_ids) & project_ids)
            if overlap > best_score:
                best_score = overlap
                best = cv
        return best

    def _generate_email(self, company, projects, cv):
        prompt = f"""Write a short, professional spontaneous application email.

RULES:
- 120-160 words max.
- Mention the company by name and one specific element of its activity.
- Mention 1 to 2 projects briefly. Never invent projects.
- Do not invent skills, experience, or achievements.
- End with a polite closing and a signature placeholder.

COMPANY:
Name: {company.name}
Domain: {company.domain}
Country: {company.country}
Description: {company.description}

PROJECTS (only mention these):
{chr(10).join(f"- {p.name}: {p.short_description}" for p in projects)}

Return only the email body (no subject line).
"""
        try:
            body = self.llm.generate(prompt)
        except Exception as exc:
            logger.warning("LLM generation failed, falling back to template: %s", exc)
            body = self._template_email(company, projects)

        subject = f"Spontaneous application – AI / Data Science ({company.name})"
        return subject, body.strip()

    @staticmethod
    def _template_email(company, projects) -> str:
        names = ", ".join(p.name for p in projects[:2])
        return (
            f"Dear {company.name} team,\n\n"
            f"I am writing to express my interest in {company.name}, "
            f"whose work in {company.domain or 'your domain'} strongly resonates with my background.\n\n"
            f"In particular, I have built projects such as {names}, which involve modern "
            f"AI/retrieval engineering practices and align with your activity.\n\n"
            f"I would be delighted to discuss how I could contribute to your team.\n\n"
            f"Best regards,\n[Your name]"
        )