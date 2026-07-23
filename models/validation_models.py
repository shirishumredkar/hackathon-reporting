from typing import List
from pydantic import BaseModel

class SQLValidationResult(BaseModel):
    valid : bool
    errors : List[str]
