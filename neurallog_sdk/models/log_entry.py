"""
Log entry model for the NeuralLog SDK.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import traceback

from neurallog_sdk.models.log_level import LogLevel


class ExceptionInfo:
    """Information about an exception."""

    def __init__(self, exception: Exception):
        """Initialize the exception info.

        Args:
            exception: The exception to convert.
        """
        self.type = exception.__class__.__name__
        self.message = str(exception)
        self.stack_trace = traceback.format_exc()
        self.inner_exception = None

        # Handle inner exception if available
        if hasattr(exception, "__cause__") and exception.__cause__:
            self.inner_exception = ExceptionInfo(exception.__cause__)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the exception info to a dictionary.

        Returns:
            A dictionary representation of the exception info.
        """
        result = {
            "type": self.type,
            "message": self.message,
            "stackTrace": self.stack_trace
        }

        if self.inner_exception:
            result["innerException"] = self.inner_exception.to_dict()

        return result


class LogEntry:
    """Log entry model for the NeuralLog SDK."""

    def __init__(
        self,
        level: LogLevel,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ):
        """Initialize the log entry.

        Args:
            level: The severity level of the log entry.
            message: The log message.
            data: The structured data associated with the log entry.
            exception: The exception if the log entry represents an error.
        """
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.level = level
        self.message = message
        self.data = data or {}
        self.exception = ExceptionInfo(exception) if exception else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the log entry to a dictionary.

        Returns:
            A dictionary representation of the log entry.
        """
        result = {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "data": self.data
        }

        if self.exception:
            result["exception"] = self.exception.to_dict()

        return result
