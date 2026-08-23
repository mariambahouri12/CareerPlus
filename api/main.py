import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from services.assistant_service import AssistantService
from tools.search_jobs_tool import SearchJobsTool
from tools.send_email_tool import SendEmailTool


@asynccontextmanager
async def lifespan(app: FastAPI):

    model = os.getenv(
        "OLLAMA_MODEL",
        "qwen3:8b",
    )

    ollama_host = os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434",
    )

    print("Starting CareerPlus API...")
    print(f"LLM model: {model}")
    print(f"Ollama host: {ollama_host}")

    # --------------------------------------------------
    # Shared Assistant Service
    # --------------------------------------------------

    app.state.assistant_service = AssistantService(
        model=model,
        ollama_host=ollama_host,
    )

    # --------------------------------------------------
    # Shared Job Search Tool
    #
    # Created ONLY ONCE.
    #
    # This loads:
    # - BGE-M3
    # - FAISS
    # - BM25
    # - CrossEncoder
    # --------------------------------------------------

    print("Loading SearchJobsTool...")

    app.state.search_jobs_tool = SearchJobsTool()

    print("SearchJobsTool ready.")

    print("Loading SendEmailTool...")

    app.state.send_email_tool = SendEmailTool()

    print("SendEmailTool ready.")

    yield

    print("Stopping CareerPlus API...")


app = FastAPI(
    title="CareerPlus API",
    description=(
        "Backend API for the CareerPlus AI job search agent."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501",
).split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
async def root():

    return {
        "service": "CareerPlus API",
        "status": "running",
    }