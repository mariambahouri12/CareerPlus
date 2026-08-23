import asyncio
from typing import Any, Dict, Optional

from tools.scraper_tool import LinkedInScraper
from tools.search_jobs_tool import SearchJobsTool
from tools.send_email_tool import SendEmailTool
from tools.get_cv_tool import GetCVTool

from rag.job_indexer import JobIndexer


class ToolRegistry:
    """
    Register and execute available CareerPlus tools.

    This class is a pure aggregator: it exposes tool schemas
    to the LLM and dispatches execution. It holds no business
    logic and no descriptions — each tool describes itself.

    Tool instances are created lazily, on first execution,
    to avoid paying startup costs (Gmail auth, FAISS loading…)
    for tools the user never actually triggers in a session.
    """

    _TOOL_CLASSES = {
        "scrape_jobs": LinkedInScraper,
        "get_cv": GetCVTool,
        "search_jobs": SearchJobsTool,
        "send_email": SendEmailTool,
    }

    def __init__(self):

        self._instances: Dict[str, Any] = {}

        self.indexer = JobIndexer()

    # ==========================================================
    # LAZY TOOL INSTANTIATION
    # ==========================================================

    def _get_tool(self, tool_name: str):
        """
        Return the cached instance of a tool, creating it on
        first use.
        """

        if tool_name not in self._instances:

            tool_class = self._TOOL_CLASSES[tool_name]

            self._instances[tool_name] = tool_class()

        return self._instances[tool_name]

    # ==========================================================
    # TOOL SCHEMAS
    # ==========================================================

    def schemas(self) -> list[Dict[str, Any]]:
        """
        Return tool schemas exposed to the LLM.

        Descriptions are read directly from each tool CLASS
        (not an instance) — no instantiation needed just to
        list the available tools.
        """

        return [

            # ==================================================
            # 1. SCRAPE JOBS
            # ==================================================

            {
                "type": "function",

                "function": {

                    "name": "scrape_jobs",

                    "description": LinkedInScraper.description,

                    "parameters": {

                        "type": "object",

                        "properties": {

                            "job_title": {
                                "type": "string",
                                "description": (
                                    "Job title or keywords "
                                    "to search on LinkedIn."
                                ),
                            },

                            "company_names": {
                                "type": "array",

                                "items": {
                                    "type": "string"
                                },

                                "description": (
                                    "Optional list of company "
                                    "names to filter."
                                ),
                            },
                        },

                        "required": [
                            "job_title"
                        ],
                    },
                },
            },

            # ==================================================
            # 2. GET CV
            # ==================================================

            {
                "type": "function",

                "function": {

                    "name": "get_cv",

                    "description": GetCVTool.description,

                    "parameters": {

                        "type": "object",

                        "properties": {},

                        "required": [],
                    },
                },
            },

            # ==================================================
            # 3. SEARCH JOBS
            # ==================================================

            {
                "type": "function",

                "function": {

                    "name": "search_jobs",

                    "description": SearchJobsTool.description,

                    "parameters": {

                        "type": "object",

                        "properties": {

                            "query": {
                                "type": "string",

                                "description": (
                                    "Natural language query "
                                    "about indexed job offers."
                                ),
                            },

                            "top_k": {
                                "type": "integer",

                                "minimum": 1,

                                "maximum": 20,

                                "description": (
                                    "Maximum number of "
                                    "offers to return."
                                ),
                            },

                            "use_cv": {
                                "type": "boolean",

                                "description": (
                                    "Whether to include the "
                                    "uploaded CV in the search."
                                ),
                            },
                        },

                        "required": [
                            "query",
                            "use_cv",
                        ],
                    },
                },
            },

            # ==================================================
            # 4. SEND EMAIL
            # ==================================================

            {
                "type": "function",

                "function": {

                    "name": "send_email",

                    "description": SendEmailTool.description,

                    "parameters": {

                        "type": "object",

                        "properties": {

                            "recipient": {
                                "type": "string",

                                "description": (
                                    "Email address of "
                                    "the recipient."
                                ),
                            },

                            "subject": {
                                "type": "string",

                                "description": (
                                    "Email subject."
                                ),
                            },

                            "body": {
                                "type": "string",

                                "description": (
                                    "Full email body."
                                ),
                            },

                            "company": {
                                "type": "string",

                                "description": (
                                    "Name of the company "
                                    "receiving the application."
                                ),
                            },

                            "spontaneous": {
                                "type": "boolean",

                                "description": (
                                    "True for a spontaneous "
                                    "application, false otherwise."
                                ),
                            },
                        },

                        "required": [
                            "recipient",
                            "subject",
                            "body",
                            "company",
                            "spontaneous",
                        ],
                    },
                },
            },
        ]

    # ==========================================================
    # EXECUTE TOOLS
    # ==========================================================

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
        cv_text: Optional[str] = None,
    ):
        """
        Execute the selected tool.

        The tool instance is created (or reused from cache) here,
        only when actually needed.

        cv_text is kept outside the LLM tool arguments.
        It comes from the uploaded CV in Streamlit.
        """

        # ======================================================
        # 1. SCRAPE JOBS
        # ======================================================

        if tool_name == "scrape_jobs":

            scraper = self._get_tool("scrape_jobs")

            jobs = await scraper.scrape_jobs(
                job_title=arguments["job_title"],

                company_names=arguments.get(
                    "company_names"
                ),
            )

            if jobs:

                await asyncio.to_thread(
                    self.indexer.index_jobs,
                    jobs,
                )

            return {
                "status": "success" if jobs else "empty",

                "message": (
                    f"{len(jobs)} job offers were "
                    "scraped and indexed successfully."
                    if jobs else
                    "No new job offers were found."
                ),

                "jobs_count": len(jobs),
            }

        # ======================================================
        # 2. GET CV
        # ======================================================

        if tool_name == "get_cv":

            cv_tool = self._get_tool("get_cv")

            return await asyncio.to_thread(
                cv_tool.run,
                cv_text=cv_text,
            )

        # ======================================================
        # 3. SEARCH JOBS
        # ======================================================

        if tool_name == "search_jobs":

            search_tool = self._get_tool("search_jobs")

            results = await asyncio.to_thread(
                search_tool.run,

                query=arguments["query"],

                top_k=arguments.get(
                    "top_k",
                    5,
                ),

                use_cv=arguments.get(
                    "use_cv",
                    False,
                ),

                cv_text=cv_text,
            )

            return results

        # ======================================================
        # 4. SEND EMAIL
        # ======================================================

        if tool_name == "send_email":

            email_tool = self._get_tool("send_email")

            result = await asyncio.to_thread(
                email_tool.send,

                recipient=arguments["recipient"],

                subject=arguments["subject"],

                body=arguments["body"],

                company=arguments["company"],

                spontaneous=arguments["spontaneous"],
            )

            return result

        # ======================================================
        # UNKNOWN TOOL
        # ======================================================

        raise ValueError(
            f"Unknown tool: {tool_name}"
        )