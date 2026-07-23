import json
import vertexai
from vertexai.generative_models import GenerativeModel
from models.router_models import RouterResponse
from models.workflow_state import WorkflowState, WorkflowStatus
from prompts.router_prompt import ROUTER_PROMPT
from config import settings
import logging
import google.auth

logger = logging.getLogger(__name__)

class RouterAgent:
    def __init__(self):
        #credentials, project_id = google.auth.default()
        #vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION, api_transport=settings.API_TRANSPORT, credentials=credentials)
        self.model = GenerativeModel(model_name=settings.MODEL_NAME)

    def route(self, user_query: str) -> RouterResponse:
        prompt = f""" {ROUTER_PROMPT}
                      User Query: {user_query}
                  """
        try:
            logger.info("Calling vertexai generate_content ...")
            response = self.model.generate_content(prompt)
            logger.info("Received response from vertexai.")
            text = response.text.strip()

            if text.startswith("```json"):
                text = text [7:]
            if text.startswith("```"):
                text = text [3:]
            if text.endswith("```"):
                text = text[:-3]

            data = json.loads(text.strip())

            if "routes" in data and "route" not in data:
                data["route"] = data.pop("routes")

            return RouterResponse(**data)
        except Exception as ex:
            logger.error(f"Error in RouterAgent: {str(ex)}")
            raise Exception(
                f" Router agent failed. Oringinal error: {str(ex)}"
            ) from ex

    def execute(self, state: WorkflowState):
        result=self.route(state.user_query)
        state.route=result.route
        state.status = WorkflowStatus.ROUTED
        return state