from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowStatus
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.INFORMATION)
class InformationNode(BaseNode):
    def __init__(self, services):
        super().__init__(services)
        self.agent = services.information

    def process(self, state):
        result = self.agent.answer(state.user_query)
        state.documentation_answer = result.answer

        # Ensure state reflects that the workflow has finished
        state.completed = True
        state.status = WorkflowStatus.COMPLETED

        return state