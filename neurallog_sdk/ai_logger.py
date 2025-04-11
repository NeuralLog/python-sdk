"""
AI logger for the NeuralLog SDK.
"""

import json
import time
import threading
from typing import Dict, Any, Optional, List, Union
from queue import Queue

from neurallog_sdk.models.log_level import LogLevel
from neurallog_sdk.models.log_entry import LogEntry
from neurallog_sdk.models.neurallog_config import NeuralLogConfig
from neurallog_sdk.http.http_client import HttpClient


class AILogger:
    """AI logger for the NeuralLog SDK."""
    
    def __init__(self, log_name: str, config: NeuralLogConfig, http_client: Optional[HttpClient] = None):
        """Initialize the AI logger.
        
        Args:
            log_name: The name of the log.
            config: The NeuralLog configuration.
            http_client: The HTTP client to use. If not provided, a new one will be created.
        """
        self.log_name = log_name
        self.config = config
        self.http_client = http_client or HttpClient(config)
        self.context: Dict[str, Any] = {}
        self.batch_queue: Queue = Queue()
        self.batch_lock = threading.Lock()
        self.batch_timer: Optional[threading.Timer] = None
        
        if self.config.async_enabled and self.config.batch_interval_ms > 0:
            self._start_batch_timer()
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Log a debug message.
        
        Args:
            message: The log message.
            data: The structured data to log.
            exception: The exception to log.
        """
        self.log(LogLevel.DEBUG, message, data, exception)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Log an info message.
        
        Args:
            message: The log message.
            data: The structured data to log.
            exception: The exception to log.
        """
        self.log(LogLevel.INFO, message, data, exception)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Log a warning message.
        
        Args:
            message: The log message.
            data: The structured data to log.
            exception: The exception to log.
        """
        self.log(LogLevel.WARNING, message, data, exception)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Log an error message.
        
        Args:
            message: The log message.
            data: The structured data to log.
            exception: The exception to log.
        """
        self.log(LogLevel.ERROR, message, data, exception)
    
    def fatal(self, message: str, data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Log a fatal message.
        
        Args:
            message: The log message.
            data: The structured data to log.
            exception: The exception to log.
        """
        self.log(LogLevel.FATAL, message, data, exception)
    
    def log(self, level: LogLevel, message: str, data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Log a message with the specified level.
        
        Args:
            level: The log level.
            message: The log message.
            data: The structured data to log.
            exception: The exception to log.
        """
        if not message:
            raise ValueError("Message cannot be empty")
        
        # Merge context with data
        merged_data = {}
        if self.context:
            merged_data.update(self.context)
        if data:
            merged_data.update(data)
        
        log_entry = LogEntry(level, message, merged_data, exception)
        
        if self.config.async_enabled:
            if self.config.batch_size > 1:
                self._enqueue_log_entry(log_entry)
            else:
                self._send_log_entry(log_entry)
        else:
            self._send_log_entry(log_entry)
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set context data for the logger.
        
        Args:
            context: The context data to set.
        """
        if context is None:
            raise ValueError("Context cannot be None")
        
        self.context = context.copy()
    
    def flush(self) -> None:
        """Flush any pending log entries."""
        if self.config.async_enabled and self.config.batch_size > 1:
            self._send_batch()
    
    def _enqueue_log_entry(self, log_entry: LogEntry) -> None:
        """Enqueue a log entry for batching.
        
        Args:
            log_entry: The log entry to enqueue.
        """
        self.batch_queue.put(log_entry)
        
        if self.batch_queue.qsize() >= self.config.batch_size:
            self._send_batch()
    
    def _send_log_entry(self, log_entry: LogEntry) -> None:
        """Send a log entry to the server.
        
        Args:
            log_entry: The log entry to send.
        """
        try:
            url = self._get_log_url()
            data = json.dumps(log_entry.to_dict())
            self.http_client.send("POST", url, data)
        except Exception as e:
            if self.config.debug_enabled:
                print(f"Error sending log entry: {e}")
    
    def _send_batch(self) -> None:
        """Send a batch of log entries to the server."""
        with self.batch_lock:
            if self.batch_queue.empty():
                return
            
            log_entries = []
            while not self.batch_queue.empty() and len(log_entries) < self.config.batch_size:
                log_entries.append(self.batch_queue.get())
            
            if not log_entries:
                return
            
            try:
                url = self._get_batch_url()
                data = json.dumps([entry.to_dict() for entry in log_entries])
                self.http_client.send("POST", url, data)
            except Exception as e:
                if self.config.debug_enabled:
                    print(f"Error sending batch: {e}")
    
    def _get_log_url(self) -> str:
        """Get the URL for logging a single entry.
        
        Returns:
            The URL for logging a single entry.
        """
        if self.config.namespace and self.config.namespace != "default":
            return f"{self.config.server_url}/{self.config.namespace}/logs/{self.log_name}"
        return f"{self.config.server_url}/logs/{self.log_name}"
    
    def _get_batch_url(self) -> str:
        """Get the URL for logging a batch of entries.
        
        Returns:
            The URL for logging a batch of entries.
        """
        if self.config.namespace and self.config.namespace != "default":
            return f"{self.config.server_url}/{self.config.namespace}/logs/{self.log_name}/batch"
        return f"{self.config.server_url}/logs/{self.log_name}/batch"
    
    def _start_batch_timer(self) -> None:
        """Start the batch timer."""
        if self.batch_timer:
            self.batch_timer.cancel()
        
        self.batch_timer = threading.Timer(self.config.batch_interval_ms / 1000, self._batch_timer_callback)
        self.batch_timer.daemon = True
        self.batch_timer.start()
    
    def _batch_timer_callback(self) -> None:
        """Callback for the batch timer."""
        self._send_batch()
        self._start_batch_timer()
    
    def __del__(self) -> None:
        """Clean up resources."""
        if self.batch_timer:
            self.batch_timer.cancel()
