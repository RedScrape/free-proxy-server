# Free Proxy Server

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/free-proxy-server.svg)](https://badge.fury.io/py/free-proxy-server)

A professional Python library for fetching proxy lists from the RedScrape API. This library provides both synchronous and asynchronous clients for seamless integration into your applications.

## Features

- 🚀 **Both Sync & Async Support** - Choose the right approach for your use case
- 🎯 **Advanced Filtering** - Filter by country, protocol, timeout, and more
- 🔧 **Type Safety** - Full type hints with Pydantic models
- ⚡ **High Performance** - Efficient HTTP clients with connection pooling
- 🛡️ **Error Handling** - Comprehensive exception handling
- 📊 **Proxy Validation** - Built-in proxy testing and validation utilities
- 🔄 **Proxy Rotation** - Smart proxy rotation and management
- 📝 **Rich Data Models** - Structured proxy data with validation

## Installation

```bash
pip install free-proxy-server
```

For development dependencies:
```bash
pip install free-proxy-server[dev]
```

## Quick Start

### Synchronous Usage

```python
from free_proxy_server import ProxyClient, ProxyFilter

# Create a client
client = ProxyClient()

# Get all proxies
proxies = client.get_proxies()
print(f"Found {len(proxies)} proxies")

# Get US proxies with filters
filters = ProxyFilter(
    country="US",
    protocol="http",
    max_timeout=1000,
    working_only=True
)
us_proxies = client.get_proxies(filters)

# Use with requests
import requests
proxy = us_proxies[0]
response = requests.get("http://httpbin.org/ip", proxies=proxy.proxy_dict)
print(response.json())
```

### Asynchronous Usage

```python
import asyncio
from free_proxy_server import AsyncProxyClient, ProxyFilter

async def main():
    # Create async client
    async with AsyncProxyClient() as client:
        # Get proxies asynchronously
        filters = ProxyFilter(country="US", protocol="http")
        proxies = await client.get_proxies(filters)
        
        # Get multiple countries concurrently
        country_proxies = await client.get_multiple_countries(["US", "GB", "DE"])
        
        print(f"Found {sum(len(p) for p in country_proxies)} total proxies")

# Run async function
asyncio.run(main())
```

## API Reference

### ProxyClient (Synchronous)

```python
from free_proxy_server import ProxyClient

client = ProxyClient(
    base_url="https://free.redscrape.com/api/",  # API base URL
    timeout=30,                                   # Request timeout
    user_agent="free-proxy-server/1.0.0"        # User agent string
)
```

#### Methods

- `get_proxies(filters=None, raw_response=False)` - Get filtered proxies
- `get_proxy_urls(filters=None)` - Get proxy URLs as strings
- `get_proxy_dicts(filters=None)` - Get proxy dicts for requests
- `get_working_proxies(filters=None)` - Get only working proxies
- `get_proxies_by_country(country_code, filters=None)` - Get country-specific proxies

### AsyncProxyClient (Asynchronous)

```python
from free_proxy_server import AsyncProxyClient

client = AsyncProxyClient(
    base_url="https://free.redscrape.com/api/",
    timeout=30,
    user_agent="free-proxy-server/1.0.0",
    session=None  # Optional aiohttp session
)
```

#### Methods

Same as ProxyClient but with `async`/`await`:

- `await get_proxies(filters=None, raw_response=False)`
- `await get_proxy_urls(filters=None)`
- `await get_proxy_dicts(filters=None)`
- `await get_working_proxies(filters=None)`
- `await get_proxies_by_country(country_code, filters=None)`
- `await get_multiple_countries(country_codes, filters=None)` - Concurrent fetching

### ProxyFilter

```python
from free_proxy_server import ProxyFilter

filters = ProxyFilter(
    country="US",           # Country code (e.g., "US", "GB")
    protocol="http",        # Protocol: http, https, socks4, socks5
    max_timeout=1000,      # Maximum timeout in milliseconds
    min_timeout=100,       # Minimum timeout in milliseconds
    format="json",         # Response format: json, txt
    limit=50,              # Maximum number of proxies
    working_only=True      # Only return working proxies
)
```

### Proxy Model

```python
proxy = proxies[0]

# Properties
print(proxy.address)        # IP address
print(proxy.port)          # Port number
print(proxy.protocol)      # Protocol type
print(proxy.country)       # Country name
print(proxy.country_code)  # Country code
print(proxy.timeout_ms)    # Timeout in milliseconds
print(proxy.is_working)    # Working status
print(proxy.last_checked)  # Last check timestamp

# Methods
print(proxy.url)           # Full URL: protocol://address:port
print(proxy.proxy_dict)    # Dict for requests library
print(str(proxy))          # address:port format
```

## Advanced Usage

### Proxy Validation

```python
from free_proxy_server import ProxyValidator

validator = ProxyValidator(timeout=10, test_url="http://httpbin.org/ip")

# Validate single proxy
is_working = validator.validate_proxy(proxy)

# Validate multiple proxies
working_proxies = validator.validate_proxies(proxy_list)

# Async validation
async def validate_async():
    working_proxies = await validator.validate_proxies_async(
        proxy_list,
        max_concurrent=10
    )
```

### Proxy Rotation

```python
from free_proxy_server import ProxyRotator

rotator = ProxyRotator(proxy_list)

# Get next proxy in rotation
proxy = rotator.get_next()

# Get random proxy
proxy = rotator.get_random()

# Remove failed proxy
rotator.remove_proxy(failed_proxy)

# Add new proxy
rotator.add_proxy(new_proxy)
```

### Custom Formatting

```python
from free_proxy_server import ProxyFormatter

# Format for curl
curl_proxies = ProxyFormatter.to_curl_format(proxies)

# Format for requests
request_proxies = ProxyFormatter.to_requests_format(proxies)

# Simple address:port list
simple_list = ProxyFormatter.to_simple_list(proxies)

# CSV format
csv_data = ProxyFormatter.to_csv(proxies, include_headers=True)
```

### Error Handling

```python
from free_proxy_server import (
    ProxyClient, 
    ProxyAPIError, 
    ProxyTimeoutError, 
    ProxyValidationError
)

try:
    client = ProxyClient()
    proxies = client.get_proxies()
except ProxyAPIError as e:
    print(f"API Error: {e} (Status: {e.status_code})")
except ProxyTimeoutError as e:
    print(f"Timeout Error: {e}")
except ProxyValidationError as e:
    print(f"Validation Error: {e}")
```

## Examples

### Using with Different HTTP Libraries

#### With requests
```python
proxy = client.get_proxies()[0]
response = requests.get("http://httpbin.org/ip", proxies=proxy.proxy_dict)
```

#### With httpx
```python
import httpx
proxy = client.get_proxies()[0]
with httpx.Client(proxies=proxy.url) as client:
    response = client.get("http://httpbin.org/ip")
```

#### With aiohttp
```python
import aiohttp
proxy = await async_client.get_proxies()
async with aiohttp.ClientSession() as session:
    async with session.get("http://httpbin.org/ip", proxy=proxy[0].url) as response:
        data = await response.json()
```

### Filtering Examples

```python
# Get fast US HTTP proxies
fast_us_proxies = client.get_proxies(ProxyFilter(
    country="US",
    protocol="http",
    max_timeout=500,
    working_only=True
))

# Get SOCKS proxies from multiple countries
socks_proxies = client.get_proxies(ProxyFilter(
    protocol="socks5",
    working_only=True,
    limit=20
))

# Get proxies with custom parameters
custom_proxies = client.get_proxies({
    "country": "GB",
    "max_timeout": 1000,
    "format": "json"
})
```

## API Response Examples

### JSON Response Format
```json
[
  {
    "address": "35.222.31.167",
    "port": 80,
    "protocol": "http",
    "country": "United States",
    "country_code": "US",
    "timeout_ms": 590,
    "is_working": true,
    "last_checked": "2025-09-20T01:49:26.531472616Z"
  }
]
```

### Text Response Format
```
201.174.239.25:8080
190.242.157.215:8080
104.238.30.17:54112
37.200.67.75:1080
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/redscrape/free-proxy-server.git
cd free-proxy-server

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
black .
isort .
flake8 .
mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: contact@redscrape.com
- 🐛 Issues: [GitHub Issues](https://github.com/redscrape/free-proxy-server/issues)
- 📖 Documentation: [Read the Docs](https://free-proxy-server.readthedocs.io/)

## Changelog

### v1.0.0
- Initial release
- Synchronous and asynchronous proxy clients
- Advanced filtering and validation
- Comprehensive documentation and examples