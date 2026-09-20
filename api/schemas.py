from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(..., min_length=1, max_length=10_000)
    history: List[ChatMessage] = Field(default_factory=list)
    include_trace: bool = True


class ToolCallTrace(BaseModel):
    step: int
    tool: str
    arguments: Dict[str, Any]


class ChatResponse(BaseModel):
    response: str
    tool_calls: List[ToolCallTrace] = Field(default_factory=list)
    steps: int
    success: bool = True


class HealthResponse(BaseModel):
    status: str
    service: str
    model: str


class CompanySearchRequest(BaseModel):
    country: Optional[str] = None
    size_max: Optional[int] = None
    size_min: Optional[int] = None
    founded_after: Optional[int] = None
    founded_before: Optional[int] = None
    domain_contains: Optional[str] = None
    name_contains: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class CompanySearchResponse(BaseModel):
    matches_found: int
    results: List[Dict[str, Any]]


class PrepareApplicationRequest(BaseModel):
    company_name: str
    recipient: Optional[str] = None


class PrepareApplicationResponse(BaseModel):
    status: str
    company: Dict[str, Any]
    recipient: str
    cv_id: str
    cv_label: str = ""
    projects_selected: List[str] = Field(default_factory=list)
    projects_names: List[str] = Field(default_factory=list)
    subject: str
    body: str


class SendEmailRequest(BaseModel):
    recipient: str = Field(..., min_length=3)
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=20_000)
    company: str
    cv_id: str
    company_id: Optional[str] = None
    projects_selected: List[str] = Field(default_factory=list)


class SendEmailResponse(BaseModel):
    status: str
    message: str
    message_id: Optional[str] = None
    recipient: str