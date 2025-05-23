"""
Module for CRUD operations on the suggestion collection.
"""

from src.storage.mongodb import CRUDDocuments


class CRUDSuggestionCollection(CRUDDocuments):
    """
    A class to handle CRUD operations for the suggestion collection in the MongoDB database.
    """

    def __init__(self):
        """
        This constructor initializes the CRUDDocuments base class 
        and sets the collection attribute to the suggestion collection.
        """
        CRUDDocuments.__init__(self)
        self.collection = CRUDDocuments.connection.db.suggestion_collection
