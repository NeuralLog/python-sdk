"""
Tests for the AILogger class.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import uuid
from datetime import datetime

from neurallog_sdk import AILogger, NeuralLogConfig, LogLevel
from neurallog_sdk.http import HttpClient


class TestAILogger(unittest.TestCase):
    """Tests for the AILogger class."""

    def setUp(self):
        """Set up the test environment."""
        self.mock_http_client = MagicMock(spec=HttpClient)
        self.config = NeuralLogConfig(
            server_url="https://logs.example.com",
            namespace="test",
            api_key="test-api-key",
            async_enabled=False  # Use synchronous mode for testing
        )
        self.logger = AILogger("test-logger", self.config, self.mock_http_client)

    def test_info_sends_log_entry_with_correct_level(self):
        """Test that info sends a log entry with the correct level."""
        # Arrange
        self.mock_http_client.send.return_value = {"status": "created"}

        # Act
        self.logger.info("Test message")

        # Assert
        self.mock_http_client.send.assert_called_once()
        args, _ = self.mock_http_client.send.call_args
        self.assertEqual("POST", args[0])
        self.assertTrue("/logs/test-logger" in args[1])
        
        # Verify the log entry
        log_entry = json.loads(args[2])
        self.assertEqual("info", log_entry["level"].lower())
        self.assertEqual("Test message", log_entry["message"])

    def test_error_with_exception_sends_log_entry_with_exception_details(self):
        """Test that error with exception sends a log entry with exception details."""
        # Arrange
        self.mock_http_client.send.return_value = {"status": "created"}
        exception = Exception("Test exception")

        # Act
        self.logger.error("Error occurred", exception=exception)

        # Assert
        self.mock_http_client.send.assert_called_once()
        args, _ = self.mock_http_client.send.call_args
        
        # Verify the log entry
        log_entry = json.loads(args[2])
        self.assertEqual("error", log_entry["level"].lower())
        self.assertEqual("Error occurred", log_entry["message"])
        self.assertIsNotNone(log_entry["exception"])
        self.assertEqual("Exception", log_entry["exception"]["type"])
        self.assertEqual("Test exception", log_entry["exception"]["message"])

    def test_log_with_structured_data_sends_log_entry_with_data(self):
        """Test that log with structured data sends a log entry with data."""
        # Arrange
        self.mock_http_client.send.return_value = {"status": "created"}
        data = {
            "user": "john.doe",
            "action": "login"
        }

        # Act
        self.logger.info("User logged in", data=data)

        # Assert
        self.mock_http_client.send.assert_called_once()
        args, _ = self.mock_http_client.send.call_args
        
        # Verify the log entry
        log_entry = json.loads(args[2])
        self.assertEqual("info", log_entry["level"].lower())
        self.assertEqual("User logged in", log_entry["message"])
        self.assertEqual("john.doe", log_entry["data"]["user"])
        self.assertEqual("login", log_entry["data"]["action"])

    @patch("neurallog_sdk.ai_logger.time.sleep")
    def test_log_with_batching_enabled_batches_requests(self, mock_sleep):
        """Test that log with batching enabled batches requests."""
        # Arrange
        batch_config = NeuralLogConfig(
            server_url="https://logs.example.com",
            namespace="test",
            api_key="test-api-key",
            async_enabled=True,
            batch_size=2,
            batch_interval_ms=100
        )
        batch_logger = AILogger("batch-logger", batch_config, self.mock_http_client)
        self.mock_http_client.send.return_value = {"status": "created"}

        # Act
        batch_logger.info("Message 1")
        batch_logger.info("Message 2")
        
        # Wait for batch to be sent (mocked)
        mock_sleep.return_value = None
        batch_logger.flush()

        # Assert
        self.mock_http_client.send.assert_called_once()
        args, _ = self.mock_http_client.send.call_args
        self.assertEqual("POST", args[0])
        self.assertTrue("/logs/batch-logger/batch" in args[1])
        
        # Verify the batch
        batch = json.loads(args[2])
        self.assertEqual(2, len(batch))
        self.assertEqual("Message 1", batch[0]["message"])
        self.assertEqual("Message 2", batch[1]["message"])


if __name__ == "__main__":
    unittest.main()
