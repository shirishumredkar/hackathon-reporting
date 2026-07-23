from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from models.workflow_event import WorkflowEvent


class WorkflowStatus(str, Enum):
    STARTED = "STARTED"
    ROUTED = "ROUTED"
    IDENTIFIED = "IDENTIFIED"
    METADATA_LOADED = "METADATA_LOADED"
    SQL_GENERATED = "SQL_GENERATED"
    SQL_VALIDATED = "SQL_VALIDATED"
    DRY_RUN_COMPLETE = "DRY_RUN_COMPLETE"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    EXECUTED = "EXECUTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowState(BaseModel):
    # ---- ADD THESE TWO ----
    user_query: Optional[str] = None          # input from the user (read by RouterAgent)
    route: Optional[str] = None               # routing decision (INFORMATION / QUERY), written by RouterAgent
    # -----------------------

    documentation_answer: str | None = None
    cc_tables: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    sql: str | None = None
    sql_explanation: str | None = None
    sql_valid: bool = False
    validation_errors: list[str] = Field(default_factory=list)
    connected: bool = False
    bytes_processed: int = 0
    estimated_cost_usd: float = 0.0
    approved: bool = False
    rows_returned: int = 0
    csv_path: str | None = None
    dataframe_preview: list[dict] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.STARTED
    error: str | None = None
    current_node: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = False
    download_url: str | None = None
    execution_time: float = 0
    bytes_billed: int = 0
    events: list[WorkflowEvent] = Field(default_factory=list)
    conversation: Optional[Any] = None        # was `None` (invalid annotation)
    session_id: Optional[str] = None