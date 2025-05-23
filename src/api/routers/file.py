"""
This module defines FastAPI endpoints for file.
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
from src.api.schemas.file import (
    FileUploadRequest,
    AllFiles,
    File
)


file_router = APIRouter(
    tags=["File"],
    prefix="/file",
)


@file_router.get(
    "/getAllFilesUpload",
    status_code=status.HTTP_200_OK,
    response_model=AllFiles
)
async def get_all_files_upload(
    service: Service = Depends(get_service)
) -> AllFiles:
    """
    Retrieve all files in the file repository.

    Args:
        service: The service used for accessing the file repository.

    Returns:
        AllFiles: A list of all files in the file repository.
    """
    try:
        file_records = service.file_repository.load_all_data()

        return AllFiles(
            data=[File(**record) for record in file_records]
        )

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@file_router.get(
    "/getFileUpload",
    status_code=status.HTTP_200_OK,
    response_model=File
)
async def get_file_upload(
    public_id: str,
    service: Service = Depends(get_service)
) -> File:
    """
    Endpoint to retrieve a specific file's details.

    Args:
        file_name (str): The name of the file to retrieve.
        service (Service): The service used for accessing the file repository.

    Raises:
        HTTPException: If the file is not found or an error occurs during retrieval.

    Returns:
        File: The details of the requested file if found.
    """
    try:
        file_record = service.file_repository.get_specific_file(
            public_id=public_id
        )

        if not file_record:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        return File(**file_record)

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@file_router.post(
    "/fileUpload",
    status_code=status.HTTP_200_OK
)
async def file_upload(
    request_file: FileUploadRequest,
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
    if not request_file.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data is required"
        )

    try:
        await service.file_management.add_file_router(
            data_list=request_file.data
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


@file_router.delete(
    "/fileDelete",
    status_code=status.HTTP_200_OK
)
async def file_delete(
    public_id: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    Endpoint to handle file deletion.

    Args:
        file_name (str): The name of the file to be deleted.
        service (Service): The service used for file management and repository access.

    Raises:
        HTTPException: If the file is not found or an error occurs during deletion.

    Returns:
        Response: Success message if the file is deleted successfully.
    """
    try:
        record = service.file_repository.get_specific_file(
            public_id=public_id
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not found"
            )

        service.file_management.delete_file(
            public_id=public_id
        )

        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Deleted file successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
