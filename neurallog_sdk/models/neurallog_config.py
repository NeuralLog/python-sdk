"""
Configuration for the NeuralLog SDK.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class NeuralLogConfig:
    """Configuration for the NeuralLog SDK."""
    
    server_url: str = "http://localhost:3030"
    namespace: str = "default"
    api_key: Optional[str] = None
    async_enabled: bool = True
    batch_size: int = 100
    batch_interval_ms: int = 5000
    max_retries: int = 3
    retry_backoff_ms: int = 1000
    debug_enabled: bool = False
    timeout_ms: int = 30000
    max_connections: int = 10
    headers: Dict[str, str] = field(default_factory=dict)
