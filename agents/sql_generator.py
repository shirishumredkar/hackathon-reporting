import json
import logging
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from config import settings
from models.workflow_state import WorkflowStatus
from prompts.sql_prompt import SQL_PROMPT


logger = logging.getLogger(__name__)

class SQLGenerator:

    def __init__(self):
        self.llm = ChatVertexAI (
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE
        )

    def generate(self,user_query,metadata):
        prompt = f"""
                   {SQL_PROMPT}
                   Available Metadata {metadata}
                   User Request {user_query}
                    """

        logger.info("Calling VertexAI for SQL Geenration  ...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        text = response.text.strip()

        logger.debug(f"RAW LLM SQL Response: {text}")

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SQL JSON. Raw test: {text}", exc_info=True)
            raise

    def execute(self, state):
        result = self.generate(state.user_query,
                               state.metadata)
        state.sql = result["sql"]
        state.sql_explanation = result["explanation"]
        state.status = WorkflowStatus.SQL_GENERATED
        return state
