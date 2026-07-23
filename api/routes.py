import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse, RedirectResponse
from uuid_utils import uuid4
from datetime import datetime
import json


from agents.router_agent import RouterAgent
from agents.information_agent import InformationAgent
from agents.query_agent import QueryAgent
from models.router_models import ChatRequest
from models.workflow_state import WorkflowState, WorkflowStatus
from core.application import app_container


logger = logging.getLogger(__name__)
router = APIRouter()
router_agent = RouterAgent()
information_agent = InformationAgent()
query_agent = QueryAgent()


@router.get("/health")
def health():
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy"
    }


class BasicChatRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request.query}")
    try:
        routing = router_agent.route(request.query)
        logger.debug(f"Routing result: {routing}")
        return routing
    except Exception as e:
        logger.error(msg=f"Error in /chat endpoint: {e}", exc_info=True)
        raise


@router.post("/information")
def information(request: ChatRequest):
    logger.info(f"Received information request: {request.query}")
    try:
        routing = information_agent.answer(request.query)
        logger.debug(f"Information result: {routing}")
        return routing
    except Exception as e:
        logger.error(msg=f"Error in /information endpoint: {e}", exc_info=True)
        raise


@router.post("/query")
def query(request: ChatRequest):
    logger.info(f"Received query request: {request.query}")
    try:
        routing = query_agent.execute(request.query)
        logger.debug(f"Query result: {routing}")
        return routing
    except Exception as e:
        logger.error(f"Error in /query endpoint: {e}", exc_info=True)
        raise


@router.post("/workflow/start")
def start(request: ChatRequest):
    logger.info(f"Starting workflow for request: {request.query}")
    state = WorkflowState(
        session_id=str(uuid4()),
        user_query=request.query
    )
    logger.debug(f"Created workflow state with session_id: {state.session_id}")
    try:
        result = app_container.workflow_engine.start(state)
        logger.info(f"Workflow {state.session_id} started successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}", exc_info=True)
        raise


@router.get("/workflow/{session_id}")
def status(session_id: str):
    logger.debug(f"Checking status for workflow: {session_id}")
    try:
        state = app_container.workflow_engine.get_state(session_id)
        if not state:
            logger.warning(f"Workflow {session_id} not found")
        return state
    except Exception as e:
        logger.error(f"Error retrieving workflow status for {session_id}: {e}", exc_info=True)
        raise


class ApprovalRequest(BaseModel):
    approved: bool


@router.post("/workflow/{session_id}/approve")
def approve(session_id: str, request: ApprovalRequest):
    logger.info(f"Received approval update for workflow: {session_id}. Approved: {request.approved}")
    try:
        # Fetch existing state
        state_data = app_container.workflow_engine.get_state(session_id)
        if not state_data:
            raise HTTPException(status_code=404, detail="Workflow not found")
            # Robustly extract the status whether it's a dict or an object
        is_dict = isinstance(state_data, dict)
        current_status = state_data.get("status") if is_dict else getattr(state_data, "status", None)
        # If it's an Enum, get the string value
        if hasattr(current_status, "value"):
            current_status = current_status.value
        if not current_status:
            current_status = "UNKNOWN"
        if current_status != "WAITING_FOR_APPROVAL":
            raise HTTPException(status_code=400,
                                detail=f"Workflow is not awaiting approval. Current Status: {current_status}")

        # Update the state robustly
        if is_dict:
            state_data["approved"] = request.approved
            events_list = state_data.get("events", [])
            if "events" not in state_data:
                state_data["events"] = events_list
        else:
            setattr(state_data, "approved", request.approved)
            events_list = getattr(state_data, "events", [])

        # We need to find the PENDING approval event and update it to SUCCESS/REJECTED
        for event in reversed(events_list):
            event_is_dict = isinstance(event, dict)
            node_name = event.get("node") if event_is_dict else getattr(event, "node", None)
            node_status = event.get("status") if event_is_dict else getattr(event, "status", None)

            # Extract string if status is an enum
            if hasattr(node_status, "value"):
                node_status = node_status.value

            if node_name == "approval" and node_status == "PENDING":
                new_status = "SUCCESS" if request.approved else "REJECTED"
                if event_is_dict:
                    event["status"] = new_status
                    event["message"] = "Human approval action received."
                    event["completed_at"] = datetime.utcnow().isoformat()
                else:
                    setattr(event, "status", new_status)
                    setattr(event, "message", "Human approval action received.")
                    setattr(event, "completed_at", datetime.utcnow().isoformat())
                break
        # Resume the workflow using the engine
        result = app_container.workflow_engine.resume(session_id, updated_state=state_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(msg=f"Error approving workflow {session_id}: {e}", exc_info=True)
        raise


@router.get("/download/{session_id}")
def download(session_id: str):
    logger.info(f"Download requested for workflow: {session_id}")
    try:
        state = app_container.workflow_engine.get_state(session_id)
        if not state:
            logger.warning(f"File not found for workflow: {session_id}")
            return {"error": "File not found"}
        # Safely handle the state depending on if it's a dict or an object
        csv_path = state.get("csv_path") if isinstance(state, dict) else getattr(state, "csv_path", None)
        if csv_path:
            logger.debug(f"Returning file: {csv_path}")
            return FileResponse(csv_path)
        logger.warning(f"File not found for workflow: {session_id}")
        return {"error": "File not found"}
    except Exception as e:
        logger.error(msg=f"Error downloading file for {session_id}: {e}", exc_info=True)
        raise
