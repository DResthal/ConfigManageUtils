import logging
import sys


class CustomLogger:
    def __init__(
        self,
        name: str,
        log_file: str,
        level: int = logging.WARNING,
        formatter=logging.Formatter("%(asctime)s %(levelname)s %(message)s"),
    ):
        self.name = name
        self.log_file = log_file
        self.level = level
        self.formatter = formatter

    def create_logger(self):
        file_handler = logging.FileHandler(self.log_file)
        stdout_handler = logging.StreamHandler(sys.stdout)
        file_handler.setFormatter(self.formatter)
        stdout_handler.setFormatter(self.formatter)
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

        return logger