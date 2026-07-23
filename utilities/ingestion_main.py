import logging
import sys
from pathlib import Path

from utilities.ingestion_agent import IngestionAgent

#sys.path.append(str(Path(__file__).parent))
#logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

def main():
    logging.info("Starting Data Loading")
    logging.info("Initializing Agent")
    ingestion_agent = IngestionAgent()
    ingestion_result = ingestion_agent.run()
    logging.info("Ingestion Successful")

if __name__ == "__main__":
    main()