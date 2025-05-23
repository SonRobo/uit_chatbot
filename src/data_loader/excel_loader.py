"""
This module provides a class for loading and processing data from Excel files.
"""

from typing import List
import pandas as pd
from llama_index.core.schema import Document

from src.data_loader.base_loader import BaseLoader


class ExcelLoader(BaseLoader):
    """
    A class for loading and processing data from Excel files.

    It converts Excel data into markdown format for easier manipulation.

    Methods:
    - convert_to_markdown: Converts Excel content to markdown format.
    - load_data: Loads data from a list of Excel files and processes it into markdown format.
    """

    @staticmethod
    def convert_to_markdown(file_path: str) -> str:
        """
        Convert the contents of an Excel file to markdown format.

        Args:
            file_path (str): The path to the Excel file.

        Returns:
            str: A string containing the file's contents in markdown format.
        """
        df = pd.read_excel(file_path)
        df.dropna(how='all', axis=0, inplace=True)
        df.dropna(how='all', axis=1, inplace=True)
        df.set_index(df.columns[0], inplace=True)
        df.replace(to_replace=r'\n', value='<br>', regex=True, inplace=True)

        return df.to_markdown()

    def load_data(
        self,
        sources: List[str]
    ) -> List[Document]:
        """
        Load data from a list of Excel files and convert the contents to markdown format.

        Args:
            files_list (List[str]): A list of paths to Excel files.

        Returns:
            List[Document]: A list of Document objects containing 
                            the loaded data in markdown format.
        """
        documents = []

        for file in sources:
            markdown_text = self.convert_to_markdown(file)
            documents.append(
                Document(
                    text=markdown_text,
                    metadata={'file_path': file}
                )
            )

        return documents
