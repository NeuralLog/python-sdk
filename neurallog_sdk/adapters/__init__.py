"""
Adapters for integrating NeuralLog with popular Python logging frameworks.
"""

from neurallog_sdk.adapters.standard_logging import NeuralLogHandler

# Try to import Loguru adapter if Loguru is available
try:
    from neurallog_sdk.adapters.loguru_adapter import NeuralLogSink
    __all__ = ["NeuralLogHandler", "NeuralLogSink"]
except ImportError:
    __all__ = ["NeuralLogHandler"]
