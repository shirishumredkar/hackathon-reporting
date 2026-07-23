import logging
from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowState, WorkflowStatus
from nodes.base_node import BaseNode
logger = logging.getLogger(__name__)

@NodeRegistry.register(WorkflowNode.EXECUTE)
class ExecuteNode(BaseNode):
    def __init__(self, services):
        super().__init__(services)
        self.bigquery = services.bigquery
        self.csv = services.csv_export

    def process(self, state: WorkflowState) -> WorkflowState:
        # Robustly get session_id and sql whether state is dict or object
        is_dict = isinstance(state, dict)
        session_id = state.get("session_id") if is_dict else getattr(state, "session_id", None)
        sql = state.get("sql") if is_dict else getattr(state, "sql", None)
        logger.info(f"Executing SQL query for session: {session_id}")
        try:
            iterator = self.bigquery.execute_sql(sql)
            rows, path = self.csv.export(iterator)
            if is_dict:
                state["rows_returned"] = rows
                state["csv_path"] = path
                state["status"] = WorkflowStatus.EXECUTED
            else:
                state.rows_returned = rows
                state.csv_path = path
                state.status = WorkflowStatus.EXECUTED
            logger.info(f"Successfully executed query. {rows} rows returned and saved to {path}")
        except Exception as e:
            logger.error(f"Error during SQL execution or CSV Export : {e}", exc_info=True)
            if is_dict:
                state["error"] = str(e)
                state["status"] = WorkflowStatus.FAILED
            else:
                state.error = str(e)
                state.status = WorkflowStatus.FAILED

        return state