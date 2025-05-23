"""
This module defines the HybridRetriever class for retrieving documents
using a hybrid approach combining vector search and traditional retrieval methods.
"""

import os
from typing import List
from dotenv import load_dotenv
import tiktoken
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode

from src.utils.utility import convert_value

load_dotenv()

MAX_TOKENS = convert_value(os.getenv('MAX_TOKENS'))
VECTOR_STORE_QUERY_MODE = convert_value(os.getenv('VECTOR_STORE_QUERY_MODE'))
SIMILARITY_TOP_K = convert_value(os.getenv('SIMILARITY_TOP_K'))
ALPHA = convert_value(os.getenv('ALPHA'))
THRESHOLD = convert_value(os.getenv('THRESHOLD'))


class HybridRetriever:
    """
    HybridRetriever class for retrieving documents using both vector search 
    and BM25 retrieval methods.
    """

    def __init__(
        self,
        index: VectorStoreIndex = None
    ):
        """
        Initializes the HybridRetriever with the given configuration parameters.
        """
        self._index = index
        self._encoding = tiktoken.get_encoding("cl100k_base")
        self.retriever = self._index.as_retriever(
            vector_store_query_mode="hybrid",
            similarity_top_k=10,
            alpha=0.65
        )

    @property
    def token_counter(self):
        """
        Retrieves the current token encoding used by the model.

        Returns:
            Any: The encoding object that represents the current token state.
        """
        return self._encoding

    async def combine_retrieved_nodes(
        self,
        retrieved_nodes: List[TextNode],
        max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Combines multiple retrieved TextNode objects into a single string.
        Args:
            retrieved_nodes (List[TextNode]): The list of TextNode objects to be combined.
            max_tokens (int, optional): The maximum number of tokens.
        Returns:
            str: The combined string of text nodes up to the token limit.
        """
        combined_strings = ""
        current_tokens = 0

        for retrieved_node in retrieved_nodes:
            text = retrieved_node.text
            metadata = str(retrieved_node.metadata)
            sub_combine = text + "\nmetadata:\n" + metadata
            tokens = len(self._encoding.encode(sub_combine))

            if tokens + current_tokens > max_tokens:
                break

            combined_strings = combined_strings + "\n" + "=" * 20 + "\n" + sub_combine
            current_tokens += tokens

        return combined_strings

    async def retrieve_nodes(
        self,
        query: str
    ) -> List[TextNode]:
        """
        Retrieves nodes based on a given query.

        Args:
            query (str): The search query to retrieve TextNode objects.

        Returns:
            Tuple[str, List[TextNode]]: A tuple containing the combined text
                                         and the list of original TextNode objects.
        """
        retrieved_nodes = await self.retriever.aretrieve(query)
        combined_retrieved_nodes = await self.combine_retrieved_nodes(
            retrieved_nodes=retrieved_nodes,
        )

        return combined_retrieved_nodes, retrieved_nodes
