#########################
# Importing the Libraries
###########################################################
import uuid
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
###########################################################
# A Class to chunk out the docs & load it into BQ Vector Database
###########################################################
class DocumentProcessor:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
        chunk_size=self.chunk_size,
        chunk_overlap=self.chunk_overlap
    )

    def chunk_documents(self, docs: list[Document], gcs_uri: str) -> list[Document]:
        logging.info("Splitting documents into chunks...")
        doc_id = str(uuid.uuid4())
        chunks = self.splitter.split_documents(docs)
        processed_docs = []
        for i, chunk in enumerate(chunks):
            processed_docs.append(
                Document(
                    page_content=chunk.page_content,
                    metadata={
                        "DOC_ID": doc_id,
                        "CHUNK_ID": str(i),
                        "SOURCE_FILE" : gcs_uri,
                        "GCS_URI" : gcs_uri,
                        "PAGE" : int(chunk.metadata.get("page",0))
                    }
                )
            )

        return processed_docs
