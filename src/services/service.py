"""
This module provides services for handling LLM and embedding models using OpenAI's API
"""

import os
import joblib
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import fasttext
import torch
from huggingface_hub import hf_hub_download
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from transformers import (AutoTokenizer,
                          AutoModelForTokenClassification)

from src.storage.weaviatedb import WeaviateDB
from src.engines.retriever_engine import HybridRetriever
from src.engines.chat_engine import ChatEngine
from src.engines.enhance_chat_engine import EnhanceChatEngine
from src.engines.agent_engine import AgentEngine
from src.utils.utility import convert_value
from src.repositories.chat_repository import ChatRepository
from src.repositories.file_repository import FileRepository
from src.data_loader.general_loader import GeneralLoader
from src.services.file_management import FileManagement
from src.repositories.suggestion_repository import SuggestionRepository
from src.engines.preprocess_engine import PreprocessQuestion
from src.engines.semantic_engine import SemanticSearch
from src.prompt.preprocessing_prompt import SAFETY_SETTINGS
from src.services.retrieve_chat import RetrieveChat

load_dotenv()

# Accessing variables
api_key = os.getenv('api_key')
azure_endpoint = os.getenv('azure_endpoint')
api_version = os.getenv('api_version')
deployment_name = os.getenv("deployment_name")
model_name = os.getenv("model_name")
openai_key = os.getenv("OPENAI_API_KEY")



OPENAI_API_KEY = convert_value(os.getenv('OPENAI_API_KEY'))
OPENAI_MODEL = convert_value(os.getenv('OPENAI_MODEL'))
OPENAI_MODEL_COMPLEX_TASK = convert_value(
    os.getenv('OPENAI_MODEL_COMPLEX_TASK')
)
OPENAI_EMBED_MODEL = convert_value(os.getenv('OPENAI_EMBED_MODEL'))
TEMPERATURE_MODEL = convert_value(os.getenv('TEMPERATURE_MODEL'))
GEMINI_API_KEY = convert_value(os.getenv('GEMINI_API_KEY'))
GEMINI_LLM_MODEL = convert_value(os.getenv('GEMINI_LLM_MODEL'))
TEMPERATURE = convert_value(os.getenv('TEMPERATURE'))
TOP_P = convert_value(os.getenv('TOP_P'))
TOP_K = convert_value(os.getenv('TOP_K'))
MAX_OUTPUT_TOKENS = convert_value(os.getenv('MAX_OUTPUT_TOKENS'))
DOMAIN_CLF_MODEL = convert_value(os.getenv('DOMAIN_CLF_MODEL'))
PROMPT_INJECTION_MODEL = convert_value(os.getenv('PROMPT_INJECTION_MODEL'))
RAG_CLASSIFIER_MODEL = convert_value(os.getenv('RAG_CLASSIFIER_MODEL'))
TONE_MODEL = convert_value(os.getenv('TONE_MODEL'))
URL = convert_value(os.getenv('LABEL_LIST'))
MAX_HISTORY_TOKENS = convert_value(os.getenv('MAX_HISTORY_TOKENS'))


class Service:
    """
    A service class that sets up and manages LLM and embedding models using OpenAI
    """

    def __init__(self):
        """
        Initializes the Service class with LLM and embedding models.
        """
        self._device = torch.device(
            "cuda") if torch.cuda.is_available() else torch.device("cpu")
        genai.configure(
            api_key=GEMINI_API_KEY
        )
        self._domain_clf_model = joblib.load(
            filename=DOMAIN_CLF_MODEL
        )
        self._prompt_injection_model = joblib.load(
            filename=PROMPT_INJECTION_MODEL
        )
        self._rag_classifier_model = joblib.load(
            filename=RAG_CLASSIFIER_MODEL
        )
        self._tone_tokenizer = AutoTokenizer.from_pretrained(
            TONE_MODEL, add_prefix_space=True)
        self._tone_model = AutoModelForTokenClassification.from_pretrained(
            TONE_MODEL
        ).to(self._device)
        self._generation_config = {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "top_k": TOP_K,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        }
        self._lang_detect_model_path = hf_hub_download(
            repo_id="facebook/fasttext-language-identification",
            filename="model.bin"
        )
        self._lang_detector = fasttext.load_model(self._lang_detect_model_path)
        # self._raw_text = requests.get(URL, timeout=60).text
        self._raw_text = """en\nvi\nja\nko\nzh-cn\nzh-tw\nen-us\nen-gb"""
        self._label_list = self._raw_text.split("\n")
        self._llm = OpenAI(
            api_key=OPENAI_API_KEY, model=OPENAI_MODEL, temperature=TEMPERATURE_MODEL
        )
        # self._complex_llm = OpenAI(
        #     api_key=OPENAI_API_KEY,
        #     model=OPENAI_MODEL_COMPLEX_TASK,
        #     temperature=TEMPERATURE_MODEL
        # )
        self._complex_llm = AzureOpenAI(
                    model=model_name,
                    engine=deployment_name,
                    api_key=api_key,
                    azure_endpoint=azure_endpoint,
                    api_version=api_version
        )
        self._embed_model = OpenAIEmbedding(
            api_key=OPENAI_API_KEY,
            model=OPENAI_EMBED_MODEL
        )
        # self._embed_model = HuggingFaceEmbedding(
        #     model_name="hiieu/halong_embedding",
        #     truncate_dim=768,
        #     trust_remote_code=True
        # )
        self._gemini = genai.GenerativeModel(
            model_name=GEMINI_LLM_MODEL,
            generation_config=self._generation_config,
            safety_settings=SAFETY_SETTINGS,
        )
        Settings.llms = self._llm
        Settings.embed_model = self._embed_model
        self._vector_database = WeaviateDB()
        self._retriever = HybridRetriever(
            index=self._vector_database.index
        )
        self._suggestion_repository = SuggestionRepository()
        self._chat_engine = ChatEngine(
            language_model=self._llm,
            complex_model=self._complex_llm,
            weaviate_db=self._vector_database,
            suggestion_repository=self._suggestion_repository
        )
        self._preprocess_engine = PreprocessQuestion(
            domain_clf_model=self._domain_clf_model,
            lang_detect_model=self._lang_detector,
            tonemark_model=self._tone_model,
            tonemark_tokenizer=self._tone_tokenizer,
            prompt_injection_model=self._prompt_injection_model,
            device_type=self._device,
            label_list=self._label_list
        )
        self._semantic_engine = SemanticSearch(
            index=self._vector_database._suggestion_index
        )
        self._chat_repository = ChatRepository()
        self._enhance_chat_engine = EnhanceChatEngine(
            llm=self._llm,
            retriever=self._retriever.retriever,
            chat_memory_tracker=self._chat_repository,
            token_limit=MAX_HISTORY_TOKENS,
            index=self._vector_database.index
        )
        self._agent_engine = AgentEngine(
            retriever=self._retriever.retriever,
            index=self._vector_database.index,
            llm=self._complex_llm
        )
        self._retrieve_chat_engine = RetrieveChat(
            retriever=self._retriever,
            chat=self._chat_engine,
            preprocess=self._preprocess_engine,
            semantic=self._semantic_engine,
            chat_history_tracker=self._chat_repository,
            max_chat_token=MAX_OUTPUT_TOKENS,
            enhance_chat_engine=self._enhance_chat_engine,
            agent=self._agent_engine,
            rag_classifier=self._rag_classifier_model
        )
        self._file_repository = FileRepository()
        self._general_loader = GeneralLoader()
        self._file_management = FileManagement(
            file_repository=self._file_repository,
            general_loader=self._general_loader,
            vector_database=self._vector_database,
        )

    @property
    def vector_database(self) -> WeaviateDB:
        """
        Retrieves the vector database instance.

        Returns:
            WeaviateDB: The initialized vector database object.
        """
        return self._vector_database

    @property
    def llm(self) -> OpenAI:
        """
        Retrieves the LLM instance.

        Returns:
            OpenAI: The initialized LLM object.
        """
        return self._llm

    @property
    def embed_model(self) -> OpenAIEmbedding:
        """
        Retrieves the embedding model instance.

        Returns:
            OpenAIEmbedding: The initialized embedding model object.
        """
        return self._embed_model

    @property
    def retriever(self) -> HybridRetriever:
        """
        Retrieves the HybridRetriever instance.

        Returns:
            HybridRetriever: The initialized HybridRetriever object.
        """
        return self._retriever

    @property
    def chat_engine(self) -> ChatEngine:
        """
        Retrieves the ChatEngine instance.

        Returns:
            ChatEngine: The initialized ChatEngine object.
        """
        return self._chat_engine

    @property
    def retrieve_chat_engine(self) -> RetrieveChat:
        """
        Retrieves the RetrieveChat instance.

        Returns:
            RetrieveChat: The initialized RetrieveChat object.
        """
        return self._retrieve_chat_engine

    @property
    def chat_repository(self) -> ChatRepository:
        """
        Retrieves the ChatRepository instance.

        Returns:
            ChatRepository: The initialized ChatRepository object.
        """
        return self._chat_repository

    @property
    def file_repository(self) -> FileRepository:
        """
        Retrieves the FileRepository instance.

        Returns:
            FileRepository: The initialized FileRepository object.
        """
        return self._file_repository

    @property
    def general_loader(self) -> GeneralLoader:
        """
        Provides access to the GeneralLoader instance.
        """
        return self._general_loader

    @property
    def file_management(self) -> FileManagement:
        """
        Provides access to the FileManagement instance.
        """
        return self._file_management

    @property
    def suggestion_repository(self) -> SuggestionRepository:
        """
        Provides access to the SuggestionRepository instance.
        """
        return self._suggestion_repository

    @property
    def preprocess_engine(self) -> PreprocessQuestion:
        """
        Provides access to the PreprocessQuestion instance.
        """
        return self._preprocess_engine

    @property
    def semantic_engine(self) -> SemanticSearch:
        """
        Provides access to the SemanticEngine instance.
        """
        return self._semantic_engine

    @property
    def enhance_chat_engine(self) -> EnhanceChatEngine:
        """
        Provides access to the EnhanceChatEngine instance.
        """
        return self._enhance_chat_engine

    @property
    def agent_engine(self) -> AgentEngine:
        """
        Provides access to the AgentEngine instance.
        """
        return self._agent_engine
