"""
Log level enum for the NeuralLog SDK.
"""

from enum import Enum


class LogLevel(str, Enum):
    """Log level enum for the NeuralLog SDK."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"
