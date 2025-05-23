"""
This module defines a Pydantic model for representing files with specific attributes.
"""
from pydantic import BaseModel


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


class FileUpload(BaseModel):
    """
    Represents a file upload with its URL, type, and name.
    """
    public_id: str
    url: str
    file_type: str
    file_name: str


class FileMetadata(BaseModel):
    """
    A Pydantic model for storing metadata about a file extracted from a URL.

    Attributes:
        file_name_with_extension (str): The complete file name including the extension.
        file_name (str): The file name without the extension.
        file_extension (str): The file extension, including the leading dot.
    """
    file_name_with_extension: str
    file_name: str
    file_extension: str
