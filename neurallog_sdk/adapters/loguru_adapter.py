"""
Adapter for Loguru.
"""

import sys
from typing import Any, Dict, Optional, Union, Callable

from neurallog_sdk import NeuralLog, AILogger, NeuralLogConfig, LogLevel

# Check if loguru is installed
try:
    import loguru
    LOGURU_AVAILABLE = True
    Message = loguru.Message
except ImportError:
    LOGURU_AVAILABLE = False
    # Define a placeholder for type hints
    class Message:
        pass


class NeuralLogSink:
    """
    A sink for Loguru that sends logs to NeuralLog.

    This sink integrates with Loguru, allowing existing applications
    to send logs to NeuralLog with minimal changes.

    Example:
        ```python
        from loguru import logger
        from neurallog_sdk.adapters import NeuralLogSink

        # Configure the Loguru sink
        logger.configure(handlers=[
            {
                "sink": NeuralLogSink(
                    log_name="my-application",
                    server_url="http://localhost:3030",
                    namespace="default"
                ),
                "level": "INFO"
            }
        ])

        # Usage
        logger.info("Hello, world!")

        # With structured data
        logger.info("User logged in", user="john.doe", action="login")

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
        batch_interval_ms: int = 5000
    ):
        """
        Initialize the NeuralLog sink.

        Args:
            log_name: The name of the log in NeuralLog.
            server_url: The URL of the NeuralLog server. If not provided, uses the global config.
            namespace: The namespace to use. If not provided, uses the global config.
            api_key: The API key to use. If not provided, uses the global config.
            async_enabled: Whether to enable asynchronous logging.
            batch_size: The number of logs to batch before sending.
            batch_interval_ms: The interval in milliseconds to send batched logs.
        """
        if not LOGURU_AVAILABLE:
            raise ImportError(
                "Loguru is not installed. Please install it with 'pip install loguru'."
            )

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

    def __call__(self, message: Message) -> None:
        """
        Process a Loguru message.

        Args:
            message: The Loguru message to process.
        """
        # Convert Loguru level to NeuralLog level
        level = self._convert_level(message.record["level"].name)

        # Extract message text
        message_text = message.record["message"]

        # Extract exception
        exception = message.record["exception"]
        if exception:
            exception = exception.value

        # Extract structured data
        data = self._extract_data(message.record)

        # Send log to NeuralLog
        self.logger.log(level, message_text, data, exception)

    def _convert_level(self, level_name: str) -> LogLevel:
        """
        Convert a Loguru level name to a NeuralLog level.

        Args:
            level_name: The Loguru level name to convert.

        Returns:
            The corresponding NeuralLog level.
        """
        level_name = level_name.lower()

        if level_name in ("critical", "fatal"):
            return LogLevel.FATAL
        elif level_name == "error":
            return LogLevel.ERROR
        elif level_name == "warning":
            return LogLevel.WARNING
        elif level_name == "info":
            return LogLevel.INFO
        else:
            return LogLevel.DEBUG

    def _extract_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from a Loguru record.

        Args:
            record: The Loguru record to extract data from.

        Returns:
            The extracted data.
        """
        data = {}

        # Add standard fields
        data["logger"] = record["name"]
        data["file"] = record["file"].path
        data["line"] = record["line"]
        data["function"] = record["function"]
        data["thread"] = record["thread"].name
        data["process"] = record["process"].name

        # Add extra attributes
        for key, value in record["extra"].items():
            data[key] = value

        return data

    def flush(self) -> None:
        """Flush any pending logs."""
        self.logger.flush()
