"""
Module for CRUD operations on the chat collection.
"""

from src.storage.mongodb import CRUDDocuments


class CRUDChatCollection(CRUDDocuments):
    """
    A class to handle CRUD operations for the result collection in the MongoDB database.
    """

    def __init__(self):
        """
        This constructor initializes the CRUDDocuments base class 
        and sets the collection attribute to the result collection.
        """
        CRUDDocuments.__init__(self)
        self.collection = CRUDDocuments.connection.db.chat_collection
