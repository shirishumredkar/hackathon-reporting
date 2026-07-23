import configparser
import os
from pathlib import Path


def load_agent_config() -> configparser.ConfigParser:
    # Look inside the 'configs' subfolder relative to config.py
    config_path = Path(__file__).parent / "configs" / "agent.properties"

    # Fallback check in case it's in the same directory
    if not config_path.exists():
        config_path = Path(__file__).parent / "agent.properties"

    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path)
    else:
        print(f"⚠️ Warning: Could not locate agent.properties at {config_path}")

    return config


def setup_environment_variables(config: configparser.ConfigParser) -> None:
    # Case-insensitive section lookup
    section_key = next((sec for sec in config.sections() if sec.lower() == "global"), None)
    global_config = config[section_key] if section_key else {}

    os.environ["GOOGLE_CLOUD_PROJECT"] = global_config.get("project_id", "")
    os.environ["GOOGLE_CLOUD_LOCATION"] = global_config.get("location", "")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = global_config.get("use_vertexai", "")

    use_rest_val = global_config.get("google_api_use_rest", "").strip().lower()
    if use_rest_val in ("true", "1"):
        os.environ["GOOGLE_API_USE_REST"] = "true"
    else:
        os.environ.pop("GOOGLE_API_USE_REST", None)

    os.environ["GRPC_SSL_CIPHER_SUITES"] = global_config.get("grpc_ssl_cipher_suites", "HIGH+ECDSA")
    os.environ["GRPC_DNS_RESOLVER"] = global_config.get("grpc_dns_resolver", "native")


agent_config = load_agent_config()
setup_environment_variables(agent_config)


class Settings:
    def __init__(self, config_parser: configparser.ConfigParser):
        # Case-insensitive lookup for [global]
        section_key = next((sec for sec in config_parser.sections() if sec.lower() == "global"), None)

        if section_key:
            global_config = config_parser[section_key]
            get_val = lambda key, fb="": global_config.get(key, fallback=fb)
        else:
            global_config = {}
            get_val = lambda key, fb="": global_config.get(key, fb)

        # Mappings
        self.PROJECT_ID = get_val("project_id", "")
        self.LOCATION = get_val("location", "europe-west3")
        self.BQ_PROJECT = self.PROJECT_ID
        self.BQ_DATASET = get_val("dataset_name", "")
        self.TABLE_NAME = get_val("table_name", "DOCUMENT_CHUNKS")
        self.EMBEDDING_MODEL = get_val("embedding_model", "text-embedding-004")
        self.MODEL_NAME = get_val("model_name", "gemini-2.5-flash")
        self.TEMPERATURE = float(get_val("temperature", "0.2"))
        self.PRICE_PER_TB = float(get_val("price_per_tb", "5.0"))
        self.DOWNLOAD_DIR = get_val("download_dir", "downloads")
        self.LOCAL_FILE_PATH = get_val("local_file_path", "")
        self.BUCKET_NAME = get_val("bucket_name", "")
        self.CHUNK_SIZE = get_val("chunk_size", "")
        self.CHUNK_OVERLAP = get_val("chunk_overlap", "")
        self.BATCH_SIZE = get_val("batch_size", "")
        self.GCS_URI = get_val("gcs_uri", "")



settings = Settings(agent_config)