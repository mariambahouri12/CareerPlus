"""
LinkedIn Playwright scraper — reused from CareerPlus v1 with minor
adaptations (imports, config paths, port implementation).
"""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List

from playwright.async_api import async_playwright, Page, BrowserContext

import config
from domain.ports.linkedin_scraper import LinkedInScraperPort

logger = logging.getLogger(__name__)


class LinkedInScraper(LinkedInScraperPort):
    name = "scrape_linkedin"

    description = (
        "Scrape new job offers from LinkedIn for a given job title, "
        "optionally filtered by one or more company names. Use when "
        "the user wants to know about recent job openings at a company."
    )

    def __init__(self) -> None:
        self.user_data_dir = config.USER_DATA_DIR
        self.page_delay = config.SCRAPE_PAGE_DELAY
        self.max_jobs = config.MAX_JOBS_TO_SCRAPE
        self.data_dir: Path = config.DATA_DIR

    # ---------------------------------------------------------------- #
    async def scrape_jobs(
        self,
        job_title: str,
        company_names: List[str] | None = None,
    ) -> List[Dict]:
        company_names = [c for c in (company_names or []) if c]
        logger.info("Scrape: job=%r companies=%s", job_title, company_names)

        async with async_playwright() as p:
            ctx = await self._launch_browser(p)
            page = await ctx.new_page()
            await page.set_extra_http_headers({"Accept-Language": "fr-FR,fr;q=0.9"})
            ctx.on("page", lambda popup: asyncio.create_task(popup.close()))

            await self._navigate_to_linkedin(page)
            await self._wait_for_login()
            await self._go_to_jobs_section(page)
            await self._fill_search_bar(page, job_title)

            if company_names:
                await self._open_company_filter(page)
                for name in company_names:
                    await self._type_and_select_company(page, name)
                await self._apply_filters(page)

            await self._wait_for_results_visible()
            job_ids = await self._collect_all_job_ids(page)
            logger.info("%d unique job IDs collected", len(job_ids))

            if not job_ids:
                await ctx.close()
                return []

            jobs = await self._extract_jobs(page, job_ids)
            await ctx.close()
            if jobs:
                self._save(jobs)
            return jobs

    # ---------------------------------------------------------------- #
    async def _launch_browser(self, playwright) -> BrowserContext:
        return await playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=False,
            args=["--start-maximized"],
            locale="fr-FR",
            timezone_id="Europe/Paris",
        )

    async def _navigate_to_linkedin(self, page: Page) -> None:
        await page.goto("https://www.linkedin.com/?lang=fr_FR")
        await page.wait_for_timeout(2000)

    @staticmethod
    async def _wait_for_login() -> None:
        print("\n" + "=" * 70)
        print("⚠️  Please make sure you are logged in to LinkedIn.")
        print("=" * 70)
        input("→ Press [ENTER] when you are logged in…")

    @staticmethod
    async def _wait_for_results_visible() -> None:
        print("\n" + "=" * 70)
        print("👁  The filtered job list should be visible in the left column.")
        print("=" * 70)
        input("→ Press [ENTER] when the jobs are visible…")

    async def _go_to_jobs_section(self, page: Page) -> None:
        for sel in [
            "a[aria-label*='Emplois']",
            "a[aria-label*='Jobs']",
            "a[href*='/jobs/']",
        ]:
            try:
                el = page.locator(sel).first
                if await el.count() and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(2000)
                    return
            except Exception:
                pass
        await page.goto("https://www.linkedin.com/jobs/")
        await page.wait_for_timeout(2000)

    async def _fill_search_bar(self, page: Page, job_title: str) -> None:
        await page.wait_for_timeout(1500)
        for sel in [
            "input[placeholder*='Décrivez l']",
            "input[placeholder*='Search by title']",
            "input[aria-label*='Rechercher']",
            "input.jobs-search-box__text-input",
        ]:
            try:
                el = page.locator(sel).first
                if await el.count() and await el.is_visible():
                    await el.click()
                    await el.fill("")
                    await el.type(job_title, delay=80)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(3000)
                    return
            except Exception:
                pass
        await page.goto(
            f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}"
        )
        await page.wait_for_timeout(2000)

    async def _open_company_filter(self, page: Page) -> None:
        for sel in [
            "div[aria-label*='Filtrer par Entreprise']",
            "div[aria-label*='Entreprise']",
            "label:has-text('Entreprise')",
        ]:
            try:
                el = page.locator(sel).first
                if await el.count() and await el.is_visible():
                    await el.scroll_into_view_if_needed()
                    await el.click()
                    await page.wait_for_timeout(1500)
                    return
            except Exception:
                pass

    async def _type_and_select_company(self, page: Page, company_name: str) -> None:
        await page.wait_for_timeout(1000)
        field = None
        for sel in [
            "input[placeholder*='Ajouter une entreprise']",
            "input[placeholder*='Add a company']",
            "input[role='combobox']",
        ]:
            try:
                el = page.locator(sel).first
                if await el.count() and await el.is_visible():
                    field = el
                    break
            except Exception:
                pass

        if not field:
            return

        await field.click()
        await field.fill("")
        await field.type(company_name, delay=80)
        await page.wait_for_timeout(2000)

        for sel in [
            f"label:has-text('{company_name}')",
            "div[role='option']:first-child",
            "li[role='option']:first-child",
        ]:
            try:
                opt = page.locator(sel).first
                if await opt.count() and await opt.is_visible():
                    await opt.click()
                    await page.wait_for_timeout(800)
                    return
            except Exception:
                pass

        await page.keyboard.press("Enter")
        await page.wait_for_timeout(800)

    async def _apply_filters(self, page: Page) -> None:
        await page.wait_for_timeout(800)
        for sel in [
            "span:has-text('Afficher les résultats')",
            "button:has-text('Afficher les résultats')",
        ]:
            try:
                els = page.locator(sel)
                for i in range(await els.count()):
                    el = els.nth(i)
                    if await el.is_visible():
                        await el.scroll_into_view_if_needed()
                        await el.click()
                        await page.wait_for_timeout(3000)
                        return
            except Exception:
                pass

    _COLLECT_JS = """
    () => {
        const ids = new Set();
        for (const el of document.querySelectorAll('[componentkey]')) {
            const key = el.getAttribute('componentkey');
            if (key && key.startsWith('job-card-component-ref-')) {
                const id = key.replace('job-card-component-ref-', '');
                if (/^\\d+$/.test(id)) ids.add(id);
            }
        }
        if (ids.size === 0) {
            for (const a of document.querySelectorAll('a[href*="/jobs/view/"]')) {
                const m = a.href.match(/\\/jobs\\/view\\/(\\d+)/);
                if (m) ids.add(m[1]);
            }
        }
        return [...ids];
    }
    """

    async def _collect_all_job_ids(self, page: Page) -> List[str]:
        seen: set[str] = set()
        stall = 0
        while stall < 3:
            ids: List[str] = await page.evaluate(self._COLLECT_JS)
            new = set(ids) - seen
            seen.update(new)
            stall = 0 if new else stall + 1
            if self.max_jobs and len(seen) >= self.max_jobs:
                break
            await page.evaluate("""
                () => {
                    const panel = document.querySelector('.jobs-search-results-list')
                        || document.querySelector('.scaffold-layout__list');
                    if (panel) panel.scrollBy(0, 800);
                    else window.scrollBy(0, 800);
                }
            """)
            await page.wait_for_timeout(1200)
        lst = list(seen)
        return lst[:self.max_jobs] if self.max_jobs else lst

    _EXTRACT_JS = """
    () => {
        const btn = document.querySelector('[data-testid="expandable-text-button"]');
        if (btn) { btn.removeAttribute('aria-hidden'); btn.click(); }
        const first = (sels) => {
            for (const s of sels) {
                const el = document.querySelector(s);
                if (el && el.innerText.trim()) return el.innerText.trim();
            }
            return '';
        };
        return {
            title: first(['h1.t-24', 'h1',
                '.job-details-jobs-unified-top-card__job-title',
                '.jobs-unified-top-card__job-title']),
            company: first([
                '.job-details-jobs-unified-top-card__company-name a',
                '.job-details-jobs-unified-top-card__company-name',
                '.jobs-unified-top-card__company-name a',
                '.jobs-unified-top-card__company-name']),
            location: first([
                '.job-details-jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__workplace-type']),
            description: first([
                '[data-testid="expandable-text-box"]',
                '#job-details',
                '.jobs-description__content',
                '.jobs-box__html-content',
                '.jobs-description']),
        };
    }
    """

    async def _extract_jobs(self, page: Page, job_ids: List[str]) -> List[Dict]:
        results = []
        total = len(job_ids)
        for i, job_id in enumerate(job_ids, 1):
            print(f"[{i}/{total}] Extracting job ID={job_id}…", end=" ", flush=True)
            try:
                await page.goto(
                    f"https://www.linkedin.com/jobs/view/{job_id}/",
                    wait_until="domcontentloaded",
                )
                await page.wait_for_timeout(self.page_delay)
                data = await page.evaluate(self._EXTRACT_JS)
                if data["description"] and len(data["description"]) < 200:
                    await page.wait_for_timeout(800)
                if data["description"] and len(data["description"]) > 100:
                    results.append({
                        "id": i,
                        "job_id": job_id,
                        "url": f"https://www.linkedin.com/jobs/view/{job_id}/",
                        "title": data["title"] or f"Job #{i}",
                        "company": data["company"],
                        "location": data["location"],
                        "description": data["description"],
                    })
                    print(f"✔  {data['title'][:55]!r}")
                else:
                    print("✗  description empty – skipped")
            except Exception as exc:
                print(f"✗  error: {exc}")
        return results

    def _save(self, jobs: List[Dict]) -> None:
        json_path = self.data_dir / "offres_extraites.json"
        txt_path = self.data_dir / "offres_extraites.txt"
        try:
            with open(json_path, "w", encoding="utf-8-sig") as f:
                json.dump(jobs, f, ensure_ascii=False, indent=4)
        except Exception as exc:
            logger.error("JSON save failed: %s", exc)
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                for job in jobs:
                    f.write("=" * 70 + "\n")
                    f.write(f"JOB #{job['id']}  |  ID: {job['job_id']}\n")
                    f.write(f"Title   : {job['title']}\n")
                    f.write(f"Company : {job.get('company', 'N/A')}\n")
                    f.write(f"Location: {job.get('location', 'N/A')}\n")
                    f.write(f"URL     : {job.get('url', 'N/A')}\n")
                    f.write("-" * 70 + "\n")
                    f.write(job["description"] + "\n\n")
        except Exception as exc:
            logger.error("TXT save failed: %s", exc)