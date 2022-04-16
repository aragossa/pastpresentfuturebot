import logging
import sys
from logging.handlers import RotatingFileHandler


FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():

    # open(f"logs/{file_name}.log", 'a').close()
    file_handler = RotatingFileHandler(f"logs/output.log", maxBytes=30000000, backupCount=5)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    # logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
