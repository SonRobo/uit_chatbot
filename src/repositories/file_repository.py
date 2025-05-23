"""
This module provides a `FileRepository` class to manage file records in a data storage system.
"""

import os
from typing import List
import requests
from dotenv import load_dotenv

from src.storage.file_crud import CRUDFileCollection
from src.models.file import (
    File,
    FileUpload
)
from src.utils.utility import (
    get_datetime,
    convert_value
)

load_dotenv()

TIME_OUT = convert_value(os.getenv('TIME_OUT'))
DIRECTORY = convert_value(os.getenv('DIRECTORY'))


class FileRepository:
    """
    A repository class for managing file records in a data storage system.
    """

    def __init__(
        self,
        time_out: int = TIME_OUT,
        directory: str = DIRECTORY
    ):
        """
        Initializes the FileRepository instance.
        """
        self.time_out = time_out
        self.directory = directory
        self.collection = CRUDFileCollection()
        self.data = self.load_all_data()

    def load_all_data(self):
        """
        Load all documents from the collection.

        Args:
            None

        Returns:
            list: A list of documents with '_id' field as a string.
        """
        self.data = list(self.collection.find_all_doc())

        for doc in self.data:
            doc["_id"] = str(doc["_id"])

        return self.data

    async def add_one_record(
        self,
        file: File = None
    ) -> None:
        """
        Insert a single file record into the collection.

        Args:
            file (File): A `File` instance containing the data to be inserted.
        """
        self.collection.insert_one_doc(file.__dict__)

    async def add_file(
        self,
        public_id: str = None,
        url: str = None,
        file_name: str = None,
        file_type: str = None,
        file_path: str = None
    ) -> None:
        """
        Create and add a new file record to the collection.

        Args:
            url (str, optional): The URL associated with the file.
            name (str, optional): The name of the file.
            file_type (str, optional): The type or format of the file (e.g., "pdf", "txt").
        """
        timestamp = get_datetime()

        file_instance = File(
            public_id=public_id,
            url=url,
            file_name=file_name,
            file_type=file_type,
            file_path=file_path,
            time=timestamp
        )

        await self.add_one_record(
            file=file_instance
        )

    async def file_transfer(
        self,
        data: FileUpload
    ) -> str:
        """
        Transfers a file from a given URL to a local directory.
        Args:
            data (FileUpload): An object containing the file"s URL, type, and name.
        Returns:
            str: The local file path where the file is saved or the URL 
                 itself if the file type is "link".
        """
        file_path = None

        if not data.file_type == "link":
            os.makedirs(
                self.directory,
                exist_ok=True
            )
            file_path = os.path.join(
                self.directory,
                data.file_name
            )
            response = requests.get(
                data.url,
                timeout=self.time_out
            )
            response.raise_for_status()
            with open(file_path, "wb") as file:
                file.write(response.content)
            return file_path

        file_path = data.url

        return file_path

    def delete_specific_file(
        self,
        public_id: str = None
    ) -> None:
        """
        Deletes a document with the specified file name from the collection.
        Args:
            file_name (str, optional): The name of the file to be deleted.
                If None, no document will be deleted.
        Raises:
            Exception: If an error occurs during the deletion process.
        Returns:
            None: This method returns nothing, but prints a message indicating
            the result of the deletion operation.
        """
        try:
            result = self.collection.delete_one_doc(
                {"public_id": public_id}
            )

            if result.deleted_count > 0:
                print(
                    f"Document with public_id = {public_id} deleted successfully."
                )
            else:
                print(f"No document with public_id = {public_id} found.")
        except Exception as e:
            print(f"Error deleting document with public_id = {public_id}: {e}")
            raise

    def get_specific_file(
        self,
        public_id: str = None
    ) -> List:
        """
        Retrieves a document from the collection based on the specified file name.
        Args:
            file_name (str, optional): The name of the file to retrieve.
        Returns:
            Optional[dict]: A dictionary representing the document
        """
        document = self.collection.find_one_doc(
            {
                "public_id": public_id
            }
        )
        if document:
            document["_id"] = str(document["_id"])

        return document
