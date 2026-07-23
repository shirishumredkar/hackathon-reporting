from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowState, WorkflowStatus
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.CSV_EXPORT)
class CsvExportNode(BaseNode):

    def process(self, state: WorkflowState) -> WorkflowState:
        if isinstance(state, dict):
            state["status"] = WorkflowStatus.COMPLETED
        else:
            state.status = WorkflowStatus.COMPLETED

        return state