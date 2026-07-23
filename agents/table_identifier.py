import json
import logging
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from config import settings
from models.workflow_state import WorkflowStatus
from prompts.table_identifier_prompt import TABLE_IDENTIFIER_PROMPT
from services.vertex_search_service import VertexSearchService
from models.table_models import TableIdentificationResponse, IdentifiedTable

logger = logging.getLogger(__name__)


class TableIdentifier:

    def __init__(self):
        self.search_service = VertexSearchService()
        self.llm = ChatVertexAI (
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE
        )

    def identify(self,user_query : str):
        logger.info("Fetching candidate metadata from Vertex Search ...")
        candidates = self.search_service.search(user_query)

        prompt = f"""
                   {TABLE_IDENTIFIER_PROMPT}
                   Candidate Metadata {candidates}
                   User Query {user_query}
                  """

        logger.info("Calling LLM to identify tables ...")
        response = self.llm.invoke([HumanMessage(content=prompt)])

        text = response.text.strip()

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        data = json.loads(text)

        tables = [
            IdentifiedTable(**table)
            for table in data["tables"]
        ]

        return TableIdentificationResponse(
            tables=tables
        )

    def execute(self,state):
        identified_response = self.identify(state.user_query)
        state.cc_tables = [table.cc_table for table in identified_response.tables]
        state.status = WorkflowStatus.IDENTIFIED
        return state
