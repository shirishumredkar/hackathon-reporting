###############################################################################
# Importing the Libraries
###############################################################################

import os
import logging
from google.cloud import storage
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader


###############################################################################
# A Class to
# a. load the local file to GCS Bucket
# b. parse the file into chunks for loading to Vector DB
###############################################################################
class GCSService:
    def __init__(self, project_id: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    def upload_pdf_to_gcs(self, local_path: str) -> str:
        filename = os.path.basename(local_path)
        destination_blob_name = filename
        blob = self.bucket.blob(destination_blob_name)
        gcs_uri = f"gs://{self.bucket_name}/{destination_blob_name}"
        if blob.exists():
            logging.info(f"File '{filename}' already exists in GCS. Skipping upload.")
            return gcs_uri
        logging.info(f"Uploading '{filename}' to GCS...")
        blob.upload_from_filename(local_path)
        logging.info("Upload complete!")
        return gcs_uri

    def download_and_parse_pdf(self, blob_name: str) -> list[Document]:
        logging.info("Downloading and parsing PDF...")
        temp_pdf_path = f"temp_{blob_name.replace('/', '_')}"
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(temp_pdf_path)
        loader = PyPDFLoader(temp_pdf_path)
        docs = loader.load()
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        return docs
