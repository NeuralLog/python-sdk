"""
Tests for the NeuralLog class.
"""

import unittest
from unittest.mock import patch, MagicMock

from neurallog_sdk import NeuralLog, NeuralLogConfig


class TestNeuralLog(unittest.TestCase):
    """Tests for the NeuralLog class."""

    def test_configure_sets_global_config(self):
        """Test that configure sets the global config."""
        # Arrange
        config = NeuralLogConfig(
            server_url="https://logs.example.com",
            namespace="test",
            api_key="test-api-key"
        )

        # Act
        NeuralLog.configure(config)

        # Assert
        self.assertEqual(config, NeuralLog.get_config())

    def test_get_logger_returns_logger_with_correct_name(self):
        """Test that get_logger returns a logger with the correct name."""
        # Arrange
        log_name = "test-logger"
        NeuralLog.configure(NeuralLogConfig(
            server_url="https://logs.example.com",
            namespace="test"
        ))

        # Act
        logger = NeuralLog.get_logger(log_name)

        # Assert
        self.assertIsNotNone(logger)
        self.assertEqual(log_name, logger.log_name)

    def test_set_global_context_sets_context_for_all_loggers(self):
        """Test that set_global_context sets context for all loggers."""
        # Arrange
        NeuralLog.configure(NeuralLogConfig(
            server_url="https://logs.example.com",
            namespace="test"
        ))
        logger1 = NeuralLog.get_logger("logger1")
        logger2 = NeuralLog.get_logger("logger2")
        
        # Mock the set_context method
        logger1.set_context = MagicMock()
        logger2.set_context = MagicMock()
        
        context = {"app": "test-app", "env": "test"}

        # Act
        NeuralLog.set_global_context(context)

        # Assert
        logger1.set_context.assert_called_once_with(context)
        logger2.set_context.assert_called_once_with(context)

    @patch("neurallog_sdk.ai_logger.AILogger.flush")
    def test_flush_all_flushes_all_loggers(self, mock_flush):
        """Test that flush_all flushes all loggers."""
        # Arrange
        NeuralLog.configure(NeuralLogConfig(
            server_url="https://logs.example.com",
            namespace="test"
        ))
        NeuralLog.get_logger("logger1")
        NeuralLog.get_logger("logger2")
        
        # Act
        NeuralLog.flush_all()

        # Assert
        self.assertEqual(2, mock_flush.call_count)


if __name__ == "__main__":
    unittest.main()
