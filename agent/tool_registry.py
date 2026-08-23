import asyncio
from typing import Any, Dict

from tools.scraper_tool import LinkedInScraper
from tools.search_jobs_tool import SearchJobsTool
from tools.send_email_tool import SendEmailTool

from rag.job_indexer import JobIndexer


class ToolRegistry:
    """
    Register and execute available CareerPlus tools.
    """

    def __init__(self):
        self.scraper = LinkedInScraper()
        self.indexer = JobIndexer()
        self.search_tool = SearchJobsTool()
        self.email_tool = SendEmailTool()

    # ==========================================================
    # TOOL SCHEMAS
    # ==========================================================

    def schemas(self) -> list[Dict[str, Any]]:
        """
        Return tool schemas exposed to the LLM.
        """

        return [

            # ==================================================
            # 1. SCRAPE JOBS
            # ==================================================

            {
                "type": "function",
                "function": {
                    "name": "scrape_jobs",
                    "description": """
Scrape new job offers from LinkedIn.

Use this tool when the user  wants
new job offers to be discovered on LinkedIn.

The scraped offers are automatically indexed
for later semantic search.
""",
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
            # 2. SEARCH JOBS
            # ==================================================

            {
                "type": "function",
                "function": {
                    "name": "search_jobs",
                    "description": self.search_tool.description,
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
                        },
                        "required": [
                            "query"
                        ],
                    },
                },
            },

            # ==================================================
            # 3. SEND EMAIL
            # ==================================================

            {
                "type": "function",
                "function": {
                    "name": "send_email",

                    "description": """
Send an application email using the user's Gmail account.

Use this tool when the user asks to send
an application email.

The email is sent first. If the email is successfully
sent, the application is automatically recorded.

company:
Name of the company receiving the application.

spontaneous:
True if this is a spontaneous application.
False if this is an application to a specific job offer.
""",

                    "parameters": {
                        "type": "object",

                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": (
                                    "Email address of the recipient."
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
                                    "Name of the company receiving "
                                    "the application."
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
    ):
        """
        Execute the selected tool.
        """

        # ======================================================
        # 1. SCRAPE JOBS
        # ======================================================

        if tool_name == "scrape_jobs":

            jobs = await self.scraper.scrape_jobs(
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
                "status": "success",
                "message": (
                    f"{len(jobs)} job offers were "
                    "scraped and indexed successfully."
                ),
                "jobs_count": len(jobs),
            }

        # ======================================================
        # 2. SEARCH JOBS
        # ======================================================

        if tool_name == "search_jobs":

            results = await asyncio.to_thread(
                self.search_tool.run,
                query=arguments["query"],
                top_k=arguments.get(
                    "top_k",
                    5,
                ),
            )

            return {
                "status": "success",
                "matches_found": len(results),
                "results": results,
            }

        # ======================================================
        # 3. SEND EMAIL
        # ======================================================

        if tool_name == "send_email":

            result = await asyncio.to_thread(
                self.email_tool.send,

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