from fastapi import Request

from services.assistant_service import AssistantService


def get_assistant_service(request: Request) -> AssistantService:
    return request.app.state.assistant_service