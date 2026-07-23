from pydantic import BaseModel

class ExecutionResult(BaseModel):
    rows: int
    csv_path: str
    execution_time: float
    byte_processed: int
    success: bool
    message : str
