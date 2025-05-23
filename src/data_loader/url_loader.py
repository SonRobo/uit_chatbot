"""
This module provides a class for loading and processing data from URLs.
"""

import re
from typing import List
import markdownify
from bs4 import BeautifulSoup
from llama_index.core.schema import Document
from llama_index.readers.web import SimpleWebPageReader

from src.data_loader.base_loader import BaseLoader
from src.utils.utility import get_last_part_of_url


class URLLoader(BaseLoader):
    """
    A class for loading and processing data from URLs.

    It extracts articles from HTML content and converts them to markdown format.

    Methods:
    - remove_duplicate_new_line: Removes duplicate newline characters from a string.
    - extract_articles: Extracts articles from HTML using the <article> tag.
    - load_data: Loads data from a list of URLs and processes it into markdown format.
    """

    @staticmethod
    def remove_duplicate_new_line(input_string: str) -> str:
        """
        Remove duplicate newline characters from the input string.

        Args:
            input_string (str): The string to process.

        Returns:
            str: The processed string with duplicate newlines removed.
        """
        return re.sub(r"\n+", "\n", input_string)

    @staticmethod
    def extract_articles(
        html_text: str
    ) -> str:
        """
        Extract articles from HTML content using the <article> tag.

        Args:
            html_text (str): The HTML content to process.
            delimiter (str, optional): The delimiter to use between
                                       extracted articles. Defaults to "\n\n".

        Returns:
            str: A string containing the extracted articles, separated by the delimiter.
        """
        # pattern = re.compile(r"<article.*?>(.*?)</article>", re.DOTALL)
        # matches = pattern.findall(html_text)
        # stripped_matches = [match.strip() for match in matches]
        # return delimiter.join(stripped_matches)

        soup = BeautifulSoup(html_text, "html.parser")
        main_div = soup.find("div", {"id": "content"})

        return str(main_div).strip()

    def load_data(
        self,
        sources: List[str]
    ) -> List[Document]:
        """
        Load data from a list of URLs and convert the content to markdown format.

        Args:
            urls (List[str]): A list of URLs to load data from.

        Returns:
            List[Document]: A list of Document objects containing
                            the loaded data in markdown format.
        """
        # Read html tag
        reader = SimpleWebPageReader()
        documents = reader.load_data(sources)
        processed_documents = []

        for doc in documents:
            # Get file_name
            file_name = get_last_part_of_url(doc.id_)
            # Extract <article> tag of HTML content
            articles = self.extract_articles(doc.text)
            # Remove duplicate new line
            articles = self.remove_duplicate_new_line(articles)
            # Convert to markdown format
            markdown_text = markdownify.markdownify(articles)
            # Add metadata
            document = Document(
                excluded_llm_metadata_keys=["url", "file_name", "file_type"],
                excluded_embed_metadata_keys=["url", "file_name", "file_type"],
                text=markdown_text,
                metadata={
                    "url": doc.id_,
                    "file_name": file_name,
                    "file_type": "web_page",
                },
            )
            processed_documents.append(document)

        return processed_documents

    async def aload_data(
        self,
        sources: List[str]
    ) -> List[Document]:
        """
        Load data from a list of URLs and convert the content to markdown format.

        Args:
            urls (List[str]): A list of URLs to load data from.

        Returns:
            List[Document]: A list of Document objects containing
                            the loaded data in markdown format.
        """
        # Read html tag
        reader = SimpleWebPageReader()
        documents = await reader.aload_data(sources)
        processed_documents = []

        for doc in documents:
            # Get file_name
            file_name = get_last_part_of_url(doc.id_)
            # Extract <article> tag of HTML content
            articles = self.extract_articles(doc.text)
            # Remove duplicate new line
            articles = self.remove_duplicate_new_line(articles)
            # Convert to markdown format
            markdown_text = markdownify.markdownify(articles)
            # Add metadata
            document = Document(
                excluded_llm_metadata_keys=["url", "file_name", "file_type"],
                excluded_embed_metadata_keys=["url", "file_name", "file_type"],
                text=markdown_text,
                metadata={
                    "url": doc.id_,
                    "file_name": file_name,
                    "file_type": "web_page",
                },
            )
            processed_documents.append(document)

        return processed_documents
