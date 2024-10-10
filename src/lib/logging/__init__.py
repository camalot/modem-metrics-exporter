import logging
import sys
import typing

from config.LoggingConfiguration import LoggingConfiguration
from lib.logging.ColorFormatter import ColorFormatter


def setup_logging(
    name: typing.Optional[str] = None, config: LoggingConfiguration = None  # type: ignore
) -> logging.Logger:
    logger = logging.getLogger("modemprobe" if name is None else name)
    log_config: LoggingConfiguration = config
    if log_config is None:
        raise ValueError("Logging configuration is required")

    logger.setLevel(level=log_config.level or logging.INFO)

    # Set formatter
    logColorFormatter = ColorFormatter(fmt=log_config.format, datefmt=log_config.date_format)

    stdoutHandler = logging.StreamHandler(sys.stdout)
    stdoutHandler.name = "stdout"
    stdoutHandler.setFormatter(logColorFormatter)
    stdoutHandler.setLevel(level=config.level)

    active_handlers = [stdoutHandler]

    if not logger.handlers:
        # check if stdoutHandler is already added
        # check if a handler with the name is already added
        for handler in active_handlers:
            if not logger.hasHandlers():
                logger.addHandler(handler)
            elif not any([handler.name == h.name for h in logger.handlers]):
                logger.addHandler(handler)

    return logger
