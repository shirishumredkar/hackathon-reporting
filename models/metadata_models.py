from pydantic import BaseModel

class TableMapping(BaseModel):
    cc_table : str
    dataset: str
    bq_table : str