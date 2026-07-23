from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowState
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.METADATA)
class MetadataNode(BaseNode):
    def __init__(self,services):
        super().__init__(services)
        self.metadata = services.metadata

    def process(self, state):
        return self.metadata.execute(state)