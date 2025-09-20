"""Custom exceptions for the free-proxy-server library."""


class ProxyServerError(Exception):
    """Base exception for all proxy server related errors."""
    pass


class ProxyAPIError(ProxyServerError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ProxyTimeoutError(ProxyServerError):
    """Raised when a request to the proxy API times out."""
    pass


class ProxyValidationError(ProxyServerError):
    """Raised when proxy data validation fails."""
    pass