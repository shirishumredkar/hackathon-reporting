from datetime import datetime
from pydantic import BaseModel, Field

class ConversationMessage(BaseModel):
    role : str
    message : str
    timestamp : datetime = Field(default_factory=datetime.utcnow)

class ConversationContext(BaseModel):
    session_id : str
    history : list[ConversationMessage] = Field(default_factory=list)
    previous_sql : str | None = None
    previous_tables : list[str] = Field(default_factory=list)
    previous_metadata: dict = Field(default_factory=dict)
    last_result_rows: int = 0