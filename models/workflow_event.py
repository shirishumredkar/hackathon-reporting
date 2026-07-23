from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class EventStatus(str, Enum):
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED  = "FAILED"
    SKIPPED = "SKIPPED"
    PENDING = "PENDING"

class WorkflowEvent(BaseModel):
    node : str
    status : EventStatus
    started_at : datetime
    completed_at : datetime | None = None
    duration_ms : float = 0
    message : str | None = None