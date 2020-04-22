import sys
import logging


def get_logger(name):
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    screen_handler = logging.StreamHandler(
        stream=sys.stdout
    )
    screen_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        f"{name}.log", mode="a", encoding=None, delay=False
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(screen_handler)
    logger.addHandler(file_handler)

    return logger
