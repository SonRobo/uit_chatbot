"""
This module defines a data model for handling chat domain data using Pydantic.
"""

from typing import List
from pydantic import BaseModel


class Chat(BaseModel):
    """
    Represents a chat response model.

    Attributes:
        response (str): The text response generated for the chat.
        is_outdomain (bool): Indicates if the response is outside the expected domain.
        retrieved_nodes (List[str]): A list of node identifiers 
                                     that were retrieved to generate the response.
    """
    response: str
    is_outdomain: bool
    retrieved_nodes: List[str]


class ChatDomain(BaseModel):
    """
    A Pydantic model representing a chat domain entry.

    Attributes:
        Id (str): A unique identifier for the chat entry.
        query (str): The user's query or question.
        answer (str): The response generated for the query.
        time (str): The timestamp of when the query was processed.
        is_outdomain (bool): A flag indicating whether the query is outside 
                             the expected domain of questions.
    """
    Id: str
    room_id: str
    query: str
    answer: str
    retrieved_nodes: List[str]
    time: str
    is_outdomain: bool
