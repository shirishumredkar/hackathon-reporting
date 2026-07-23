import os
from pathlib import Path
from google.cloud import storage
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_community import BigQueryVectorStore

# Load global configuration
import sys
from pathlib import Path

# Add project root directory to Python search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now import settings safely
from config import settings

# Paths & Inputs
LOCAL_FILE_PATH = settings.LOCAL_FILE_PATH
BUCKET_NAME = settings.BUCKET_NAME


def upload_to_gcs(local_path: str, bucket_name: str) -> str:
    """Uploads the local PDF to GCS for persistence and tracking."""
    file_path = Path(local_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Local PDF file not found at: {file_path}")

    storage_client = storage.Client(project=settings.PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)

    blob_name = f"pdf_documents/{file_path.name}"
    blob = bucket.blob(blob_name)

    print(f"Uploading {file_path.name} to gs://{bucket_name}/{blob_name}...")
    blob.upload_from_filename(str(file_path))

    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    print(f"File uploaded successfully to {gcs_uri}")
    return gcs_uri


def process_and_store_pdf():
    # 1. Upload file to GCS
    gcs_uri = upload_to_gcs(LOCAL_FILE_PATH, BUCKET_NAME)



    # 2. Extract Text from PDF
    print("Extracting text from PDF...")
    loader = PyPDFLoader(LOCAL_FILE_PATH)
    documents = loader.load()

    # 3. Chunk Document
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)

    # 4. Clean Metadata to match BigQuery schema
    print("Sanitizing metadata...")
    for chunk in chunks:
        # Retain only standard/known metadata keys that exist in your BQ schema
        chunk.metadata = {
            "source": Path(LOCAL_FILE_PATH).name,
            "page": chunk.metadata.get("page", 0),
            "gcs_path": gcs_uri
        }

    print(f"Created {len(chunks)} cleaned chunks from PDF.")

    # 5. Initialize BigQuery Vector Store
    print(f"Connecting to BigQuery Vector Store ({settings.BQ_DATASET}.{settings.TABLE_NAME})...")

    embedding_model = VertexAIEmbeddings(
        model_name=settings.EMBEDDING_MODEL,  # e.g., "text-embedding-004"
        project=settings.PROJECT_ID,
        location=settings.LOCATION
    )
    vector_store = BigQueryVectorStore(
        project_id=settings.PROJECT_ID,
        dataset_name=settings.BQ_DATASET,
        table_name=settings.TABLE_NAME,
        location=settings.LOCATION,
        embedding=embedding_model
    )

    # 6. Embed and Write Chunks to BigQuery
    print("Generating embeddings and inserting into BigQuery...")
    vector_store.add_documents(chunks)
    print(f"Successfully loaded {len(chunks)} chunks into {settings.TABLE_NAME}!")


if __name__ == "__main__":
    process_and_store_pdf()