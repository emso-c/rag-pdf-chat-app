"""
Module for configuring logging in the application.

This module sets up logging using the Loguru library, defining 
the log files and their retention policies. It includes methods 
to manage log file sizes, ensuring that older log files are 
deleted when the total log size exceeds a predefined limit.

See app/config.py app_config for the storage location

Logging Configuration:
- Logs at the DEBUG level are written to "logfile.log".
- Logs at the ERROR level are written to "error.log".
- Logs at the INFO level are output to the system's standard output (stdout).
"""

import os
import sys
from loguru import logger
from app.config import app_config

# remove all attached loggers
logger.remove()
if app_config.is_testing:
    logger.disable('')

if not app_config.is_testing:
    def size_retention(files: list[str]) -> None:
        """Manages log file retention based on total size.

        This function checks the sizes of log files and deletes the oldest
        files first until the total size is below the defined retention limit.

        Args:
            files (list[str]): A list of file paths to be managed for retention.

        Returns:
            None: This function does not return any value.
        """
        stats = [(file, os.stat(file)) for file in files]
        stats.sort(
            key=lambda s: -s[1].st_mtime
        )  # delete oldest file first by modification time
        while sum(s[1].st_size for s in stats) > app_config.loguru_retention_size:
            file, _ = stats.pop()
            os.remove(file)


    # log debug level logs to logfile.log
    logger.add(
        app_config.log_path / f"logfile.log",
        level="DEBUG",
        rotation=app_config.loguru_rotation,
        compression="zip",
        retention=size_retention,
    )

    # log error level logs to error.log
    logger.add(
        app_config.log_path / f"error.log",
        level="ERROR",
        rotation=app_config.loguru_rotation,
        compression="zip",
        retention=size_retention,
    )

    # log info level logs to system stdout
    logger.add(sys.stdout, level="INFO")
