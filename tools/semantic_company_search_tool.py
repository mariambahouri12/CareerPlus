from application.semantic_company_search import SemanticCompanySearchUseCase
from tools.base import BaseTool


class SemanticCompanySearchTool(BaseTool):
    name = "semantic_company_search"
    description = (
        "Semantic retrieval over company descriptions. Use for "
        "descriptive discovery like 'companies working on RAG for "
        "healthcare'. Do not use for deterministic filters."
    )

    def __init__(self, company_retriever, companies_repo, **kwargs):
        self.use_case = SemanticCompanySearchUseCase(company_retriever, companies_repo)

    def run(self, query: str, top_k: int = 5):
        return self.use_case.run(query=query, top_k=top_k)