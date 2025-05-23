"""
This schemas is used for file
"""

from typing import List
from pydantic import BaseModel


class FileUpload(BaseModel):
    """
    Represents a file upload with its URL, type, and name.
    """
    public_id: str
    url: str
    file_type: str
    file_name: str


class FileUploadRequest(BaseModel):
    """
    Represents a list of file uploads.
    """
    data: List[FileUpload]


class FileUploadResponse(BaseModel):
    """
    Represents a response message for a file upload operation.
    """
    message: str


class File(BaseModel):
    """
    A Pydantic model representing a file with key attributes.

    Attributes:
        Id (str): A unique identifier for the file.
        name (str): The name of the file.
        file_type (str): The type or extension of the file (e.g., 'pdf', 'txt').
        time (str): A timestamp indicating when the file was created, modified, or accessed.
    """
    public_id: str
    url: str
    file_name: str
    file_type: str
    file_path: str
    time: str


class AllFiles(BaseModel):
    """
    A Pydantic model representing a list of files with key attributes.

    Attributes:
        data (List[File]): A list of File objects representing the files.
    """
    data: List[File]
