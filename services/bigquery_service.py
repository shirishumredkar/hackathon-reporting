from google.cloud import bigquery
from config import settings
from models.execution_models import ConnectionStatus, DryRunResult
from models.workflow_state import WorkflowStatus
from services.cost_service import CostService

class BigQueryService:
    def __init__(self):
        self.client = bigquery.Client(
            project=settings.BQ_PROJECT
        )

        self.cost = CostService()

    def check_connection(self):
        try:
            project = self.client.project
            list(self.client.list_datasets())
            return ConnectionStatus(
                connected=True,
                project=project,
                message="Connected Successfully"
            )
        except Exception as ex:
            return ConnectionStatus(
                connected=False,
                project="",
                message=str(ex))

    def dry_run(self, sql: str):

        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False
        )
        job = self.client.query(
            sql, job_config=job_config
        )
        bytes_processed = job.total_bytes_processed
        cost = self.cost.estimate(bytes_processed)
        return DryRunResult(
            valid=True,
            byte_processed=bytes_processed,
            estimated_cost_usd=cost,
            cache_hit=False
        )

    def execute(self, state):
        connection = self.check_connection()
        if not connection.connected:
            state.error = connection.message
            state.status = WorkflowStatus.FAILED
            return state
        state.connected = True
        dry = self.dry_run(state.sql)
        state.bytes_processed = dry.bytes_processed
        state.estimated_cost_usd = dry.estimated_cost_usd
        state.status = WorkflowStatus.WAITING_FOR_APPROVAL
        return state

    def execute_sql(self, sql: str):
        job = self.client.query(sql)
        result = job.result()
        return result