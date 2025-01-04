import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import open_discourse.definitions.path_definitions as path_definitions


def setup_and_get_logger(
    log_file: str, log_level: int = logging.DEBUG
) -> logging.Logger:
    """
    Logger Setup for Root-Logger; can be used globally

    Args:
        log_file (str)  : name of log_file, 3 chars minimum required
        log_level (int) : logging level, e.g. logging.DEBUG (default value)

    Returns:
        logger (logging.logger):
    """
    # check args
    if not isinstance(log_file, str) or len(log_file) < 3:
        raise ValueError("arg 'log_file' should be a string of 3 chars minimum!")
    # only standard log levels are supported
    if not isinstance(log_level, int) or log_level not in (
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ):
        log_level = logging.DEBUG

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # file handler
    logs_dir = path_definitions.LOGS_DIR
    logs_dir.mkdir(parents=False, exist_ok=True)  # create logs directory if necessary
    log_file = Path(logs_dir, str(Path(log_file).stem + ".log"), encoding="utf-8")
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
