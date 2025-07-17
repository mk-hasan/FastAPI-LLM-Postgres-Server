import logging
import os

def setup_logging():
    """
    Sets up basic logging configuration.
    For production, consider more robust solutions like structlog or integrations with ELK stack.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(), # Logs to console
            # logging.FileHandler("app.log") # Uncomment for file logging
        ]
    )