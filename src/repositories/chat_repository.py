"""
This repository class for managing chat collec in the question answering system.
"""

from typing import (
    List,
    Any
)

from src.storage.chat_crud import CRUDChatCollection
from src.models.chat import ChatDomain
from src.utils.utility import (
    create_new_id,
    get_datetime
)


class ChatRepository:
    """
    A repository class for managing result documents in the question answering system.
    """

    def __init__(self):
        """
        Initializes the collection attribute with a CRUDResultCollection instance 
        and loads all data into the data attribute.
        """
        self.collection = CRUDChatCollection()
        self.data = self.load_all_data()

    def load_all_data(self):
        """
        Load all documents from the collection.

        Args:
            None

        Returns:
            list: A list of documents with '_id' field as a string.
        """
        self.data = list(self.collection.find_all_doc())

        for doc in self.data:
            doc["_id"] = str(doc["_id"])

        return self.data

    async def add_one_record(
        self,
        chat: ChatDomain
    ):
        """
        Add a new chat domain document to the collection.

        Args:
            chat (ChatDomain): The chat document to be added.

        Returns:
            None
        """
        self.collection.insert_one_doc(chat.__dict__)

    async def add_chat_domains(
        self,
        room_id: str,
        query: str,
        answer: str,
        retrieved_nodes: List[str],
        is_out_of_domain: bool = False
    ) -> None:
        """
        Add a new chat domain document to the collection.

        Args:
            query (str): The user's query.
            answer (str): The chatbot's answer to the query.
            inference_time (float): The time it took to generate the answer.
            retrieved_nodes (List): the list of retrieved nodes.
            is_out_of_domain (bool, optional): Flag indicating if the query 
                                               is out of domain. Defaults to False.

        Returns:
            None
        """
        chat_domain_id = create_new_id(prefix="chatdomain")
        timestamp = get_datetime()

        chat_instance = ChatDomain(
            Id=chat_domain_id,
            room_id=room_id,
            query=query,
            answer=answer,
            retrieved_nodes=retrieved_nodes,
            time=timestamp,
            is_outdomain=is_out_of_domain
        )

        await self.add_one_record(chat=chat_instance)

    async def get_last_chat(
        self,
        room_id: str
    ) -> ChatDomain:
        """
        Retrieve the last five chat messages from a specific room.

        Args:
            room_id (str): The ID of the chat room.

        Returns:
            ChatDomain: The last five chat messages from the room.
        """
        filter_obj = {"room_id": room_id}
        latest_chats = await self.collection.find_with_filter(
            filter_obj=filter_obj,
            sort_by=("time", -1),
            limit=5
        )

        return latest_chats

    async def get_room_chat(
        self,
        room_id: str
    ) -> Any:
        """
        Get all chat records for a specified room.

        Args:
            room_id (str): The ID of the chat room.

        Returns:
            Any: All chat records for the room.
        """
        filter_obj = {"room_id": room_id}
        records = self.collection.find_one_doc(
            obj=filter_obj
        )

        return records

    async def delete_room_chat(
        self,
        room_id: str
    ) -> bool:
        """
        Delete all chat records for a given room.

        Args:
            room_id (str): The ID of the chat room.

        Returns:
            bool: True if records were deleted, otherwise False.
        """
        filter_obj = {"room_id": room_id}
        records = await self.collection.delete_many_doc(
            obj=filter_obj
        )

        if records.deleted_count > 0:
            return True

        return False

    async def get_lastest_chat(
        self,
        room_id: str
    ) -> List[ChatDomain]:
        """
        Retrieve the most recent chat message from a specific room.

        Args:
            room_id (str): The ID of the chat room.

        Returns:
            List[ChatDomain]: The most recent chat message from the room.
        """
        filter_obj = {"room_id": room_id}
        latest_chats = await self.collection.find_with_filter(
            filter_obj=filter_obj,
            sort_by=("time", -1),
            limit=1
        )

        return list(latest_chats)
