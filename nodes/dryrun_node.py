import logging
from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowState, WorkflowStatus
from nodes.base_node import BaseNode
logger = logging.getLogger(__name__)

@NodeRegistry.register(WorkflowNode.DRYRUN)
class DryRunNode(BaseNode):
    def __init__(self, services):
        super().__init__(services)
        self.bigquery = services.bigquery
        # Note: CostService seems to be already utilized inside bigquery.dry_run()
        # based on services/bigquery_service.py

    def process(self, state: WorkflowState) -> WorkflowState:
        # Prevent hitting BigQuery if SQL is empty or invalid
        if not state.sql or not state.sql_valid:
            logger.warning(f"Skipping DryRun. SQL is empty or invalid. Errors: {state.validation_errors}")
            state.status = WorkflowStatus.FAILED
            state.error = f"Invalid SQL: {state.validation_errors}"
            return state

        # Call dry_run with the actual SQL string, not the state object
        dryrun_result = self.bigquery.dry_run(state.sql)

        # Update the state with the results
        state.bytes_processed = dryrun_result.byte_processed
        state.estimated_cost_usd = dryrun_result.estimated_cost_usd
        state.status = WorkflowStatus.DRY_RUN_COMPLETE

        return state