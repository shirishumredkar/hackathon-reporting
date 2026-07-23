import sys
import traceback
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import settings
import vertexai
import google.auth

# Configure logging to output to both console AND file
logging.basicConfig(
    level=logging.INFO,  # Standardized to INFO (DEBUG can leak auth tokens)
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("reporting_app")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

def init_vertex():
    """Safely initialize Vertex AI using auto-discovered or configured project settings."""
    try:
        logger.info("Fetching Google Application Default Credentials...")
        credentials, discovered_project = google.auth.default()

        # Fall back to auto-discovered project ID if settings.PROJECT_ID is missing or empty
        project_id = getattr(settings, "PROJECT_ID", None) or discovered_project
        location = getattr(settings, "LOCATION", "us-central1")

        logger.info(f"Initializing Vertex AI (Project: {project_id}, Location: {location})...")

        # Build kwargs dynamically to avoid passing invalid/empty optional params
        init_kwargs = {
            "project": project_id,
            "location": location,
            "credentials": credentials,
        }

        # Only pass api_transport if explicitly set to a valid non-empty string
        #api_transport = getattr(settings, "API_TRANSPORT", None)
        #if api_transport:
        #  init_kwargs["api_transport"] = api_transport

        vertexai.init(**init_kwargs)
        logger.info("✅ Vertex AI initialized successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Vertex AI: {e}")
        logger.error(traceback.format_exc())
        raise e  # Fail early so the app doesn't start in a broken state

# Initialize Vertex AI before routes load
init_vertex()

app = FastAPI(
    title="Test AI",
    version="1.0.0",
    docs_url="/"
)

# Import routes after Vertex AI initialization
from api.routes import router
app.include_router(router)
logger.info("FastAPI application started and routes included.")
