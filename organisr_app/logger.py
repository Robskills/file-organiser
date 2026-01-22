import logging
import sys
from config import LOG_FILE

def setup_logging():
    """Configures the logging for the application."""
    handlers = [logging.FileHandler(LOG_FILE)]
    
    # Only add stdout handler if stdout exists (prevents crash in windowed mode)
    if sys.stdout:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers
    )