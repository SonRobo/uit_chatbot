"""
This module defines FastAPI endpoints for chat.
"""
from fastapi import (
    status,
    Depends,
    APIRouter,
    HTTPException,
    Response
)

from src.services.service import Service
from src.api.dependencies.dependency import get_service
from src.api.schemas.chat import (
    RequestChat,
    ResponseChat
)


chat_router = APIRouter(
    tags=["Chat"],
    prefix="/chat",
)


@chat_router.post(
    '/chatDomain',
    status_code=status.HTTP_200_OK,
    response_model=ResponseChat
)
async def chat_domain(
    request_chat: RequestChat,
    service: Service = Depends(get_service)
) -> ResponseChat:
    """
    Endpoint to handle chat queries and retrieve responses from the chat engine.

    Args:
        request_chat (RequestChat): An object containing the chat query.
        service (Service, optional): Dependency injection for the service layer.
                                     Defaults to Depends(get_service).

    Returns:
        ResponseChat: An object containing the chat response and a flag  
                      indicating if the query was out of the expected domain.
    """
    if not request_chat.query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is required"
        )

    try:
        result = await service.retrieve_chat_engine.preprocess_query(
            query=request_chat.query,
            room_id=request_chat.room_id
        )
        await service.chat_repository.add_chat_domains(
            room_id=request_chat.room_id,
            query=request_chat.query,
            answer=result.response,
            retrieved_nodes=result.retrieved_nodes,
            is_out_of_domain=result.is_outdomain
        )

        return ResponseChat(
            response=result.response,
            is_outdomain=result.is_outdomain
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e


@chat_router.delete(
    "/deleteChat",
    status_code=status.HTTP_200_OK
)
async def history_chat_deletion(
    room_id: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    Delete all chat history records for a specific room ID.

    Args:
        room_id (str): The unique identifier of the chat room.
        service (Service): Dependency-injected service for accessing chat repository.

    Returns:
        Response: HTTP response indicating the result of the deletion.

    Raises:
        HTTPException: If room ID is missing, not found, or if an error occurs during deletion.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )

    try:
        records = await service.chat_repository.get_room_chat(
            room_id=room_id
        )
        if not records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room ID not found"
            )

        await service.chat_repository.delete_room_chat(
            room_id=room_id
        )

        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Deleted room chat successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
