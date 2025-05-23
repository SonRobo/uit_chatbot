"""
This module provides a flexible framework for loading and processing data
from various sources including URLs, Excel files, and PDF files. It supports
converting data into markdown format for easy parsing and readability.
"""

from typing import List
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm
from llama_index.core.schema import Document

from src.data_loader.base_loader import BaseLoader
from src.data_loader.pdf_loader import PDFLoader
from src.data_loader.excel_loader import ExcelLoader
from src.data_loader.url_loader import URLLoader
from src.data_loader.image_loader import ImageLoader


class GeneralLoader(BaseLoader):
    """
    A general-purpose loader class for loading data from various sources (PDF, Excel, URL).

    It uses specific loaders for different file types and handles data extraction accordingly.

    Methods:
    - is_valid_url: Checks if a given string is a valid URL.
    - check_extension: Determines the source type based on file extension or URL.
    - load_data: Loads data from a list of sources, handling each based on its type.
    """

    def __init__(self) -> None:
        """
        Initialize the GeneralLoader with specific loaders for different file types.
        """
        self.pdf_loader = PDFLoader()
        self.excel_loader = ExcelLoader()
        self.url_loader = URLLoader()
        self.image_loader = ImageLoader()
        self.pdf_ext = [".pdf"]
        self.excel_ext = [".xls", ".xlsx", ".csv", ".tsv"]
        self.image_ext = [".jpg", ".jpeg", ".png",
                          ".svg", ".tiff", ".webp", ".bmp"]

    @staticmethod
    def is_valid_url(
        url: str,
        qualifying: tuple = ("scheme", "netloc")
    ) -> bool:
        """
        Check if the provided string is a valid URL.

        Args:
            url (str): The string to check.
            qualifying (tuple, optional): A tuple of qualifying attributes to verify.
                                          Defaults to ('scheme', 'netloc').

        Returns:
            bool: True if the string is a valid URL, False otherwise.
        """
        tokens = urlparse(url)

        return all(getattr(
            tokens, qualifying_attr
        ) for qualifying_attr in qualifying)

    def check_extension(self, file_path: str) -> str:
        """
        Check the file extension and determine the source type (PDF, Excel, or URL).

        Args:
            file_path (str): The path or URL of the file to check.

        Returns:
            str: A string representing the source type ('pdf', 'excel', or 'url').

        Raises:
            ValueError: If the file type is unsupported or the URL is invalid.
        """
        path = Path(file_path)

        if path.is_file():
            if path.suffix in self.pdf_ext:
                return "pdf"
            elif path.suffix in self.excel_ext:
                return "excel"
            elif path.suffix in self.image_ext:
                return "image"
        elif self.is_valid_url(file_path):
            return "url"
        else:
            raise ValueError(
                f"Unsupported file type or invalid URL: {file_path}")

    def load_data(self, sources: List[str]) -> List[Document]:
        """
        Load data from a list of sources, which may include PDF files, Excel files, and URLs.

        Args:
            sources (List[str]): A list of file paths or URLs to load data from.

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        documents = []

        for source in tqdm(sources):
            source_type = self.check_extension(source)
            if source_type == "pdf":
                documents.extend(
                    self.pdf_loader.load_data([source])
                )
            elif source_type == "excel":
                documents.extend(
                    self.pdf_loader.load_data([source])
                )
            elif source_type == "url":
                documents.extend(
                    self.url_loader.load_data([source])
                )
            elif source_type == "image":
                documents.extend(
                    self.image_loader.load_data([source])
                )
            else:
                print("Source type is not supported:", source_type)

        return documents

    async def aload_data(
        self,
        sources: List[str]
    ) -> List[Document]:
        """
        Load data from a list of sources, which may include PDF files, Excel files, and URLs.

        Args:
            sources (List[str]): A list of file paths or URLs to load data from.

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        documents = []

        for source in tqdm(sources):
            source_type = self.check_extension(source)
            if source_type == "pdf":
                documents.extend(
                    await self.pdf_loader.aload_data([source])
                )
            elif source_type == "excel":
                documents.extend(
                    await self.pdf_loader.aload_data([source])
                )
            elif source_type == "url":
                documents.extend(
                    await self.url_loader.aload_data([source])
                )
            elif source_type == "image":
                documents.extend(
                    await self.image_loader.aload_data([source])
                )
            else:
                print("Source type is not supported:", source_type)

        return documents
