"""
This module provides a class for loading and processing data from pdf files.
"""

import os
from typing import List
from dotenv import load_dotenv
import nest_asyncio
from llama_parse import LlamaParse
from llama_parse.utils import Language, ResultType
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

from src.data_loader.base_loader import BaseLoader
from src.utils.utility import convert_value

nest_asyncio.apply()

load_dotenv()

PARSING_INSTRUCTION = convert_value(os.getenv("PARSING_INSTRUCTION"))


class PDFLoader(BaseLoader):
    """
    A class for loading and processing data from PDF files.

    It uses LlamaParse to convert PDF content into markdown format.

    Methods:
    - load_data: Loads data from a list of PDF files and processes it into markdown format.
    """

    def __init__(
        self,
        result_type: ResultType = ResultType.MD,
        language: Language = Language.VIETNAMESE,
        parsing_instruction: str = PARSING_INSTRUCTION,
    ):
        """
        Initialize the PDFLoader with the specified parsing options.

        Args:
            result_type (ResultType, optional): The desired result type (e.g., markdown).
                                                Defaults to ResultType.MD.
            language (Language, optional): The language of the documents to be processed.
                                           Defaults to Language.VIETNAMESE.
            parsing_instruction (str, optional): Instructions for parsing the PDF content.
                                                 Defaults to 'Parse and structure the information
                                                 from the file provided. Write in Vietnamese'.
        """
        self.num_workers = 4  # the more the faster but crash the server
        self.parser = LlamaParse(
            result_type=result_type,
            language=language,
            parsing_instruction=parsing_instruction,
            num_workers=self.num_workers,
            # invalidate_cache=False,
            max_timeout=3600,
        )
        self.extensions = [
            ".xls",
            ".xlsx",
            ".csv",
            ".tsv",
            ".jpg",
            ".jpeg",
            ".png",
            ".svg",
            ".tiff",
            ".webp",
            ".bmp",
            ".pdf",
        ]
        self.file_extractor = {ext: self.parser for ext in self.extensions}

    def load_data(
        self,
        sources: List[str]
    ) -> List[Document]:
        """
        Load data from a list of PDF files and return a list of Document objects.

        Args:
            files_list (List[str]): A list of paths to PDF files.

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        try:
            documents = SimpleDirectoryReader(
                input_files=sources, file_extractor=self.file_extractor
            ).load_data()

        except ValueError as e:
            print("Use default PDF, return text instead of markdown:", str(e))
            del self.file_extractor[".pdf"]
            documents = SimpleDirectoryReader(
                input_files=sources, file_extractor=self.file_extractor
            ).load_data()

        return documents

    async def aload_data(
        self,
        sources: List[str]
    ) -> List[Document]:
        """
        Load data from a list of PDF files and return a list of Document objects.

        Args:
            files_list (List[str]): A list of paths to PDF files.

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        try:
            print("Loading data from PDF files...")
            documents = await SimpleDirectoryReader(
                input_files=["./data/cam_nang_sau_dai_hoc_thac_si_truong_uit.pdf"], file_extractor=self.file_extractor
            ).aload_data()
            print("Data loaded successfully.")
            print("Documents:", documents[0])

        except ValueError as e:
            print("Use default PDF, return text instead of markdown:", str(e))
            del self.file_extractor[".pdf"]
            documents = await SimpleDirectoryReader(
                input_files=sources, file_extractor=self.file_extractor
            ).aload_data()
        print(documents)

        return documents
