from application.filter_companies import FilterCompaniesUseCase
from domain.value_objects.company_filter import CompanyFilter
from tools.base import BaseTool


class SearchCompaniesTool(BaseTool):
    name = "search_companies"
    description = (
        "Structured search over the internal company database. Use for "
        "deterministic queries (country, size, founding year, domain "
        "keyword). Returns a dataset of companies."
    )

    def __init__(self, companies_repo, **kwargs):
        self.use_case = FilterCompaniesUseCase(companies_repo)

    def run(self, **kwargs):
        f = CompanyFilter(
            country=kwargs.get("country"),
            size_max=kwargs.get("size_max"),
            size_min=kwargs.get("size_min"),
            founded_after=kwargs.get("founded_after"),
            founded_before=kwargs.get("founded_before"),
            domain_contains=kwargs.get("domain_contains"),
            name_contains=kwargs.get("name_contains"),
            keywords=list(kwargs.get("keywords", [])),
        )
        results = self.use_case.run(f)
        return {"status": "success", "matches_found": len(results), "results": results}