import logging
import time
from models.workflow_state import WorkflowState
from workflows.workflow_builder import WorkflowBuilder
from engine.checkpoint_manager import CheckpointManager

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self):
        logger.debug("Initializing WorkflowEngine")
        self.graph = WorkflowBuilder().build()
        self.checkpoints = CheckpointManager()
        logger.info("WorkflowEngine initialized successfully")

    def start(self, state):
        logger.info(f"Starting workflow graph execution for session_id: {state.session_id}")
        start_time = time.time()
        try:
            result = self.graph.invoke(state)

            end_time = time.time()
            execution_time = end_time - start_time

            if isinstance(result, dict):
                result["execution_time"] = execution_time
            else:
                result.execution_time = execution_time

            self.checkpoints.checkpoint(result)
            logger.info(f"Workflow execution completed for session_id: {state.session_id} in {execution_time}")
            return result
        except Exception as e:
            logger.error(f"Error executing workflow graph: {e}", exc_info = True)
            raise

    def resume(self, session_id: str, updated_state=None):
        logger.info(f"Resuming workflow for session_id: {session_id}")
        start_time = time.time()
        try:
            state_to_process = updated_state
            if state_to_process is None:
                state_to_process = self.checkpoints.restore(session_id)

            if state_to_process is None:
                logger.error(f"Workflow not found for session_id: {session_id}")
                raise Exception("Workflow not found")

            # Convert the dictionary to a Pydantic model before invoking the graph
            if isinstance(state_to_process, dict):
                # Ensure events are treated properly before conversion
                state_model = WorkflowState(**state_to_process)
            else:
                state_model = state_to_process  # It's already a model.

            logger.debug(f"State restored for {session_id}, invoking graph...")
            result = self.graph.invoke(state_model)

            end_time = time.time()
            new_execution_time = end_time - start_time

            if isinstance(result, dict):
                # Ensure events are treated properly before conversion
                state_model = WorkflowState(**state_to_process)
            else:
                state_model = state_to_process  # It's already a model

            logger.debug(f"State restored for {session_id}, invoking graph...")
            result = self.graph.invoke(state_model)

            end_time = time.time()
            new_execution_time = end_time - start_time

            if isinstance(result, dict):
                existing_time = result.get("execution_time", 0)
                result["execution_time"] = existing_time + new_execution_time
            else:
                existing_time = getattr(result, "execution_time", 0)
                result.execution_time = existing_time + new_execution_time

            self.checkpoints.checkpoint(result)
            logger.info(f"Workflow resumed and completed for session_id: {session_id} in {new_execution_time}")
            return result
        except Exception as e:
            logger.error( f"Error resuming workflow {session_id}: {e}", exc_info = True)
            raise


    def get_state(self, session_id):
        logger.debug(f"Fetching state for session_id: {session_id}")
        return self.checkpoints.restore(session_id)