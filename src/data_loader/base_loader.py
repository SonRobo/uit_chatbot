"""
This module provides an abstract base class for loading data from various sources.
"""

from typing import List, Union
from llama_index.core.schema import Document


class BaseLoader:
    """
    An abstract base class for loading data from various sources.
    """

    def load_data(
        self,
        sources: Union[str, List[str]]
    ) -> List[Document]:
        """
        Abstract method to load data from the specified source.

        Args:
            source (Union[str, List[str]]): A string or list of strings representing 
                                            the data source(s).

        Returns:
            List[Document]: A list of Document objects containing the loaded data.
        """
        raise NotImplementedError("Subclasses should implement this method")
