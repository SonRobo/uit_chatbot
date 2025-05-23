"""
This module defines FastAPI endpoints for file.
"""
from typing import List
from fastapi import (
    status,
    Depends,
    APIRouter,
    HTTPException,
    Response
)

from src.services.service import Service
from src.api.dependencies.dependency import get_service


manually_file_router = APIRouter(
    tags=["Manually"],
    prefix="/manual",
)


@manually_file_router.post(
    "/fileUpload",
    status_code=status.HTTP_200_OK
)
async def file_upload(
    request_file: List[str],
    service: Service = Depends(get_service)
) -> Response:
    """
    Endpoint to handle file uploads.

    Args:
        request_file (FileUploadRequest): The uploaded file data.
        service (Service): The service used for file management.

    Raises:
        HTTPException: If request data is missing or an error occurs.

    Returns:
        dict: Success message if the file is uploaded successfully.
    """
    if not request_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data is required"
        )

    try:
        await service.file_management.add_file_by_chunking(
            data_list=request_file
        )

        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Adding file successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
