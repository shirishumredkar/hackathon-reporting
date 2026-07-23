from pydantic import BaseModel
from enum import Enum

class RouteType(str, Enum):
    INFORMATION = "INFORMATION"
    QUERY = "QUERY"

class RouterResponse(BaseModel):
    route : RouteType
    confidence : float
    reason : str

class ChatRequest(BaseModel):
    query : str