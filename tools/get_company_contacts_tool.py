from tools.base import BaseTool


class GetCompanyContactsTool(BaseTool):
    name = "get_company_contacts"
    description = "Return the list of contacts for a given company."

    def __init__(self, companies_repo, **kwargs):
        self.repo = companies_repo

    def run(self, company_id: str = "", company_name: str = ""):
        if company_id:
            contacts = self.repo.list_contacts(company_id)
        elif company_name:
            c = self.repo.get_by_name(company_name)
            contacts = list(c.contacts) if c else []
        else:
            return {"status": "error", "message": "Provide company_id or company_name."}
        return {"status": "success", "contacts": contacts}