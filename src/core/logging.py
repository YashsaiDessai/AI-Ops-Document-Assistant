import logging
import sys
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    Formatter that prints log records along with any extra context passed as key-value pairs.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Filter out standard LogRecord fields to find extra context
        standard_fields = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
            'stack_info', 'thread', 'threadName'
        }
        extra_keys = {
            key: val
            for key, val in record.__dict__.items()
            if key not in standard_fields
        }

        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        kv_context = " ".join(f"{k}={v}" for k, v in extra_keys.items())
        exc_str = ""
        if record.exc_info:
            exc_str = f"\n{self.formatException(record.exc_info)}"

        if kv_context:
            return f"[{timestamp}] {level:<7} [{logger_name}] {message} | {kv_context}{exc_str}"
        return f"[{timestamp}] {level:<7} [{logger_name}] {message}{exc_str}"


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """
    Adapter that automatically intercepts keyword arguments and passes them as 'extra' logging fields.
    Allows style: logger.info("Message", key1="val1", key2="val2")
    Protects against collisions with standard LogRecord fields by prefixing reserved keys.
    """
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any] = None):
        super().__init__(logger, extra or {})

    def process(self, msg: Any, kwargs: Any) -> tuple[Any, Any]:
        extra = self.extra.copy() if self.extra else {}
        
        # Standard attributes that cannot be overwritten in a LogRecord __dict__
        reserved = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
            'stack_info', 'thread', 'threadName', 'message'
        }

        # Move all non-standard parameters to extra dict
        for key in list(kwargs.keys()):
            if key not in {'exc_info', 'stack_info', 'stacklevel', 'extra'}:
                val = kwargs.pop(key)
                log_key = f"ctx_{key}" if key in reserved else key
                extra[log_key] = val
        kwargs['extra'] = extra
        return msg, kwargs


def get_logger(name: str) -> StructuredLoggerAdapter:
    """
    Utility function to obtain a configured structured logger.
    """
    logger = logging.getLogger(name)
    return StructuredLoggerAdapter(logger)


def configure_logging(verbose: bool = False) -> None:
    """
    Initializes and sets up the root logger configuration.
    """
    root_logger = logging.getLogger()
    level = logging.DEBUG if verbose else logging.INFO
    root_logger.setLevel(level)

    # Clean existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = StructuredFormatter()
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
