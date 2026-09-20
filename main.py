import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from api.routes import router
from infrastructure.email.gmail_sender import GmailSender
from infrastructure.retrieval.company_indexer import CompanyIndexer
from infrastructure.retrieval.company_retriever import CompanyRetriever
from infrastructure.scraping.linkedin_scraper import LinkedInScraper
from infrastructure.storage.postgres_application_repository import PostgresApplicationRepository
from infrastructure.storage.postgres_company_repository import PostgresCompanyRepository
from infrastructure.storage.postgres_cv_repository import PostgresCVRepository
from infrastructure.storage.postgres_project_repository import PostgresProjectRepository
from infrastructure.llm.ollama_client import OllamaClient
from services.assistant_service import AssistantService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting CareerPlus API...")

    if not config.SUPABASE_DB_URL:
        raise RuntimeError(
            "SUPABASE_DB_URL is not set. Add it to your .env file."
        )

    # ---------------- Repositories (Postgres / Supabase) ----------------
    companies_repo = PostgresCompanyRepository(config.SUPABASE_DB_URL)
    projects_repo = PostgresProjectRepository(config.SUPABASE_DB_URL)
    cvs_repo = PostgresCVRepository(config.SUPABASE_DB_URL)
    applications_repo = PostgresApplicationRepository(config.SUPABASE_DB_URL)

    # ---------------- Index companies on startup (local FAISS) ----------------
    print("Indexing companies...")
    indexer = CompanyIndexer(
        index_path=str(config.COMPANIES_INDEX_PATH),
        metadata_path=str(config.COMPANIES_METADATA_PATH),
    )
    indexer.index(companies_repo.all())
    print("Companies indexed.")

    # ---------------- Retriever ----------------
    company_retriever = CompanyRetriever(
        index_path=str(config.COMPANIES_INDEX_PATH),
        metadata_path=str(config.COMPANIES_METADATA_PATH),
    )

    # ---------------- Email ----------------
    try:
        email_sender = GmailSender(
            credentials_path=config.GMAIL_CREDENTIALS_PATH,
            token_path=config.GMAIL_TOKEN_PATH,
        )
    except Exception as exc:
        print(f"[WARN] Gmail sender unavailable: {exc}")
        email_sender = None

    # ---------------- Scraper ----------------
    scraper = LinkedInScraper()

    # ---------------- LLM ----------------
    llm = OllamaClient()

    # ---------------- Assistant ----------------
    app.state.assistant_service = AssistantService(
        model=config.OLLAMA_MODEL,
        ollama_host=config.OLLAMA_HOST,
        companies_repo=companies_repo,
        projects_repo=projects_repo,
        cvs_repo=cvs_repo,
        applications_repo=applications_repo,
        email_sender=email_sender,
        scraper=scraper,
        company_retriever=company_retriever,
    )

    app.state.companies_repo = companies_repo
    app.state.projects_repo = projects_repo
    app.state.cvs_repo = cvs_repo
    app.state.applications_repo = applications_repo
    app.state.email_sender = email_sender
    app.state.llm = llm

    print("CareerPlus API ready.")
    yield
    print("Stopping CareerPlus API...")


app = FastAPI(
    title="CareerPlus API",
    description="Agentic AI + RAG company intelligence and application platform.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"service": "CareerPlus API", "status": "running"}