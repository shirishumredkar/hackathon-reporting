import logging
import sqlglot
from sqlglot import expressions as exp
from models.validation_models import SQLValidationResult
from models.workflow_state import WorkflowStatus
from services.metadata_service import MetadataService

logger = logging.getLogger(__name__)
class SQLValidator:
    def __init__(self):
        self.metadata = MetadataService()


    def validate(self, sql: str):
        errors = []
        try:
            # Tell sqlglot to explicitly parse BigQuery dialect
            tree = sqlglot.parse_one(sql, read="bigquery")
        except Exception as e:
            logger.warning(f"SQL Syntax Error detected by sqlglot: {e}")
            return SQLValidationResult(
                valid=False,
                errors=[f"Invalid SQL Syntax. Exception: {e}"]
            )

        if not isinstance(tree, exp.Select):
            errors.append(
                "Only Select Statements are allowed."
            )

        blocked = ["INSERT", "UPDATE", "DELETE", "MERGE", "DROP", "ALTER", "TRUNCATE", "CREATE"]
        upper_sql = sql.upper()
        for keyword in blocked:
            if keyword in upper_sql:
                errors.append(
                    f"{keyword} is not allowed."
                )
        return SQLValidationResult(
                valid=len(errors) == 0,
                errors=errors
            )

    def execute(self, state):
        validation = self.validate(state.sql)
        state.sql_valid = validation.valid
        state.validation_errors = validation.errors
        state.status = WorkflowStatus.SQL_VALIDATED

        return state