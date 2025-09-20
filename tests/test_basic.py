"""
Simple test to verify the library imports and basic functionality.
"""

import pytest
from free_proxy_server import (
    ProxyClient,
    AsyncProxyClient,
    Proxy,
    ProxyFilter,
    ProxyResponse,
    ProxyServerError,
    ProxyAPIError,
    ProxyTimeoutError
)


def test_imports():
    """Test that all main classes can be imported."""
    assert ProxyClient is not None
    assert AsyncProxyClient is not None
    assert Proxy is not None
    assert ProxyFilter is not None
    assert ProxyResponse is not None


def test_proxy_model():
    """Test Proxy model creation and properties."""
    proxy = Proxy(
        address="192.168.1.1",
        port=8080,
        protocol="http"
    )
    
    assert proxy.address == "192.168.1.1"
    assert proxy.port == 8080
    assert proxy.protocol == "http"
    assert proxy.url == "http://192.168.1.1:8080"
    assert str(proxy) == "192.168.1.1:8080"
    
    proxy_dict = proxy.proxy_dict
    assert proxy_dict["http"] == "http://192.168.1.1:8080"
    assert proxy_dict["https"] == "http://192.168.1.1:8080"


def test_proxy_filter():
    """Test ProxyFilter model and parameter conversion."""
    filters = ProxyFilter(
        country="US",
        protocol="http",
        max_timeout=1000,
        limit=50
    )
    
    params = filters.to_params()
    assert params["country"] == "US"
    assert params["protocol"] == "http"
    assert params["max_timeout"] == 1000
    assert params["limit"] == 50


def test_proxy_response():
    """Test ProxyResponse model."""
    proxies = [
        Proxy(address="192.168.1.1", port=8080, protocol="http"),
        Proxy(address="192.168.1.2", port=8080, protocol="http"),
    ]
    
    response = ProxyResponse(proxies=proxies, total_count=2)
    
    assert len(response) == 2
    assert response.total_count == 2
    assert response[0].address == "192.168.1.1"
    
    # Test iteration
    addresses = [proxy.address for proxy in response]
    assert addresses == ["192.168.1.1", "192.168.1.2"]


def test_client_creation():
    """Test that clients can be created."""
    sync_client = ProxyClient()
    assert sync_client.base_url == "https://free.redscrape.com/api/"
    assert sync_client.timeout == 30
    
    async_client = AsyncProxyClient()
    assert async_client.base_url == "https://free.redscrape.com/api/"
    assert async_client.timeout.total == 30


def test_exception_hierarchy():
    """Test exception hierarchy."""
    assert issubclass(ProxyAPIError, ProxyServerError)
    assert issubclass(ProxyTimeoutError, ProxyServerError)
    
    # Test ProxyAPIError with status code
    error = ProxyAPIError("Test error", status_code=404)
    assert str(error) == "Test error"
    assert error.status_code == 404


if __name__ == "__main__":
    # Run basic tests
    test_imports()
    test_proxy_model()
    test_proxy_filter()
    test_proxy_response()
    test_client_creation()
    test_exception_hierarchy()
    
    print("✓ All basic tests passed!")
    print("Library is properly configured and ready to use.")