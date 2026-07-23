from pydantic import BaseModel
from typing import List

class SQLGenerationResponse(BaseModel):
    cc_tables : List[str]
    datasets : List[str]
    sql : str
    explanation : str
