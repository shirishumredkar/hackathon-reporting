from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_community import BigQueryVectorStore
from config import settings
from unittest.mock import patch
from google.cloud import bigquery as bq


class VectorSearchService:
    def __init__(self):
        self.project_id = settings.PROJECT_ID
        self.location = settings.LOCATION
        self.dataset_name = settings.BQ_DATASET
        self.table_name = settings.TABLE_NAME
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self._vector_store = None

    def _get_embedding_model(self):
        return VertexAIEmbeddings(
            model_name=self.embedding_model_name,
            project=self.project_id,
            location=self.location,
            max_retries=3,
        )

    def get_vector_store(self) -> BigQueryVectorStore:
        if self._vector_store is None:
            # Ensure required variables are non-empty
            if not self.project_id or not self.dataset_name:
                raise ValueError(
                    f"Invalid BigQuery config: project_id='{self.project_id}', "
                    f"dataset_name='{self.dataset_name}'. Check your .env file."
                )

            embedding = self._get_embedding_model()

            with patch(
                    "langchain_google_community.bq_storage_vectorstores._base.check_bq_dataset_exists"
            ) as mock_dataset_check, patch(
                "google.cloud.bigquery.client.Client.create_table"
            ) as mock_create_table:
                mock_dataset_check.return_value = True
                mock_create_table.return_value = None

                self._vector_store = BigQueryVectorStore(
                    project_id=self.project_id,
                    dataset_name=self.dataset_name,
                    table_name=self.table_name,
                    location=self.location,
                    embedding=embedding,
                    content_field="CONTENT",
                    embedding_field="EMBEDDING",
                )
                self._vector_store._bq_client = bq.Client(
                    project=self.project_id,
                    location=self.location
                )
        return self._vector_store