"""
this model provides a data model for representing a processed data entry
"""

from pydantic import BaseModel


class ProcessedData(BaseModel):
    """
    Represents the processed data of a user's query.

    Attributes:
        query (str): The processed query text.
        language (bool): A flag indicating whether the language is detected
        is_prompt_injection (bool): A flag indicating if the query contains a prompt injection.
        is_outdomain (bool): A flag indicating if the query is outside the expected domain.
    """
    query: str
    language: bool
    is_prompt_injection: bool
    is_outdomain: bool
    is_short_chat: bool
    is_only_icon: bool


class ShortChat(BaseModel):
    """
    Represents a short chat interaction.

    Attributes:
        query (str): The original user query.
        clean_query (str): The cleaned version of the user query for processing.
        is_short_chat (bool): Indicates whether the interaction.
        short_chat_response (str): The response generated for the short chat.
    """
    query: str
    clean_query: str
    is_short_chat: bool
    short_chat_response: str


class UnsupportedLanguage(BaseModel):
    """
    Model for unsupported language responses.

    Attributes:
        language (bool): Indicates if the language is unsupported.
        response (str): Message about unsupported language.
    """
    language: bool
    response: str


class PromptInjection(BaseModel):
    """
    Model for prompt injection detection.

    Attributes:
        is_prompt_injection (bool): Indicates if prompt injection was detected.
        response (str): Response for prompt injection case.
    """
    is_prompt_injection: bool
    response: str
