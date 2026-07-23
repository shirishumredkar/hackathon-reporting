from engine.workflow_repository import WorkflowRepository

class MemoryWorkflowRepository(WorkflowRepository):

    def __init__(self):
        self.storage = {}

    def save(self,state):
        if isinstance(state,dict):
            session_id = state.get("session_id")
        else:
            session_id = getattr(state,"sesssion_id", None)

        if session_id:
            self.storage[session_id] = state

    def load(self,session_id):
        return self.storage.get(session_id)

    def delete(self,session_id):
        self.storage.pop(session_id, None)