"""
Main entry point for the NeuralLog SDK.
"""

import threading
from typing import Dict, Any, Optional

from neurallog_sdk.models.neurallog_config import NeuralLogConfig
from neurallog_sdk.ai_logger import AILogger


class NeuralLog:
    """Main entry point for the NeuralLog SDK."""
    
    _config = NeuralLogConfig()
    _loggers: Dict[str, AILogger] = {}
    _global_context: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    @classmethod
    def configure(cls, config: NeuralLogConfig) -> None:
        """Configure the NeuralLog SDK.
        
        Args:
            config: The configuration to use.
        """
        if not config:
            raise ValueError("Config cannot be None")
        
        cls._config = config
    
    @classmethod
    def get_config(cls) -> NeuralLogConfig:
        """Get the current configuration.
        
        Returns:
            The current configuration.
        """
        return cls._config
    
    @classmethod
    def get_logger(cls, log_name: str) -> AILogger:
        """Get a logger with the specified name.
        
        Args:
            log_name: The name of the log.
            
        Returns:
            An AI logger.
            
        Raises:
            ValueError: If log_name is empty.
        """
        if not log_name:
            raise ValueError("Log name cannot be empty")
        
        with cls._lock:
            if log_name not in cls._loggers:
                logger = AILogger(log_name, cls._config)
                
                if cls._global_context:
                    logger.set_context(cls._global_context)
                
                cls._loggers[log_name] = logger
            
            return cls._loggers[log_name]
    
    @classmethod
    def set_global_context(cls, context: Dict[str, Any]) -> None:
        """Set global context data for all loggers.
        
        Args:
            context: The context data to set.
            
        Raises:
            ValueError: If context is None.
        """
        if context is None:
            raise ValueError("Context cannot be None")
        
        cls._global_context = context.copy()
        
        with cls._lock:
            for logger in cls._loggers.values():
                logger.set_context(cls._global_context)
    
    @classmethod
    def flush_all(cls) -> None:
        """Flush all loggers."""
        with cls._lock:
            for logger in cls._loggers.values():
                logger.flush()
