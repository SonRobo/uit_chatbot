"""
This module provides a wrapper class Weaviate database
for managing a vector store using Weaviate and LlamaIndex.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
import weaviate
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.schema import (
    Document,
    TextNode,
    NodeRelationship,
    RelatedNodeInfo,
    ObjectType,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from scrapegraphai.graphs import SmartScraperGraph

from src.utils.utility import convert_value
from src.prompt.loader_prompt import URL_SPLITER_PROMPT
from src.utils.openai_call import get_major_name_from_link

load_dotenv()

WEAVIATE_HOST = convert_value(os.getenv("WEAVIATE_HOST"))
WEAVIATE_PORT = convert_value(os.getenv("WEAVIATE_PORT"))
WEAVIATE_NAME = convert_value(os.getenv("WEAVIATE_NAME"))
SUGGESTION_NAME = convert_value(os.getenv("SUGGESTION_NAME"))
MONGODB_URL = convert_value(os.getenv("MONGODB_URL"))
MONGODB_NAME = convert_value(os.getenv("MONGODB_NAME"))
OPENAI_MODEL_GRAPH = convert_value(os.getenv("OPENAI_MODEL_GRAPH"))
OPENAI_EMBED_MODEL = convert_value(os.getenv("OPENAI_EMBED_MODEL"))
CHUNK_SIZE = convert_value(os.getenv("CHUNK_SIZE"))


class WeaviateDB:
    """
    WeaviateDB is a wrapper class for managing a Weaviate-based vector store.
    """

    def __init__(
        self,
        host: str = WEAVIATE_HOST,
        port: str = WEAVIATE_PORT,
        index_name: str = WEAVIATE_NAME,
        suggestion_name: str = SUGGESTION_NAME,
        mongodb_url: str = MONGODB_URL,
        mongodb_name: str = MONGODB_NAME,
        documents: List[Document] = None,
    ):
        """
        Initializes the WeaviateDB class with the specified host, port
        and index name for the Weaviate instance,
        and optionally a list of documents.
        """
        self._host = host
        self._port = port
        self._index_name = index_name
        self._suggestion_name = suggestion_name
        self._documents = documents
        self._mongodb_url = mongodb_url
        self._mongodb_name = mongodb_name
        self._client = weaviate.connect_to_local(host=self._host, port=self._port)
        self._vector_store = WeaviateVectorStore(
            weaviate_client=self._client, index_name=self._index_name
        )
        self._suggestion_vector_store = WeaviateVectorStore(
            weaviate_client=self._client, index_name=self._suggestion_name
        )
        self._storage_context = StorageContext.from_defaults(
            docstore=MongoDocumentStore.from_uri(
                uri=self._mongodb_url, db_name=self._mongodb_name
            ),
            vector_store=self._vector_store,
        )
        self._suggestion_storage_context = StorageContext.from_defaults(
            vector_store=self._suggestion_vector_store
        )
        self.parser = SentenceSplitter(chunk_size=CHUNK_SIZE)
        # if self._documents:
        #     self._index = VectorStoreIndex.from_documents(
        #         documents=self._documents, storage_context=self._storage_context
        #     )
        # else:
        #     self._index = VectorStoreIndex.from_vector_store(
        #         vector_store=self._vector_store
        #     )
        self._index = VectorStoreIndex.from_vector_store(
                 vector_store=self._vector_store
        )
        self._suggestion_index = VectorStoreIndex.from_vector_store(
            vector_store=self._suggestion_vector_store
        )

    @property
    def index(self) -> VectorStoreIndex:
        """
        Returns the VectorStoreIndex object that is used for
        querying and retrieving documents from the Weaviate database.

        Args:
            None

        Returns:
            VectorStoreIndex: The VectorStoreIndex object
        """
        return self._index

    @property
    def client(self) -> weaviate:
        """
        Provides access to the Weaviate client instance.
        """
        return self._client

    def configure_documents(
        self,
        url: Optional[str] = None,
        documents: List[Document] = None,
        file_type: Optional[str] = None,
        file_name: Optional[str] = None,
        public_id: Optional[str] = None,
    ) -> List[Document]:
        """
        Updates the metadata of a list of Document objects with a specified file name.

        Args:
            file_type (Optional[str]): The default file type to set in the metadata
                                        if it is not already present.
            file_name (Optional[str]): The default file name to set in the metadata
                                        if it is not already present.
            public_id (Optional[str]): The default public ID to set in the metadata
                                        if it is not already present.
            documents (List[Document]): A list of Document objects to be configured.

        Returns:
            List[Document]: The list of Document objects with updated metadata.
        """
        for idx, doc in enumerate(documents):
            if "file_path" not in doc.metadata:
                doc.metadata.update(
                    {"public_id": public_id, "link": url, "file_type": file_type}
                )
                doc.excluded_embed_metadata_keys = [
                    "file_name",
                    "public_id",
                    "file_type",
                    "link",
                ]
                doc.excluded_llm_metadata_keys = [
                    "file_name",
                    "public_id",
                    "file_type",
                    "link",
                ]
            if "public_id" not in doc.metadata:
                doc.metadata.update(
                    {
                        "public_id": public_id,
                        "file_name": file_name,
                        "file_type": file_type,
                        "page": idx + 1,
                    }
                )
                doc.excluded_embed_metadata_keys = [
                    "file_name",
                    "public_id",
                    "page",
                    "file_type",
                    "file_path",
                ]
                doc.excluded_llm_metadata_keys = [
                    "file_name",
                    "public_id",
                    "page",
                    "file_type",
                    "file_path",
                ]
        return documents

    async def suggestion_config(
        self,
        question: str = None,
        answer: str = None
    ) -> List[Document]:
        """
        Creates a list of Document objects based on the provided question and answer.

        Args:
            question (str): The question text.
            answer (str): The corresponding answer text.

        Returns:
            List[Document]: A list of Document objects with metadata, or None if inputs are missing.
        """
        if question and answer:
            document = [
                Document(text=answer, metadata={"question": question, "answer": answer})
            ]
            return self.documents_to_nodes(documents=document)

        return None

    async def insert_suggestion_nodes(
        self,
        nodes: List[TextNode]
    ) -> None:
        """
        Inserts a list of TextNode objects into the suggestion index.

        Args:
            nodes (List[TextNode]): A list of nodes to be inserted.
        """
        if nodes:
            self._suggestion_index.insert_nodes(nodes=nodes)

    def documents_to_nodes(
        self,
        documents: List[Document]
    ) -> List[TextNode]:
        """
        Converts a list of Document objects into a list of TextNode objects.

        Args:
            documents (List[Document]): A list of Document objects to be
                                        converted into TextNode objects.

        Returns:
            List[TextNode]: A list of TextNode objects derived from the given documents.
        """
        nodes = self.parser.get_nodes_from_documents(documents=documents)

        return nodes

    def get_sessions_splitter(
        self,
        text
    ):
        """Splitter to split text of a document into many nodes containing sessions.

        Args:
            text (str): input text

        Returns:
            SmartScraperGraph: A class including fetching, parsing and generating answer
            based on prompt and source using LLMs and text embedding model.
        """
        graph_config = {
            "llm": {
                "model": OPENAI_MODEL_GRAPH,
                "temperature": 0,
            },
            # "embeddings": {
            #     "model": OPENAI_EMBED_MODEL,
            #     "temperature": 0,
            # },
            # "verbose": True,
        }

        return SmartScraperGraph(
            prompt=URL_SPLITER_PROMPT,
            source=text,
            config=graph_config,
        )

    def documents_to_nodes_by_sessions(
        self,
        documents: List[Document]
    ) -> List[TextNode]:
        """
        Converts a list of Document objects into a list of TextNode
        objects splitted by sessions using ScrapeGraph:
        https://github.com/ScrapeGraphAI/Scrapegraph-ai.

        Args:
            documents (List[Document]): A list of Document objects to be
                                        converted into TextNode objects.

        Returns:
            List[TextNode]: A list of TextNode objects splitted by sessions.
            derived from the given documents.
        """
        nodes_of_docs = []

        for doc in documents:
            splitter = self.get_sessions_splitter(doc.text)
            # splitted_text_list = [{'title': 'Title A', 'content': 'content A'}]
            splitted_text_list = splitter.run()
            # print(splitted_text_list)
            splitted_text_list = splitted_text_list["sessions"]
            # Add each TextNode to list nodes
            nodes = []
            for text_dict in splitted_text_list:
                title = text_dict["title"]
                content = text_dict["content"]
                node = TextNode(text=title + "\n" + content)
                nodes.append(node)
            # Add relationship throughout TextNodes
            for i, node in enumerate(nodes):
                # Add source relationship
                node.relationships[NodeRelationship.SOURCE] = RelatedNodeInfo(
                    node_id=doc.id_,
                    node_type=ObjectType.DOCUMENT,
                    metadata=doc.metadata,
                    hash=doc.hash,
                )

                if len(nodes) == 1:  # If there is only 1 nodes --> pass
                    continue

                if i == 0:  # If it is Start node, add next node relationship
                    node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                        node_id=nodes[i + 1].node_id,
                        node_type=ObjectType.TEXT,
                        hash=nodes[i + 1].hash,
                    )

                elif (
                    i == len(nodes) - 1
                ):  # If it is End node, add previous node relationship
                    node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                        node_id=nodes[i - 1].node_id,
                        node_type=ObjectType.TEXT,
                        hash=nodes[i - 1].hash,
                    )

                else:  # Add both previous node and next node relationship for remaining nodes
                    node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                        node_id=nodes[i - 1].node_id,
                        node_type=ObjectType.TEXT,
                        hash=nodes[i - 1].hash,
                    )
                    node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                        node_id=nodes[i + 1].node_id,
                        node_type=ObjectType.TEXT,
                        hash=nodes[i + 1].hash,
                    )
                # Add metadata
                node.metadata = doc.metadata
                # doc.metadata.update({"tiêu đề": title})
                node.excluded_embed_metadata_keys = doc.excluded_embed_metadata_keys
                node.excluded_llm_metadata_keys = doc.excluded_llm_metadata_keys

            # Extend the nodes_of_docs list including nodes from multiple documents
            nodes_of_docs.extend(nodes)

        return nodes_of_docs

    def insert_nodes(
        self,
        nodes: List[TextNode]
    ) -> str:
        """
        Adds a list of nodes into the vector store.

        Args:
            nodes (List[Node]): List of nodes to be added.

        Returns:
            None
        """
        if nodes:
            self._index.insert_nodes(nodes=nodes)

    def delete_nodes(
        self,
        ref_doc_id: str = None
    ) -> None:
        """
        Deletes a document from the vector store using the reference document ID.

        Returns:
            None

        Args:
            ref_doc_id (str, optional): The reference document ID of the document to be deleted.
        """
        if ref_doc_id:
            self._index.delete_ref_doc(ref_doc_id=ref_doc_id)

    def insert_docstore(
        self,
        nodes: List[TextNode]
    ) -> None:
        """
        Inserts a list of TextNode objects into the document store.

        Args:
        nodes (List[TextNode]): A list of TextNode objects to be inserted
                                into the document store.

        Returns:
            None
        """
        if nodes:
            self._storage_context.docstore.add_documents(nodes)

    def delete_docstore(
        self,
        ref_doc_id: str = None
    ) -> None:
        """
        Deletes a document from the document store using its reference document ID.

        Args:
        ref_doc_id (str, optional): The reference document ID of the document to be deleted.
                                    If None, no action is taken.

        Returns:
            None
        """
        if ref_doc_id:
            self._storage_context.docstore.delete_ref_doc(ref_doc_id=ref_doc_id)

    async def add_knowledge(
        self,
        url: str = None,
        file_type: str = None,
        public_id: str = None,
        file_name: str = None,
        documents: List[Document] = List[None],
    ) -> None:
        """
        Adds a list of Document objects to the knowledge base.

        Args:
            file_name (str, optional): The name of the file associated with the documents.
            documents (List[Document], optional): A list of Document objects to be added.
                                                  Defaults to an empty list if not provided.

        Returns:
            None
        """
        if documents:
            processed_documents = self.configure_documents(
                url=url,
                file_type=file_type,
                file_name=file_name,
                public_id=public_id,
                documents=documents,
            )
            # nodes = self.documents_to_nodes(documents=processed_documents)
            nodes = self.documents_to_nodes_by_sessions(documents=processed_documents)

            self.insert_nodes(nodes=nodes)
            self.insert_docstore(nodes=nodes)

    async def add_knowledge_by_chunking(
        self,
        url: str = None,
        file_type: str = None,
        public_id: str = None,
        file_name: str = None,
        documents: List[Document] = List[None],
    ) -> None:
        """
        Adds a list of Document objects to the knowledge base.

        Args:
            file_name (str, optional): The name of the file associated with the documents.
            documents (List[Document], optional): A list of Document objects to be added.
                                                  Defaults to an empty list if not provided.

        Returns:
            None
        """
        if documents:
            processed_documents = self.configure_documents(
                url=url,
                file_type=file_type,
                file_name=file_name,
                public_id=public_id,
                documents=documents,
            )
            nodes = self.documents_to_nodes(documents=processed_documents)
            title = os.path.basename(file_name)
            vietnamese_title = await get_major_name_from_link(title)
            print("Tiêu đề:", vietnamese_title.text)
            # For each node add vietnamese_title in node.text

            for node in nodes:
                node.text = f"Tiêu đề: {vietnamese_title.text}\n{node.text}"

            self.insert_nodes(nodes=nodes)
            self.insert_docstore(nodes=nodes)

    def delete_knowlegde(
        self,
        public_id: str = None
    ) -> None:
        """
        Deletes documents from the knowledge base by file name.

        Args:
            file_name (str, optional): The name of the file associated with the documents
                                       to be deleted. If None, no action is taken.
        """
        ref_doc_ids = []
        for _, node in self._storage_context.docstore.docs.items():
            if (
                node.metadata.get("public_id") == public_id
                and node.ref_doc_id not in ref_doc_ids
            ):
                self.delete_nodes(ref_doc_id=node.ref_doc_id)
                print(f"delete node with ref_doc_id {node.ref_doc_id} successfully ")
                self.delete_docstore(ref_doc_id=node.ref_doc_id)
                print(
                    f"delete doc from docstore with ref_doc_id {node.ref_doc_id} successfully "
                )
                ref_doc_ids.append(node.ref_doc_id)

    def delete_collection(
        self,
        collection_name: str = None
    ) -> None:
        """
        Deletes a collection from the document storage by name.

        Args:
            collection_name (str, optional): The name of the collection to be deleted.
                                             If None, no action is taken.

        Returns:
            None
        """
        self._client.collections.delete(name=collection_name)
