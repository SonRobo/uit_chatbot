"""
This module defines FastAPI endpoints for suggestion.
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
from src.api.schemas.suggestion import (
    ResponseSuggestion,
    ResponseSuggestionList,
    Suggestion
)

suggestion_router = APIRouter(
    tags=["Suggestion"],
    prefix="/suggestion",
)


@suggestion_router.get(
    "/getAllSuggestion",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuggestionList
)
async def get_all_suggestion(
    service: Service = Depends(get_service)
) -> ResponseSuggestionList:
    """
    Retrieve all suggestions.

    Args:
        service: Service - A dependency that provides access to the suggestion repository.

    Returns:
        ResponseSuggestionList: A list of all suggestions.

    Raises:
        HTTPException: If an internal server error occurs, a 500 status code is returned.
    """
    try:
        suggestion_records = service.suggestion_repository.load_data()

        if not suggestion_records:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="No suggestion not found"
            )

        return ResponseSuggestionList(
            suggestion=[ResponseSuggestion(**record)
                        for record in suggestion_records]
        )

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@suggestion_router.get(
    "/getSuggestion",
    status_code=status.HTTP_200_OK
)
async def get_suggestion(
    suggestion_question: str,
    service: Service = Depends(get_service)
) -> Suggestion:
    """
    This endpoint retrieves a single suggestion based on the provided question.

    Args:
        suggestion_question: str - The question to find a suggestion for.
        service: Service - A dependency that provides access to the suggestion repository.

    Returns:
        Suggestion: The suggestion associated with the provided question.

    Raises:
        404 status code if the suggestion is not found.
        500 status code if an internal server error occurs.
    """
    try:
        suggestion_record = service.suggestion_repository.get_suggestion_by_question(
            suggestion_question=suggestion_question
        )

        if not suggestion_record:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )

        return Suggestion(**suggestion_record)

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@suggestion_router.post(
    "/suggestionUpload",
    status_code=status.HTTP_200_OK
)
async def upload_suggestion(
    question: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    This endpoint processes a question using a chat engine to generate an answer

    Args:
        question: str - The question for which a suggestion will be generated.
        service: Service - A dependency that provides access to the 
                           chat engine and suggestion repository.

    Returns:
        Response: A response indicating successful addition of the suggestion.

    Raises:
        HTTPException: If an internal server error occurs, a 500 status code is returned.
    """
    try:
        response = await service.chat_engine.funny_chat(
            query=question
        )
        node = await service.vector_database.suggestion_config(
            question=question,
            answer=response
        )
        await service.vector_database.insert_suggestion_nodes(
            nodes=node
        )
        service.suggestion_repository.add_suggestion(
            question=question,
            answer=response
        )

        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Adding suggestion successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e


@suggestion_router.delete(
    "/deleteSuggestion",
    status_code=status.HTTP_200_OK
)
async def delete_suggestion(
    field: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    This endpoint deletes a suggestion from the database based on the provided field

    Args:
        field: str The unique identifier for the suggestion

    Returns:
        Response An HTTP response indicating the outcome of the deletion operation.

    Raises:
        400 Bad Request: If the 'field' parameter is missing.
        500 Internal Server Error: If an unexpected error occurs during the deletion process.
    """
    if not field:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field is required"
        )

    try:
        service.suggestion_repository.delete_suggestion(
            identifier=field
        )

        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Delete suggestion successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e
