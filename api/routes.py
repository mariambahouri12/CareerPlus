import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request

from api.dependencies import get_assistant_service
from api.schemas import (
    ChatRequest,
    ChatResponse,
    CompanySearchRequest,
    CompanySearchResponse,
    HealthResponse,
    PrepareApplicationRequest,
    PrepareApplicationResponse,
    SendEmailRequest,
    SendEmailResponse,
)
from domain.value_objects.company_filter import CompanyFilter
from services.assistant_service import AssistantService

router = APIRouter(prefix="/api/v1")


# ==========================================================
# HEALTH
# ==========================================================
@router.get("/health", response_model=HealthResponse)
async def health(assistant: AssistantService = Depends(get_assistant_service)):
    return HealthResponse(status="ok", service="CareerPlus API", model=assistant.model)


# ==========================================================
# CHAT
# ==========================================================
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    assistant: AssistantService = Depends(get_assistant_service),
):
    try:
        return await assistant.chat(
            message=request.message,
            history=request.history,
            include_trace=request.include_trace,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc


# ==========================================================
# COMPANY SEARCH (deterministic)
# ==========================================================
@router.post("/companies/search", response_model=CompanySearchResponse)
async def companies_search(request: CompanySearchRequest, http_request: Request):
    repo = http_request.app.state.companies_repo
    f = CompanyFilter(
        country=request.country,
        size_max=request.size_max,
        size_min=request.size_min,
        founded_after=request.founded_after,
        founded_before=request.founded_before,
        domain_contains=request.domain_contains,
        name_contains=request.name_contains,
        keywords=request.keywords,
    )
    results = [c.to_dict() for c in (repo.filter(f) if not f.is_empty() else repo.all())]
    return CompanySearchResponse(matches_found=len(results), results=results)


# ==========================================================
# PREPARE APPLICATION
# ==========================================================
@router.post("/applications/prepare", response_model=PrepareApplicationResponse)
async def prepare_application(request: PrepareApplicationRequest, http_request: Request):
    from application.prepare_application import PrepareApplicationUseCase

    use_case = PrepareApplicationUseCase(
        companies=http_request.app.state.companies_repo,
        projects=http_request.app.state.projects_repo,
        cvs=http_request.app.state.cvs_repo,
        llm=http_request.app.state.llm,
    )
    result = use_case.run(company_name=request.company_name, recipient=request.recipient)
    if result["status"] != "prepared":
        raise HTTPException(status_code=400, detail=result.get("message", "Preparation failed."))
    return PrepareApplicationResponse(**result)


# ==========================================================
# SEND APPLICATION
# ==========================================================
@router.post("/applications/send", response_model=SendEmailResponse)
async def send_application(request: SendEmailRequest, http_request: Request):
    from application.send_application import SendApplicationUseCase

    use_case = SendApplicationUseCase(
        email_sender=http_request.app.state.email_sender,
        applications=http_request.app.state.applications_repo,
    )
    result = await asyncio.to_thread(
        use_case.run,
        company=request.company,
        contact=request.recipient,
        subject=request.subject,
        body=request.body,
        cv_id=request.cv_id,
        company_id=request.company_id,
        projects_selected=request.projects_selected,
    )
    return SendEmailResponse(
        status=result["status"],
        message=result["message"],
        message_id=result.get("message_id"),
        recipient=result["recipient"],
    )