from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowState, WorkflowStatus
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.APPROVAL)
class ApprovalNode(BaseNode):
    def __init__(self,services):
        super().__init__(services)

    def process(self, state: WorkflowState) -> WorkflowState:
        # If the state has already been approved (e.g. by the API endpoint before resuming),
        # we should immediately pass it forward rather than setting it to waiting again.
        if state.approved:
            # We don't alter the status here, allowing the graph to proceed
            return state

        state.status = WorkflowStatus.WAITING_FOR_APPROVAL
        return state