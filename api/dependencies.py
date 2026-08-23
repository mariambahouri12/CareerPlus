from fastapi import Request

from services.assistant_service import AssistantService


def get_assistant_service(
    request: Request,
) -> AssistantService:
    """
    Retrieve the single shared AssistantService instance.
    """

    return request.app.state.assistant_service