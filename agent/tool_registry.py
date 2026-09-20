import asyncio
from typing import Any, Dict

from tools.filter_companies_tool import FilterCompaniesTool
from tools.generate_application_email_tool import GenerateApplicationEmailTool
from tools.get_company_contacts_tool import GetCompanyContactsTool
from tools.get_company_tool import GetCompanyTool
from tools.get_projects_tool import GetProjectsTool
from tools.scrape_linkedin_tool import ScrapeLinkedInTool
from tools.search_companies_tool import SearchCompaniesTool
from tools.select_cv_tool import SelectCVTool
from tools.semantic_company_search_tool import SemanticCompanySearchTool
from tools.send_email_tool import SendEmailTool


class ToolRegistry:
    """
    Registry of tools exposed to the agent.

    Instances are lazy: created on first execution. Schemas are read
    from the classes directly (no instantiation needed).
    """

    _TOOL_CLASSES = {
        "search_companies": SearchCompaniesTool,
        "filter_companies": FilterCompaniesTool,
        "get_company": GetCompanyTool,
        "semantic_company_search": SemanticCompanySearchTool,
        "get_company_contacts": GetCompanyContactsTool,
        "scrape_linkedin": ScrapeLinkedInTool,
        "get_projects": GetProjectsTool,
        "select_cv": SelectCVTool,
        "prepare_application": GenerateApplicationEmailTool,
        "send_email": SendEmailTool,
    }

    def __init__(self, shared: Dict[str, Any] | None = None):
        # The registry receives shared singletons (repositories, llm…)
        # so tools can be wired lazily.
        self._shared = shared or {}
        self._instances: Dict[str, Any] = {}

    def _get_tool(self, name: str):
        if name not in self._instances:
            cls = self._TOOL_CLASSES[name]
            self._instances[name] = cls(**self._shared)
        return self._instances[name]

    # ------------------------------------------------------------------ #
    def schemas(self) -> list[Dict[str, Any]]:
        return [
            self._schema("search_companies", SearchCompaniesTool, {
                "country": {"type": "string"},
                "size_max": {"type": "integer"},
                "size_min": {"type": "integer"},
                "founded_after": {"type": "integer"},
                "founded_before": {"type": "integer"},
                "domain_contains": {"type": "string"},
                "name_contains": {"type": "string"},
                "keywords": {"type": "array", "items": {"type": "string"}},
            }),
            self._schema("filter_companies", FilterCompaniesTool, {
                "country": {"type": "string"},
                "size_max": {"type": "integer"},
                "size_min": {"type": "integer"},
                "founded_after": {"type": "integer"},
                "founded_before": {"type": "integer"},
                "domain_contains": {"type": "string"},
                "name_contains": {"type": "string"},
                "keywords": {"type": "array", "items": {"type": "string"}},
            }),
            self._schema("get_company", GetCompanyTool, {
                "name": {"type": "string"},
            }, required=["name"]),
            self._schema("semantic_company_search", SemanticCompanySearchTool, {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20},
            }, required=["query"]),
            self._schema("get_company_contacts", GetCompanyContactsTool, {
                "company_id": {"type": "string"},
                "company_name": {"type": "string"},
            }),
            self._schema("scrape_linkedin", ScrapeLinkedInTool, {
                "job_title": {"type": "string"},
                "company_names": {"type": "array", "items": {"type": "string"}},
            }, required=["job_title"]),
            self._schema("get_projects", GetProjectsTool, {
                "keywords": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
            }),
            self._schema("select_cv", SelectCVTool, {
                "project_ids": {"type": "array", "items": {"type": "string"}},
                "company_description": {"type": "string"},
            }),
            self._schema("prepare_application", GenerateApplicationEmailTool, {
                "company_name": {"type": "string"},
                "recipient": {"type": "string"},
            }, required=["company_name"]),
            self._schema("send_email", SendEmailTool, {
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "company": {"type": "string"},
                "cv_id": {"type": "string"},
                "company_id": {"type": "string"},
                "projects_selected": {"type": "array", "items": {"type": "string"}},
            }, required=["recipient", "subject", "body", "company", "cv_id"]),
        ]

    @staticmethod
    def _schema(name: str, cls, properties: dict, required: list | None = None):
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required or [],
                },
            },
        }

    # ------------------------------------------------------------------ #
    async def execute(
        self,
        tool_name: str,
        arguments: dict,
    ):
        if isinstance(arguments, str):
            import json as _json
            try:
                arguments = _json.loads(arguments) if arguments.strip() else {}
            except Exception:
                arguments = {}

        if tool_name not in self._TOOL_CLASSES:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self._get_tool(tool_name)

        if asyncio.iscoroutinefunction(tool.run):
            return await tool.run(**arguments)
        return await asyncio.to_thread(tool.run, **arguments)