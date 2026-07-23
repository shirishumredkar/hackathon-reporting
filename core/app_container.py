from workflows.workflow_builder import WorkflowBuilder
from engine.workflow_engine import WorkflowEngine
from core.service_registry import ServiceRegistry


class AppContainer:

    def __init__(self):
        self.services = (ServiceRegistry())
        self.workflow_builder = (WorkflowBuilder(self.services))
        self.graph = (self.workflow_builder.build())
        self.workflow_engine = (WorkflowEngine(self.graph))


container = AppContainer()