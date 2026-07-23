# Importing the Libraries

from unittest.mock import patch
import google.cloud.bigquery as bq
from langchain_google_community import BigQueryVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from config import settings

# A class to initialize the vector for query searching
class BigQueryVectorStoreManager:
    def __init__(self):
        self.project_id = settings.PROJECT_ID
        self.location = settings.LOCATION
        self.dataset_name = settings.BQ_DATASET
        self.table_name = settings.TABLE_NAME
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self.vector_store = None

    def _get_embedding_model(self):
        return VertexAIEmbeddings(
            model_name=self.embedding_model_name,
            project=self.project_id,
            location=self.location,
            max_retries=3
        )

    def get_vector_store(self) -> BigQueryVectorStore:
        """Initializes and returns the BigQuery Vector Store."""
        if self.vector_store is None:
            embedding = self._get_embedding_model()
            with patch(
                    "langchain_google_community.bq_storage_vectorstores._base.check_bq_dataset_exists") as mock_dataset_check, \
                    patch("google.cloud.bigquery.client.Client.create_table") as mock_create_table:
                mock_dataset_check.return_value = True
                mock_create_table.return_value = None
                self._vector_store = BigQueryVectorStore(
                    project_id=self.project_id,
                    dataset_name=self.dataset_name,
                    table_name=self.table_name,
                    location=self.location,
                    embedding=embedding,
                    content_field="CONTENT",
                    embedding_field="EMBEDDING"
                )
                self._vector_store._bq_client = bq.Client(project=self.project_id, location=self.location)
        return self._vector_store
