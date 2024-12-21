import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import open_discourse.definitions.path_definitions as path_definitions


def setup_and_get_logger(
    log_file: str = logging, log_level: int = logging.DEBUG
) -> logging.Logger:
    """Logger Setup for Root-Logger; can be used globally

    Args:
        log_file (str)  : name of log_file
        log_level (int) : logging level, e.g. logging.DEBUG (default value)

    Returns:
        logger (logging.logger):
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # file handler
    logs_dir = path_definitions.LOGS_DIR
    logs_dir.mkdir(parents=False, exist_ok=True)  # create logs directory if necessary
    log_file = Path(logs_dir, str(Path(log_file).stem + ".log"))
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # get and config root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Add only if no handlers, to avoid double output
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger