"""Central configuration. Reads .env, exposes paths and DB credentials."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FAISS_DIR = DATA_DIR / "faiss"
FAISS_DIR.mkdir(parents=True, exist_ok=True)

# Local FAISS index (kept local — vectors are heavy and stay on disk)
COMPANIES_INDEX_PATH = FAISS_DIR / "companies.index"
COMPANIES_METADATA_PATH = FAISS_DIR / "companies_metadata.json"

# --- Supabase / Postgres ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")

# --- Scraper ---
USER_DATA_DIR = BASE_DIR / "linkedin_browser"
SCRAPE_PAGE_DELAY = 1500
MAX_JOBS_TO_SCRAPE = 0

# --- LLM ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# --- Embeddings ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

# --- Email ---
GMAIL_CREDENTIALS_PATH = str(BASE_DIR / "credentials.json")
GMAIL_TOKEN_PATH = str(BASE_DIR / "token.json")

# --- Retrieval ---
RERANKER_THRESHOLD = 0.30
RETRIEVAL_K = 20

# --- FastAPI ---
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501",
).split(",")