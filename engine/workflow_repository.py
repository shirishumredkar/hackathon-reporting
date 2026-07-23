from abc import ABC
from abc import abstractmethod
from models.workflow_state import WorkflowState

class WorkflowRepository(ABC):
    @abstractmethod
    def save(self, state: WorkflowState):
        pass

    @abstractmethod
    def load(self,session_id: str) -> WorkflowState:
        pass

    @abstractmethod
    def delete(self,session_id: str):
        pass