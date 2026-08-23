import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request

from api.dependencies import get_assistant_service
from api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    JobSearchRequest,
    JobSearchResponse,
    SendEmailRequest,
    SendEmailResponse,
)
from services.assistant_service import AssistantService


router = APIRouter(
    prefix="/api/v1",
)


# ==========================================================
# HEALTH
# ==========================================================

@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health(
    assistant: AssistantService = Depends(
        get_assistant_service
    ),
):
    return HealthResponse(
        status="ok",
        service="CareerPlus API",
        model=assistant.model,
    )


# ==========================================================
# CHAT
# ==========================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    assistant: AssistantService = Depends(
        get_assistant_service
    ),
):
    try:

        return await assistant.chat(
            message=request.message,
            history=request.history,
            include_trace=request.include_trace,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}",
        ) from exc


# ==========================================================
# SEARCH JOBS
# ==========================================================

@router.post(
    "/search-jobs",
    response_model=JobSearchResponse,
)
async def search_jobs(
    request: JobSearchRequest,
    http_request: Request,
):
    try:

        # Reuse the single SearchJobsTool instance
        # created during application startup.
        tool = (
            http_request
            .app
            .state
            .search_jobs_tool
        )

        return tool.run(
            query=request.query,
            top_k=request.top_k,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Job search failed: {exc}",
        ) from exc


# ==========================================================
# SEND EMAIL
# ==========================================================

@router.post(
    "/send-email",
    response_model=SendEmailResponse,
)
async def send_email(
    request: SendEmailRequest,
    http_request: Request,
):
    try:

        # Reuse the single SendEmailTool instance
        # created during application startup.
        tool = (
            http_request
            .app
            .state
            .send_email_tool
        )

        result = await asyncio.to_thread(
            tool.send,
            recipient=request.recipient,
            subject=request.subject,
            body=request.body,
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {exc}",
        ) from exc