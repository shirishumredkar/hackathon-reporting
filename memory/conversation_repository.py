from abc import ABC
from abc import abstractmethod

class ConversationRepository(ABC):

    @abstractmethod
    def save(self, context):
        pass

    @abstractmethod
    def load(self, session_id):
        pass

    @abstractmethod
    def delete(self, session_id):
        pass

class MemoryConversationRepository(ConversationRepository):

    def __init__(self):
        self.storage = {}

    def save(self, context):
        self.storage[context.session_id] = context

    def load(self, session_id):
        return self.storage.get(session_id)

    def delete(self, session_id):
        self.storage.pop(session_id, None)