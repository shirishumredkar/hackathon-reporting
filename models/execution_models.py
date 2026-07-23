from pydantic import BaseModel

class ConnectionStatus(BaseModel):
    connected: bool
    project: str
    message: str

class DryRunResult(BaseModel):
    valid : bool
    byte_processed : int
    estimated_cost_usd : float
    cache_hit : bool
