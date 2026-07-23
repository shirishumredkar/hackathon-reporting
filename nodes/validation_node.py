from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowState
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.VALIDATION)
class ValidationNode(BaseNode):
    def __init__(self,services):
        super().__init__(services)
        self.validator = services.validator

    def process(self, state : WorkflowState ) -> WorkflowState:
        return self.validator.execute(state)