from pydantic import BaseModel

class InformationResponse(BaseModel):
    answer : str
    grounded : bool
    source : str