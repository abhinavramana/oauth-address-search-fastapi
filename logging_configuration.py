import logging
from pythonjsonlogger import jsonlogger


def add_json_config_to_logger(logger):
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
