import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(log_file='app.log', level=logging.DEBUG):
    """Logger Setup für Root-Logger, der global genutzt wird."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Dateihandler
    logs_dir = Path(Path(__file__).parent.parent.parent, "logs")
    log_file = Path(logs_dir,log_file)
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # Konsolenhandler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Holen des Root-Loggers
    logger = logging.getLogger()
    logger.setLevel(level)

    # Nur hinzufügen, wenn noch keine Handler vorhanden sind (vermeidet doppelte Ausgaben)
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
