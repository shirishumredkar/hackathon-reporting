from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.TABLE_IDENTIFIER)
class TableIdentifierNode(BaseNode):
    def __init__(self,services):
        super().__init__(services)
        self.agent = services.table_identifier

    def process(self, state):
        return self.agent.execute(state)