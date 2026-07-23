import logging
from agents.sql_generator import SQLGenerator
from services.metadata_service import MetadataService
from models.query_models import SQLGenerationResponse

logger = logging.getLogger(__name__)


class QueryAgent:

    def __init__(self):
        self.metadata = MetadataService()
        self.generator = SQLGenerator()

    def execute(self, user_query: str) -> SQLGenerationResponse:
        query_upper = user_query.upper()

        # 1. Fetch all available keys from table_mapping.json
        all_tables = self.metadata.get_all_tables()
        matched_tables = []

        # 2. Match keys against the user query (case-insensitive)
        for table_key in all_tables.keys():
            if table_key in query_upper:
                matched_tables.append(table_key)

        # Fallback: If no table name was mentioned in the query, pass all mapped tables
        if not matched_tables:
            logger.info("No specific table key matched in query string. Defaulting to all configured tables.")
            matched_tables = list(all_tables.keys())

        # 3. Retrieve TableMapping objects via MetadataService
        table_mappings = []
        datasets = set()

        for table_key in matched_tables:
            mapping = self.metadata.get_mapping(table_key)
            if mapping:
                table_mappings.append({
                    "cc_table": mapping.cc_table,
                    "dataset": mapping.dataset,
                    "bq_table": mapping.bq_table
                })
                datasets.add(mapping.dataset)
            else:
                logger.warning(f"No BigQuery mapping found for key: '{table_key}'")

        if not table_mappings:
            raise Exception("No valid BigQuery table mappings could be resolved from table_mapping.json.")

        # 4. Generate SQL using the metadata context
        metadata_context = {
            "tables": table_mappings
        }

        sql_result = self.generator.generate(user_query, metadata_context)

        return SQLGenerationResponse(
            cc_tables=matched_tables,
            datasets=list(datasets),
            sql=sql_result.get("sql", ""),
            explanation=sql_result.get("explanation", "")
        )