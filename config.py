from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

USER_DATA_DIR = BASE_DIR / "linkedin_browser"

SCRAPE_PAGE_DELAY = 1500

MAX_JOBS_TO_SCRAPE = 0