from models.conversation import ConversationMessage, ConversationContext

class ConversationManager:
    def __init__(self, repository):
        self.repository = repository

    def load(self, session_id):
        context = self.repository.load(session_id)
        if context is None:
            context = ConversationContext(session_id=session_id)
        return context

    def save(self, context):
        self.repository.save(context)

    def add_user_message(self,  context, message):
        context.history.append(ConversationMessage(role="user", message=message))

    def add_assistant_message(self,  context, message):
        context.history.append(ConversationMessage(role="assistant", message=message))