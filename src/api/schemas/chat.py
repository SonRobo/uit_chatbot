"""
This schemas is used for chat
"""

from typing import List
from pydantic import BaseModel


class RequestChat(BaseModel):
    """
    A model for representing a chat request.
    """
    room_id: str
    query: str


class ResponseChat(BaseModel):
    """
    A model for representing a chat response.
    """
    response: str
    is_outdomain: bool


class RequestChatSuggestion(BaseModel):
    """
    A model for representing a chat suggestion request.
    """
    query: str


class ResponseChatSuggestion(BaseModel):
    """
    A model for representing a response with chat suggestions.
    """
    response: str
    suggestion: List[str]
