import json
from pathlib import Path
from models.metadata_models import TableMapping
from models.workflow_state import WorkflowStatus

class MetadataService:
    def __init__(self):
        root = Path(__file__).parent.parent
        with open(root / "data" / "table_mapping.json", "r") as f:
            self.mapping = json.load(f)

    def get_mapping(self, cc_table: str):
        key = cc_table
        if key not in self.mapping:
            return None
        # Fixed: mapping is a dictionary, use square brackets to access it, not parentheses
        mapping_dict = self.mapping[key]

        return TableMapping(
            cc_table=key,
            dataset=mapping_dict["dataset"],
            bq_table=mapping_dict["table"]
        )

    def get_all_tables(self):
        return self.mapping

    def execute(self, state):
        metadata = {}
        for table in state.cc_tables:
            metadata[table] = self.get_mapping(table)
        state.metadata = metadata
        state.status = WorkflowStatus.METADATA_LOADED
        return state