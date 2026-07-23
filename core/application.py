from engine.workflow_engine import WorkflowEngine

class Application:

    def __init__(self):
        self.workflow_engine = WorkflowEngine()

app_container = Application()
