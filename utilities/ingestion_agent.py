###############################################################################
# Importing the Libraries
###############################################################################

import time
from datetime import datetime, timezone
import google.cloud.bigquery as bq
import logging
from utilities.bq_vector_store import BigQueryVectorStoreManager
from utilities.gcs_tool import GCSService
from utilities.document_processor_tool import DocumentProcessor
from config import settings

###############################################################################
# A class managing An agent orchestrator responsible for ingesting files into the Vector Database.
###############################################################################

class IngestionAgent:
    def __init__(self):
        self.project_id = settings.PROJECT_ID
        self.bucket_name = settings.BUCKET_NAME
        self.chunk_size = int(settings.CHUNK_SIZE)
        self.chunk_overlap = int(settings.CHUNK_OVERLAP)
        self.batch_size = int(settings.BATCH_SIZE)
        self.gcs_service = GCSService(self.project_id, self.bucket_name)
        self.doc_processor = DocumentProcessor(self.chunk_size, self.chunk_overlap)
        self.bq_manager = BigQueryVectorStoreManager()
        self.local_pdf_path = settings.LOCAL_FILE_PATH
        self.gcs_uri = settings.GCS_URI

    def run(self):
        gcs_uri = self.gcs_uri
        local_pdf_path = self.local_pdf_path
        if not gcs_uri and local_pdf_path:
            gcs_uri = self.gcs_service.upload_pdf_to_gcs(local_pdf_path)

        if not gcs_uri:
            raise ValueError("Either local_pdf_path or gcs_uri must be provided")
        #uri_parts = gcs_uri.replace(old="gs://", new="").split(sep="/", maxsplit=1)
        uri_parts = self.gcs_uri.replace("gs://", "").split("/", 1)
        if len(uri_parts) > 1:
            blob_name = uri_parts[1]
        else:
            logging.error(f"Invalid GCS URI format: {gcs_uri}")
            return "Failed"


        docs = self.gcs_service.download_and_parse_pdf(blob_name)
        processed_docs = self.doc_processor.chunk_documents(docs, gcs_uri)
        vector_store = self.bq_manager.get_vector_store()
        logging.info(f"Loading {len(processed_docs)} chunks into BigQuery...")
        bq_client = bq.Client(project=self.bq_manager.project_id, location=self.bq_manager.location)
        table_id = f"{self.bq_manager.project_id}.{self.bq_manager.dataset_name}.{self.bq_manager.table_name}"

        for i in range(0, len(processed_docs), self.batch_size):
            batch = processed_docs[i:i + self.batch_size]
            logging.info(f"Processing batch {i // self.batch_size + 1} ({len(batch)} chunks)...")
            texts = [doc.page_content for doc in batch]
            embeddings = vector_store.embedding.embed_documents(texts)
            records = []
            current_timestamp = datetime.now(timezone.utc).isoformat()
            for doc, emb in zip(batch, embeddings):
                record = {
                    "CONTENT": doc.page_content,
                    "EMBEDDING": emb,
                    "CREATED_AT": current_timestamp
                }
                record.update(doc.metadata)
                records.append(record)

            if records:
                errors = bq_client.insert_rows_json(table_id, records)
                if errors:
                    logging.error(f"Errors occured during streaming insert: {errors}")
            time.sleep(1.5)

        return "Success"
