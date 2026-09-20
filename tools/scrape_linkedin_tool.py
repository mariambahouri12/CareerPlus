from tools.base import BaseTool


class ScrapeLinkedInTool(BaseTool):
    name = "scrape_linkedin"
    description = (
        "Scrape recent LinkedIn job postings for a given job title, "
        "optionally restricted to specific companies. Use when the "
        "user asks about recent job openings at a company."
    )

    def __init__(self, scraper, **kwargs):
        self.scraper = scraper

    async def run(self, job_title: str, company_names: list[str] | None = None):
        jobs = await self.scraper.scrape_jobs(
            job_title=job_title,
            company_names=company_names,
        )
        return {
            "status": "success" if jobs else "empty",
            "jobs_count": len(jobs),
            "jobs": jobs,
        }