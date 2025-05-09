import logging
import sys
from app.config import LOG_LEVEL


class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter that adds colors to log messages based on their level.
    """
    COLOR_CODES = {
        logging.DEBUG: "\033[94m",     # Blue
        logging.INFO: "\033[92m",      # Green
        logging.WARNING: "\033[93m",   # Yellow
        logging.ERROR: "\033[91m",     # Red
        logging.CRITICAL: "\033[95m",  # Magenta
    }
    RESET_CODE = "\033[0m"

    def format(self, record):
        color = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        record.levelname = f"{color}{record.levelname}{self.RESET_CODE}"
        message = super().format(record)
        return message


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger configured with a colored console handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    return logger
