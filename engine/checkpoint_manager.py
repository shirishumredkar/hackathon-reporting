from engine.memory_repository import MemoryWorkflowRepository

class CheckpointManager:

    def __init__(self):
        self.repository = MemoryWorkflowRepository()

    def checkpoint(self,state):
        self.repository.save(state)

    def restore(self, session_id):
        return self.repository.load(session_id)

    def clear(self,session_id):
        self.repository.delete(session_id)
