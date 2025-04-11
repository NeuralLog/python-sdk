"""
HTTP client for the NeuralLog SDK.
"""

import json
import time
from typing import Dict, Any, Optional
import requests

from neurallog_sdk.models.neurallog_config import NeuralLogConfig


class HttpClient:
    """HTTP client for the NeuralLog SDK."""
    
    def __init__(self, config: NeuralLogConfig):
        """Initialize the HTTP client.
        
        Args:
            config: The NeuralLog configuration.
        """
        self.config = config
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Set API key if provided
        if config.api_key:
            self.session.headers.update({
                "X-API-Key": config.api_key
            })
        
        # Set custom headers
        if config.headers:
            self.session.headers.update(config.headers)
    
    def send(self, method: str, url: str, data: Optional[str] = None) -> Dict[str, Any]:
        """Send an HTTP request.
        
        Args:
            method: The HTTP method to use.
            url: The URL to send the request to.
            data: The request body as a JSON string.
            
        Returns:
            The response body as a dictionary.
            
        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        retries = 0
        last_exception = None
        
        while retries <= self.config.max_retries:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    timeout=self.config.timeout_ms / 1000
                )
                response.raise_for_status()
                
                if response.status_code == 204:  # No content
                    return {}
                
                return response.json()
            except requests.exceptions.RequestException as e:
                last_exception = e
                retries += 1
                
                if retries <= self.config.max_retries:
                    # Wait with exponential backoff
                    backoff = self.config.retry_backoff_ms * (2 ** (retries - 1)) / 1000
                    time.sleep(backoff)
                    
                    if self.config.debug_enabled:
                        print(f"Retrying request ({retries}/{self.config.max_retries})...")
        
        if self.config.debug_enabled and last_exception:
            print(f"Request failed after {self.config.max_retries} retries: {last_exception}")
            
        raise last_exception
