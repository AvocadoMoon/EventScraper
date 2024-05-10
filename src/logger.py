import logging

logger_name = "codebase_logger"

def setup_custom_logger(logLevel: int):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logLevel)
    logger.addHandler(handler)
    return logger

