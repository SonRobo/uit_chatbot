"""
this service provides retrieve and chat module for chatbot
"""

from typing import Any

from src.engines.chat_engine import ChatEngine
from src.engines.retriever_engine import HybridRetriever
from src.engines.semantic_engine import SemanticSearch
from src.engines.preprocess_engine import PreprocessQuestion
from src.engines.enhance_chat_engine import EnhanceChatEngine
from src.engines.agent_engine import AgentEngine
from src.repositories.chat_repository import ChatRepository
from src.models.chat import Chat


class RetrieveChat:
    """
    RetrieveChat: A class designed to retrieve chat responses.
    """

    def __init__(
        self,
        retriever: HybridRetriever = None,
        chat: ChatEngine = None,
        preprocess: PreprocessQuestion = None,
        semantic: SemanticSearch = None,
        chat_history_tracker: ChatRepository = None,
        max_chat_token: float = 2000,
        enhance_chat_engine: EnhanceChatEngine = None,
        agent: AgentEngine = None,
        rag_classifier: Any = None
    ) -> None:
        self._retriever = retriever
        self._chat = chat
        self._preprocess = preprocess
        self._semantic = semantic
        self._chat_history_tracker = chat_history_tracker
        self._max_chat_token = max_chat_token
        self._enhance_chat_engine = enhance_chat_engine
        self._agent = agent
        self._rag_classifier = rag_classifier

    async def history_chat_config(
        self,
        room_id: str
    ):
        """
        Retrieve and combine chat history for a specific room, limiting by token count.

        Args:
            room_id (str): The ID of the chat room.

        Returns:
            str: Combined chat history formatted as a string.
        """
        lastest_chats = await self._chat_history_tracker.get_last_chat(
            room_id=room_id
        )
        lastest_chats = list(lastest_chats)
        combine_history_chat = ""
        sum_token = 0

        for idx, chat in enumerate(reversed(lastest_chats)):
            record = f"question {idx + 1}: {chat['query']}\nanswer {idx + 1}: {chat['answer']}"
            tokens = len(self._retriever.token_counter.encode(record))
            if tokens + sum_token >= self._max_chat_token:
                break
            combine_history_chat = combine_history_chat + record + "\n"
            sum_token += tokens

        return combine_history_chat

    async def retrieve_chat(
        self,
        query: str,
        room_id: str
    ) -> Chat:
        """
        Process a chat query and retrieve a response, utilizing a domain classifier.

        Args:
            query (str): The user's chat query.
            room_id (str): The ID of the chat room.

        Returns:
            Chat: The response object containing the chat response and metadata.
        """
        chat_history = await self._enhance_chat_engine.history_config(
            room_id=room_id
        )

        # score = self._rag_classifier.predict_proba([query])[0][1]
        # print(f"domain score: {score}")

        # if score <= 0.5:
        #     previous_query = await self._chat_history_tracker.get_lastest_chat(room_id=room_id)
        #     if previous_query:
        #         print("re classify domain")
        #         temp_query = previous_query[0]["query"] + " " + query
        #         score_phrase_2 = self._rag_classifier.predict_proba(
        #             [temp_query]
        #         )[0][1]
        #         if score_phrase_2 >= 0.5:
        #             print("agent pipeline")
        #             response = await self._agent.reasoning_agent(
        #                 chat=query,
        #                 chat_history=chat_history
        #             )
        #             return Chat(
        #                 response=response,
        #                 is_outdomain=False,
        #                 retrieved_nodes=[]
        #             )
        #     print("Base RAG pipeline")
        #     response, retrieved_nodes = await self._enhance_chat_engine.enhance_chat(
        #         query=query,
        #         chat_history=chat_history
        #     )
        #     return Chat(
        #         response=response,
        #         is_outdomain=False,
        #         retrieved_nodes=retrieved_nodes
        #     )
        print("AGENT AI RAG pipeline")
        response = await self._agent.reasoning_agent(
            chat=query,
            chat_history=chat_history
        )

        return Chat(
            response=response,
            is_outdomain=False,
            retrieved_nodes=[]
        )

    async def preprocess_query(
        self,
        query: str,
        room_id: str
    ) -> Chat:
        """
        Preprocesses the user's query and generates an appropriate response.

        Args:
            query (str): The input query from the user.

        Returns:
            Chat: A Chat object containing the response, a flag indicating if the response
                is out of domain, and a list of retrieved nodes.
        """
        processed_query = await self._preprocess.preprocess_text(
            text_input=query
        )
        print(processed_query)

        if processed_query.is_only_icon:
            answer = await self._chat.chat(
                text=query
            )
            return Chat(
                response=answer,
                is_outdomain=True,
                retrieved_nodes=[]
            )

        if processed_query.is_short_chat:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )

        if processed_query.language is False:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )

        if processed_query.is_prompt_injection:
            return Chat(
                response=processed_query.query,
                is_outdomain=True,
                retrieved_nodes=[]
            )

        # if processed_query.is_outdomain:
        #     answer = await self._enhance_chat_engine.enhance_funny_chat(
        #         room_id=room_id,
        #         query=processed_query.query
        #     )
        #     if str(answer) == "True":
        #         print("classify again")
        #         return await self.retrieve_chat(
        #             query=processed_query.query,
        #             room_id=room_id
        #         )
        #     return Chat(
        #         response=answer,
        #         is_outdomain=True,
        #         retrieved_nodes=[]
        #     )

        return await self.retrieve_chat(
            query=processed_query.query,
            room_id=room_id
        )
