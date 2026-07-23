import logging
from abc import ABC
from abc import abstractmethod
from models.workflow_state import WorkflowState, WorkflowStatus
from datetime import datetime
from models.workflow_nodes import WorkflowNode

logger = logging.getLogger(__name__)

class BaseNode(ABC):

    workflow_node = None

    def __init__(self, services):
        self.audit = services.audit

    def execute(self, state: WorkflowState) -> WorkflowState:
        node_name = self.workflow_node.value if self.workflow_node else "UnknownNode"
        is_dict = isinstance(state, dict)
        session_id = state.get("session_id") if is_dict else getattr(state, "session_id", "Unknown")

        logger.info(f"Executing node: {node_name} for session: {session_id}")

        if is_dict:
            state["current_node"] = node_name
        else:
            state.current_node = node_name

        # We need to make sure the audit service knows how to handle a dict state
        # The audit service appends events, so we must safely fetch them
        events = state.get("events", []) if is_dict else getattr(state, "events", [])
        from models.workflow_event import WorkflowEvent, EventStatus
        event = WorkflowEvent(
            node = node_name,
            status = EventStatus.STARTED,
            started_at = datetime.utcnow()
        )

        if is_dict:
            if "events" not in state:
                state["events"] = []
            state["events"].append(event)
        else:
            if not hasattr(state, "events"):
                state.events = []
            state.events.append(event)

        try:
            logger.debug(f"Starting process logic for node: {node_name}")
            result = self.process(state)

            result_is_dict = isinstance(result, dict)
            result_status = result.get("status") if result_is_dict else getattr(result, "status", None)

            # Check if the node intentionally paused the workflow
            if result_status == WorkflowStatus.WAITING_FOR_APPROVAL or result_status == WorkflowStatus.WAITING_FOR_APPROVAL.value:
                self.audit.pending(event)
                logger.info(f"Node {node_name} paused workflow for approval.")
            else:
                self.audit.success(event)
                logger.info(f"Successfully completed node: {node_name}")

            return result
        except Exception as ex:
            logger.error(f"Error during node execution [{node_name}]: {ex}", exc_info = True)
            self.audit.failed(event, ex)

            if isinstance(state, dict):
                state["error"] = str(ex)
                state["status"] = WorkflowStatus.FAILED
            else:
                state.error = str(ex)
                state.status = WorkflowStatus.FAILED

            return state

    @abstractmethod
    def process(self, state: WorkflowState) -> WorkflowState:
        """
        Each node implement its own business logic
        """
        pass