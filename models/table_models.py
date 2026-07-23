from typing import List
from pydantic import BaseModel, ConfigDict, model_validator, Field


class IdentifiedTable(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    cc_table: str = Field(alias="cc_table")
    confidence: float

    @model_validator(mode="before")
    @classmethod
    def _normalize_table_key(cls, data):
        if isinstance(data, dict):
            # Accept any of these keys from the LLM and map them to cc_table
            for alt in ("cc_tables", "table", "table_name"):
                if alt in data and "cc_table" not in data:
                    data["cc_table"] = data.pop(alt)
                    break
        return data


class TableIdentificationResponse(BaseModel):
    tables: List[IdentifiedTable]