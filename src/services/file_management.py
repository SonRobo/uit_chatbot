"""
This service represents the file management functionality of the application.
"""
import re
from typing import List

from src.data_loader.general_loader import GeneralLoader
from src.repositories.file_repository import FileRepository
from src.storage.weaviatedb import WeaviateDB
from src.models.file import FileUpload


class FileManagement:
    """
    The FileManagement class provides functionalities to manage files
    """

    def __init__(
        self,
        file_repository: FileRepository = None,
        general_loader: GeneralLoader = None,
        vector_database: WeaviateDB = None,
    ):
        self._file_repository = file_repository
        self._general_loader = general_loader
        self._vector_database = vector_database

    async def add_file(
        self,
        data_list: List[FileUpload]
    ) -> None:
        """
        Adds files to the system by transferring them, loading their data,
        and storing them in a vector database.

        Args:
            data_list (List[FileUpload]): A list of FileUpload objects containing file metadata.

        Returns:
            None
        """
        for data in data_list:
            file_path = await self._file_repository.file_transfer(data=data)
            documents = await self._general_loader.aload_data(sources=[file_path])
            print([doc.id_ for doc in documents])

            try:
                await self._vector_database.add_knowledge(
                    url=data.url,
                    file_type=data.file_type,
                    public_id=data.public_id,
                    file_name=data.file_name,
                    documents=documents,
                )
                print("Indexing successfully!!!")
                await self._file_repository.add_file(
                    public_id=data.public_id,
                    url=data.url,
                    file_name=data.file_name,
                    file_type=data.file_type,
                    file_path=file_path,
                )
                print("add data successfully!!!")
            except ValueError as e:
                print(f"Failed to process file {data.file_name}: {str(e)}")

    async def add_file_by_chunking(
        self,
        data_list: List[FileUpload]
    ) -> None:
        """
        Adds files to the system by transferring them, loading their data,
        and storing them in a vector database.

        Args:
            data_list (List[FileUpload]): A list of FileUpload objects containing file metadata.

        Returns:
            None
        """
        for data in data_list:
            # file_path = await self._file_repository.file_transfer(data=data)
            file_path = data.url
            documents = await self._general_loader.aload_data(sources=[file_path])
            print(f"documents: {documents[0]}")
            print([doc.id_ for doc in documents])

            try:
                await self._vector_database.add_knowledge_by_chunking(
                    url=data.url,
                    file_type="link",
                    public_id=data.public_id,
                    file_name=data.file_name,
                    documents=documents,
                )
                print("Indexing successfully!!!")
                # print(os.path.basename(data))
                await self._file_repository.add_file(
                    url=data.url,
                    file_type="link",
                    public_id=data.public_id,
                    file_name=data.file_name,
                    file_path=file_path,
                )
                print("add data successfully!!!")
            except ValueError as e:
                print(f"Failed to process file {data.file_name}: {str(e)}")

    async def add_file_router(
        self,
        data_list: List[FileUpload],
    ) -> None:
        """
        Process a list of file uploads and add them based on their URL.

        Args:
            data_list (List[FileUpload]): A list of files to be uploaded.

        Returns:
            None
        """
        pattern = r"https://student\.uit\.edu\.vn/"

        for data in data_list:
            temp_list = []
            temp_list.append(data)
            match = re.search(pattern, data.url)

            if match:
                await self.add_file_by_chunking(
                    data_list=temp_list
                )
            else:
                await self.add_file_by_chunking(
                    data_list=temp_list
                )

    def delete_file(self, public_id: str = None) -> None:
        """
        Deletes a file and its associated knowledge from the vector database.

        Args:
            file_name (str): The name of the file to be deleted.

        Returns:
            None
        """
        self._file_repository.delete_specific_file(public_id=public_id)
        self._vector_database.delete_knowlegde(public_id=public_id)
