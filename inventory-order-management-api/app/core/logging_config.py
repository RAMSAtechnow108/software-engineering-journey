import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    
    BASE_DIR = Path(__file__).resolve().parents[2]

    LOG_DIR = BASE_DIR/"logs"
    LOG_DIR.mkdir(parents=True, exist_ok = True)
    root_logger = logging.getLogger()
    
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    
    
    file_handler = RotatingFileHandler(
        filename= LOG_DIR / "app.log",
        maxBytes= 10 * 1024 *1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    

    root_logger.setLevel(logging.DEBUG)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    
    root_logger.info("Logging system initialized")