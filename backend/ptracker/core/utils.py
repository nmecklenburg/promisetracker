from functools import partial
from termcolor import colored

import logging


class ColorFormatter(logging.Formatter):
    log_colorer = {
        logging.DEBUG: partial(colored, color="grey"),
        logging.INFO: partial(colored, color="white"),
        logging.WARNING: partial(colored, color="light_yellow"),
        logging.CRITICAL: partial(colored, color="light_magenta"),
        logging.ERROR: partial(colored, color="red")
    }

    def format(self, record):
        spacer = 8
        template = self.log_colorer[record.levelno](
            f"%(asctime)s %(levelname)s {' ' * (spacer - len(record.levelname))}|| (%(name)s:%(lineno)d) %(message)s"
        )
        formatter = logging.Formatter(template)
        return formatter.format(record)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(ColorFormatter())
    logger.addHandler(handler)
    return logger
