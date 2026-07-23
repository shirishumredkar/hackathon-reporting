from datetime import datetime
from models.workflow_event import WorkflowEvent, EventStatus

class AuditService:
    def start(self, state, node):
        event = WorkflowEvent(
            node = node,
            status = EventStatus.STARTED,
            started_at = datetime.utcnow() )
        state.events.append(event)
        return event

    def success(self, event):
        event.status = EventStatus.SUCCESS
        event.completed_at = datetime.utcnow()
        event.duration_ms = (event.completed_at - event.started_at).total_seconds() * 1000

    def failed(self, event, error):
        event.status = EventStatus.FAILED
        event.completed_at = datetime.utcnow()
        event.duration_ms = (event.completed_at - event.started_at).total_seconds() * 1000

    def pending(self, event):
        event.status = EventStatus.PENDING
        event.completed_at = datetime.utcnow()
        event.duration_ms = (event.completed_at - event.started_at).total_seconds() * 1000