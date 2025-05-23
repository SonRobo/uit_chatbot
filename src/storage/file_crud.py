"""
Module for CRUD operations on the file collection.
"""

from src.storage.mongodb import CRUDDocuments


class CRUDFileCollection(CRUDDocuments):
    """
    A class to handle CRUD operations for the file collection in the MongoDB database.
    """

    def __init__(self):
        """
        This constructor initializes the CRUDDocuments base class 
        and sets the collection attribute to the result collection.
        """
        CRUDDocuments.__init__(self)
        self.collection = CRUDDocuments.connection.db.file_collection
