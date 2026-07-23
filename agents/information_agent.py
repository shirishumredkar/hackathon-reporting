import logging
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings
from services.vertex_search_service import VertexSearchService
from prompts.information_prompt import SYSTEM_PROMPT
from models.information_models import InformationResponse

logger = logging.getLogger(__name__)
class InformationAgent:

    def __init__(self):
        self.llm = ChatVertexAI (
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE
        )

        self.vertexSearchService = VertexSearchService()

    def answer(self, query : str):
        logger.debug(f"Inside Information Agent: {query}")
        document = self.vertexSearchService.search(query)
        logger.debug(f"Docuemnt: {document}")
        if document is None:
            return InformationResponse(
                answer="I Couldn't find the answer in Product Documentation",
                grounded=False,
                source=""
            )
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"""
                                    Docuemntation : {document}
                                    Question : {query}
                                    """) ]
        response = self.llm.invoke(messages)
        return InformationResponse (
            answer = response.content,
            grounded=True,
            source="PRODUCT DOCUMENT PDF"
        )



