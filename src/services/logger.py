"""
This module provides the QAsystem class which sets up logging for the system.
"""
import os
import logging

LOG_NOTIFICATION = "====="


class DSCLogger(object):
    """
    A class to handle logging for system.
    """

    def __init__(
        self,
        file_name,
        file_log="log",
        write_to_file=False,
        mode="info",
        data_source="./log"
    ):
        """
        Initialize the QAsystem instance.
        """
        self.file_name = file_name

        if not write_to_file:
            logging.basicConfig()

        self.logger = logging.getLogger(file_log)

        if write_to_file:
            hdlr = logging.FileHandler(os.path.join(
                data_source, f"{file_log}.log"))
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s")
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)

        self.logger.setLevel(logging.INFO)

        if mode == "debug":
            self.logger.setLevel(logging.DEBUG)

    def info(self, content):
        """
        Log an informational message.

        Args:
            content (str): The message content to log.

        Returns:
            None
        """
        content = f"{self.file_name}:{LOG_NOTIFICATION} {content}"
        self.logger.info(content)

    def error(self, content):
        """
        Log an error message.

        Args:
            content (str): The message content to log.

        Returns:
            None
        """
        content = f"{self.file_name}:{LOG_NOTIFICATION}{content}"
        self.logger.error(content)

    def debug(self, content):
        """
        Log a debug message.

        Args:
            content (str): The message content to log.

        Returns:
            None
        """
        content = f"{self.file_name}:{LOG_NOTIFICATION}{content}"
        self.logger.debug(content)
