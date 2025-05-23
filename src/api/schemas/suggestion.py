"""
This schemas is used for suggestion
"""

from typing import List
from pydantic import BaseModel


class ResponseSuggestion(BaseModel):
    """
    A model for representing suggestion
    """
    question: str
    answer: str


class ResponseSuggestionList(BaseModel):
    """
    A model for representing suggestion list
    """
    suggestion: List[ResponseSuggestion]


class Suggestion(BaseModel):
    """A Pydantic model representing a suggestion with key attributes.

    Attributes:
        Id (str): A unique identifier for the suggestion.
        query (str): The user's query or question.
        answer (str): The response generated for the query.
        time (str): The timestamp of when the query was processed.
    """
    Id: str
    question: str
    answer: str
    time: str
