"""
Free Proxy Server - A professional Python library for fetching proxy lists from RedScrape API.

This library provides both synchronous and asynchronous clients for fetching and filtering
proxy servers from the RedScrape free proxy service.
"""

__version__ = "1.0.0"
__author__ = "RedFree Team"
__email__ = "contact@redfree.com"

from .client import ProxyClient
from .async_client import AsyncProxyClient
from .models import Proxy, ProxyFilter, ProxyResponse
from .exceptions import ProxyServerError, ProxyAPIError, ProxyTimeoutError

__all__ = [
    "ProxyClient",
    "AsyncProxyClient", 
    "Proxy",
    "ProxyFilter",
    "ProxyResponse",
    "ProxyServerError",
    "ProxyAPIError",
    "ProxyTimeoutError",
]