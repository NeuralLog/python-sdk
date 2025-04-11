"""
Tests for the standard logging adapter.
"""

import unittest
import logging
from unittest.mock import patch, MagicMock

from neurallog_sdk.adapters import NeuralLogHandler
from neurallog_sdk import LogLevel


class TestStandardLoggingAdapter(unittest.TestCase):
    """Tests for the standard logging adapter."""
    
    def setUp(self):
        """Set up the test environment."""
        # Configure the root logger
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in self.root_logger.handlers[:]:
            self.root_logger.removeHandler(handler)
        
        # Create a NeuralLogHandler with a mock logger
        self.mock_ai_logger = MagicMock()
        self.handler = NeuralLogHandler("test-logger")
        self.handler.logger = self.mock_ai_logger
        
        # Add the handler to the root logger
        self.root_logger.addHandler(self.handler)
    
    def test_info_log_is_sent_to_neurallog(self):
        """Test that an info log is sent to NeuralLog."""
        # Arrange
        message = "Test info message"
        
        # Act
        logging.info(message)
        
        # Assert
        self.mock_ai_logger.log.assert_called_once()
        args, _ = self.mock_ai_logger.log.call_args
        self.assertEqual(LogLevel.INFO, args[0])
        self.assertTrue(message in args[1])
    
    def test_error_log_with_exception_includes_exception_details(self):
        """Test that an error log with an exception includes exception details."""
        # Arrange
        message = "Test error message"
        exception = ValueError("Test exception")
        
        # Act
        try:
            raise exception
        except ValueError:
            logging.exception(message)
        
        # Assert
        self.mock_ai_logger.log.assert_called_once()
        args, _ = self.mock_ai_logger.log.call_args
        self.assertEqual(LogLevel.ERROR, args[0])
        self.assertTrue(message in args[1])
        self.assertIsNotNone(args[3])  # Exception
    
    def test_log_with_extra_data_includes_data_in_neurallog(self):
        """Test that a log with extra data includes the data in NeuralLog."""
        # Arrange
        message = "Test message with data"
        extra_data = {"user": "john.doe", "action": "login"}
        
        # Act
        logging.info(message, extra={"data": extra_data})
        
        # Assert
        self.mock_ai_logger.log.assert_called_once()
        args, _ = self.mock_ai_logger.log.call_args
        self.assertEqual(LogLevel.INFO, args[0])
        self.assertTrue(message in args[1])
        
        # Check that the extra data is included
        data = args[2]
        self.assertEqual("john.doe", data.get("user"))
        self.assertEqual("login", data.get("action"))
    
    def test_debug_log_is_converted_to_debug_level(self):
        """Test that a debug log is converted to the debug level."""
        # Arrange
        self.root_logger.setLevel(logging.DEBUG)
        message = "Test debug message"
        
        # Act
        logging.debug(message)
        
        # Assert
        self.mock_ai_logger.log.assert_called_once()
        args, _ = self.mock_ai_logger.log.call_args
        self.assertEqual(LogLevel.DEBUG, args[0])
        self.assertTrue(message in args[1])
    
    def test_warning_log_is_converted_to_warning_level(self):
        """Test that a warning log is converted to the warning level."""
        # Arrange
        message = "Test warning message"
        
        # Act
        logging.warning(message)
        
        # Assert
        self.mock_ai_logger.log.assert_called_once()
        args, _ = self.mock_ai_logger.log.call_args
        self.assertEqual(LogLevel.WARNING, args[0])
        self.assertTrue(message in args[1])
    
    def test_critical_log_is_converted_to_fatal_level(self):
        """Test that a critical log is converted to the fatal level."""
        # Arrange
        message = "Test critical message"
        
        # Act
        logging.critical(message)
        
        # Assert
        self.mock_ai_logger.log.assert_called_once()
        args, _ = self.mock_ai_logger.log.call_args
        self.assertEqual(LogLevel.FATAL, args[0])
        self.assertTrue(message in args[1])
    
    def test_flush_calls_flush_on_neurallog_logger(self):
        """Test that flush calls flush on the NeuralLog logger."""
        # Act
        self.handler.flush()
        
        # Assert
        self.mock_ai_logger.flush.assert_called_once()


if __name__ == "__main__":
    unittest.main()
