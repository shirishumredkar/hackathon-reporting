import logging

from langchain_classic.chains import RetrievalQA
from langchain_google_vertexai import ChatVertexAI
from config import settings
from prompts import information_prompt
from services.vector_search_service import  VectorSearchService

class VertexSearchService:

    def __init__(self):
        self.bq_manager = VectorSearchService()
        self.project_id = settings.PROJECT_ID
        self.location   = settings.LOCATION
        self.llm_model  = settings.MODEL_NAME
        self.llm_temperature = settings.TEMPERATURE
        self.instructions = information_prompt.SYSTEM_PROMPT
        self._qa_chain = None

    def _initialize_qa_chain(self):
        logging.info("Initializing QA Chain")
        vector_store = self.bq_manager.get_vector_store()
        llm_kwargs = {}
        if self.instructions:
            llm_kwargs["system_instruction"] = self.instructions
        llm = ChatVertexAI(
            model_name=self.llm_model,
            temperature=self.llm_temperature,
            project=self.project_id,
            location=self.location,
            transport="rest",
            **llm_kwargs
        )

        retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )

        self._qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever
        )

    def search(self, query: str) -> str:
        logging.info(f"Processing query: '{query}'")
        if self._qa_chain is None:
            self._initialize_qa_chain()
        logging.info("Searching Vector Database and generating response ...")
        response = self._qa_chain.invoke({"query": query})
        return response["result"]
