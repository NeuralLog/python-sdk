"""
Adapter for Python's standard logging module.
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union

from neurallog_sdk import NeuralLog, AILogger, NeuralLogConfig, LogLevel


class NeuralLogHandler(logging.Handler):
    """
    A logging handler that sends logs to NeuralLog.
    
    This handler integrates with Python's standard logging module, allowing
    existing applications to send logs to NeuralLog with minimal changes.
    
    Example:
        ```python
        import logging
        from neurallog_sdk.adapters import NeuralLogHandler
        
        # Configure the standard logging handler
        logger = logging.getLogger("my-application")
        handler = NeuralLogHandler(
            log_name="my-application",
            server_url="http://localhost:3030",
            namespace="default"
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Usage
        logger.info("Hello, world!")
        
        # With structured data
        logger.info("User logged in", extra={
            "data": {
                "user": "john.doe",
                "action": "login"
            }
        })
        
        # With exception
        try:
            # Some code that might throw an exception
            raise Exception("Something went wrong")
        except Exception as e:
            logger.exception("Failed to process request")
        ```
    """
    
    def __init__(
        self,
        log_name: str,
        server_url: Optional[str] = None,
        namespace: Optional[str] = None,
        api_key: Optional[str] = None,
        async_enabled: bool = True,
        batch_size: int = 100,
        batch_interval_ms: int = 5000,
        level: int = logging.NOTSET
    ):
        """
        Initialize the NeuralLog handler.
        
        Args:
            log_name: The name of the log in NeuralLog.
            server_url: The URL of the NeuralLog server. If not provided, uses the global config.
            namespace: The namespace to use. If not provided, uses the global config.
            api_key: The API key to use. If not provided, uses the global config.
            async_enabled: Whether to enable asynchronous logging.
            batch_size: The number of logs to batch before sending.
            batch_interval_ms: The interval in milliseconds to send batched logs.
            level: The minimum logging level to process.
        """
        super().__init__(level)
        
        # Create a custom config if any parameters are provided
        if server_url or namespace or api_key or not async_enabled or batch_size != 100 or batch_interval_ms != 5000:
            config = NeuralLogConfig(
                server_url=server_url or NeuralLog.get_config().server_url,
                namespace=namespace or NeuralLog.get_config().namespace,
                api_key=api_key or NeuralLog.get_config().api_key,
                async_enabled=async_enabled,
                batch_size=batch_size,
                batch_interval_ms=batch_interval_ms
            )
            self.logger = AILogger(log_name, config)
        else:
            # Use the global config
            self.logger = NeuralLog.get_logger(log_name)
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to NeuralLog.
        
        Args:
            record: The log record to emit.
        """
        try:
            # Convert logging level to NeuralLog level
            level = self._convert_level(record.levelno)
            
            # Extract message
            message = self.format(record)
            
            # Extract exception info
            exception = None
            if record.exc_info:
                exception = record.exc_info[1]
            
            # Extract structured data
            data = self._extract_data(record)
            
            # Send log to NeuralLog
            self.logger.log(level, message, data, exception)
        except Exception as e:
            self.handleError(record)
    
    def _convert_level(self, level: int) -> LogLevel:
        """
        Convert a logging level to a NeuralLog level.
        
        Args:
            level: The logging level to convert.
            
        Returns:
            The corresponding NeuralLog level.
        """
        if level >= logging.CRITICAL:
            return LogLevel.FATAL
        elif level >= logging.ERROR:
            return LogLevel.ERROR
        elif level >= logging.WARNING:
            return LogLevel.WARNING
        elif level >= logging.INFO:
            return LogLevel.INFO
        else:
            return LogLevel.DEBUG
    
    def _extract_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Extract structured data from a log record.
        
        Args:
            record: The log record to extract data from.
            
        Returns:
            The extracted data.
        """
        data = {}
        
        # Add standard fields
        data["logger"] = record.name
        data["file"] = record.pathname
        data["line"] = record.lineno
        data["function"] = record.funcName
        data["thread"] = record.threadName
        data["process"] = record.processName
        
        # Add extra data if available
        if hasattr(record, "data") and isinstance(record.data, dict):
            data.update(record.data)
        
        # Add all extra attributes
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "args", "asctime", "created", "exc_info", "exc_text",
                    "filename", "funcName", "levelname", "levelno", "lineno",
                    "module", "msecs", "message", "msg", "name", "pathname",
                    "process", "processName", "relativeCreated", "stack_info",
                    "thread", "threadName", "data"
                }:
                    data[key] = value
        
        return data
    
    def flush(self) -> None:
        """Flush any pending logs."""
        self.logger.flush()
    
    def close(self) -> None:
        """Close the handler and flush any pending logs."""
        self.flush()
        super().close()
