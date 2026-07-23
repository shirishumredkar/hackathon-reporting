from enum import Enum

class WorkflowNode(str, Enum):
    ROUTER = "router"
    INFORMATION = "information"
    TABLE_IDENTIFIER = "table_identifier"
    METADATA = "metadata"
    SQL_GENERATION = "sql_generation"
    VALIDATION = "validation"
    DRYRUN = "dryrun"
    APPROVAL = "approval"
    EXECUTE = "execute"
    CSV_EXPORT = "csv_export"