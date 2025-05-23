"""
This module is used to search for similar documents in a vector store.
"""

import os
from typing import List
from dotenv import load_dotenv
import tiktoken
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode

from src.utils.utility import convert_value

load_dotenv()

VECTOR_STORE_QUERY_MODE = convert_value(os.getenv('VECTOR_STORE_QUERY_MODE'))
SIMILARITY_TOP_1 = convert_value(os.getenv('SIMILARITY_TOP_1'))
ALPHA = convert_value(os.getenv('ALPHA'))
MAX_TOKENS = convert_value(os.getenv('MAX_TOKENS'))
THRESHOLD = convert_value(os.getenv('THRESHOLD'))


class SemanticSearch:
    """
    A class to perform semantic search on a vector store index.
    """

    def __init__(
        self,
        query_mode: str = VECTOR_STORE_QUERY_MODE,
        top_k: int = SIMILARITY_TOP_1,
        alpha: float = ALPHA,
        threshold: float = THRESHOLD,
        index: VectorStoreIndex = None
    ):
        """
        Initializes the SemanticSearch class with the provided parameters.

        Args:
            query_mode (str): Mode of querying the vector store.
            top_k (int): Number of top similar results to retrieve.
            alpha (float): Weighting factor for the similarity score.
            threshold (float): Score threshold for filtering results.
            index (VectorStoreIndex): The vector store index to search.
        """
        self._query_mode = query_mode
        self._top_k = top_k
        self._alpha = alpha
        self._threshold = threshold
        self._index = index
        self._encoding = tiktoken.get_encoding("cl100k_base")
        self._retriever = self._index.as_retriever(
            vector_store_query_mode=self._query_mode,
            similarity_top_k=SIMILARITY_TOP_1,
            alpha=ALPHA
        )

    async def retrieve_nodes(
        self,
        query: str = None
    ) -> List[TextNode]:
        """
        Retrieves relevant nodes based on the query.

        Args:
            query (str): The user's query to search for.

        Returns:
            List[TextNode]: A list of retrieved text nodes.
        """
        retrieved_nodes = await self._retriever.aretrieve(query)

        return retrieved_nodes

    async def get_relevant_answer(
        self,
        query: str = None
    ) -> str:
        """
        Retrieves the most relevant answer for the given query.

        Args:
            query (str): The user's query to search for.

        Returns:
            str: The most relevant answer based on the query.
        """
        retrieved_nodes = await self.retrieve_nodes(query=query)

        if retrieved_nodes:
            print(f"the score: {retrieved_nodes[0].score}")
            if retrieved_nodes[0].score <= self._threshold:
                return retrieved_nodes[0].metadata['answer']

        return None
