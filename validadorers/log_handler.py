
import logging
import sys

from .const_app import PATH_GLOBAL
from .const_file import LogFile


def new_stream_handler(_logger: logging.Logger, stream) -> logging.StreamHandler:
    """Create new stream handler

    Args:
        _logger: logger instance.
        stream: stream object.
    Returns:
        Stream handler.
    """
    format_console = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )
    _handler = logging.StreamHandler(stream)
    _handler.setFormatter(format_console)
    _handler.setLevel(logging.INFO)
    _logger.addHandler(_handler)
    return _handler


def new_file_handler(_logger: logging.Logger, filepath: str, filename: str) -> logging.FileHandler:
    """Create new file handler

    Args:
        _logger: logger instance.
        filepath: log file path.
        filename: log file name.
    Returns:
        File handler.
    """
    format_file = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    _handler = logging.FileHandler(f"{filepath}{filename}")
    _handler.setFormatter(format_file)
    _handler.setLevel(logging.INFO)
    _logger.addHandler(_handler)
    return _handler


def set_logging_level(_logger: logging.Logger, log_stream=None, log_level=1) -> None:
    """Set logging level

    Args:
        _logger: logger instance.
        log_stream: log stream object.
        log_level:
            0 = output only warning or error to console.
            1 = output all log to console.
            2 = output all log to both console & file.
    """
    _logger.setLevel(logging.INFO)
    if log_stream is not None:
        new_stream_handler(_logger, log_stream)
    if log_level >= 1:
        new_stream_handler(_logger, sys.stdout)
        _logger.info("LOGGING: output to console")
    if log_level == 2:
        new_file_handler(_logger, PATH_GLOBAL, LogFile.APP_LOG)
        _logger.info("LOGGING: output to %s", LogFile.APP_LOG)
