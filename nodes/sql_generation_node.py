from core.node_registry import NodeRegistry
from models.workflow_nodes import WorkflowNode
from models.workflow_state import WorkflowStatus
from nodes.base_node import BaseNode

@NodeRegistry.register(WorkflowNode.SQL_GENERATION)
class SQLGeneratorNode(BaseNode):
    def __init__(self,services):
        super().__init__(services)
        self.sql_generator = services.sql_generator

    def process(self, state):
        sql = self.sql_generator.generate(state.user_query,state.metadata)
        state.sql = sql ["sql"]
        state.sql_explanation = (sql["explanation"])
        state.status = WorkflowStatus.SQL_GENERATED
        return state