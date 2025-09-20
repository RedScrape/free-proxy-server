"""
Advanced usage examples for free-proxy-server library.
Demonstrates proxy validation, rotation, and custom formatting.
"""

import asyncio
from free_proxy_server import (
    ProxyClient, 
    AsyncProxyClient,
    ProxyFilter,
    ProxyValidator,
    ProxyRotator,
    ProxyFormatter
)


def validation_example():
    """Demonstrate proxy validation."""
    print("="*50)
    print("PROXY VALIDATION EXAMPLE")
    print("="*50)
    
    # Get some proxies
    client = ProxyClient()
    proxies = client.get_proxies(ProxyFilter(limit=5))
    client.close()
    
    print(f"Testing {len(proxies)} proxies...")
    
    # Create validator
    validator = ProxyValidator(timeout=5, test_url="http://httpbin.org/ip")
    
    # Test each proxy
    for i, proxy in enumerate(proxies, 1):
        print(f"{i}. Testing {proxy.address}:{proxy.port}...", end=" ")
        is_working = validator.validate_proxy(proxy)
        print("✓ Working" if is_working else "✗ Failed")
    
    # Validate all at once
    print("\nValidating all proxies...")
    working_proxies = validator.validate_proxies(proxies)
    print(f"Found {len(working_proxies)} working proxies out of {len(proxies)}")


async def async_validation_example():
    """Demonstrate async proxy validation."""
    print("\n" + "="*50)
    print("ASYNC PROXY VALIDATION EXAMPLE")
    print("="*50)
    
    # Get some proxies
    async with AsyncProxyClient() as client:
        proxies = await client.get_proxies(ProxyFilter(limit=10))
    
    print(f"Testing {len(proxies)} proxies asynchronously...")
    
    # Create validator
    validator = ProxyValidator(timeout=5)
    
    # Validate asynchronously with concurrency control
    working_proxies = await validator.validate_proxies_async(
        proxies, 
        max_concurrent=5
    )
    
    print(f"Found {len(working_proxies)} working proxies out of {len(proxies)}")
    for proxy in working_proxies[:3]:
        print(f"  ✓ {proxy.address}:{proxy.port}")


def rotation_example():
    """Demonstrate proxy rotation."""
    print("\n" + "="*50)
    print("PROXY ROTATION EXAMPLE")
    print("="*50)
    
    # Get some proxies
    client = ProxyClient()
    proxies = client.get_proxies(ProxyFilter(limit=5))
    client.close()
    
    # Create rotator
    rotator = ProxyRotator(proxies)
    print(f"Created rotator with {rotator.size()} proxies")
    
    # Demonstrate rotation
    print("\nRotating through proxies:")
    for i in range(8):  # More than we have proxies to show rotation
        proxy = rotator.get_next()
        print(f"  {i+1}. {proxy.address}:{proxy.port}")
    
    # Demonstrate random selection
    print("\nRandom proxy selection:")
    for i in range(3):
        proxy = rotator.get_random()
        print(f"  {i+1}. {proxy.address}:{proxy.port}")
    
    # Remove a proxy (simulate failure)
    if not rotator.is_empty():
        removed_proxy = proxies[0]
        success = rotator.remove_proxy(removed_proxy)
        print(f"\nRemoved proxy {removed_proxy}: {success}")
        print(f"Rotator now has {rotator.size()} proxies")


def formatting_example():
    """Demonstrate different proxy formatting options."""
    print("\n" + "="*50)
    print("PROXY FORMATTING EXAMPLE")
    print("="*50)
    
    # Get some proxies
    client = ProxyClient()
    proxies = client.get_proxies(ProxyFilter(limit=3))
    client.close()
    
    print(f"Formatting {len(proxies)} proxies...")
    
    # Simple list format
    print("\n1. Simple address:port format:")
    simple_list = ProxyFormatter.to_simple_list(proxies)
    for proxy_str in simple_list:
        print(f"  {proxy_str}")
    
    # Curl format
    print("\n2. Curl format:")
    curl_format = ProxyFormatter.to_curl_format(proxies)
    for curl_str in curl_format:
        print(f"  {curl_str}")
    
    # Requests format
    print("\n3. Requests library format:")
    requests_format = ProxyFormatter.to_requests_format(proxies)
    for i, proxy_dict in enumerate(requests_format):
        print(f"  {i+1}. {proxy_dict}")
    
    # CSV format
    print("\n4. CSV format:")
    csv_data = ProxyFormatter.to_csv(proxies, include_headers=True)
    print(csv_data)


def filtering_examples():
    """Demonstrate advanced filtering."""
    print("\n" + "="*50)
    print("ADVANCED FILTERING EXAMPLES")
    print("="*50)
    
    client = ProxyClient()
    
    try:
        # Example 1: Fast HTTP proxies from US
        print("1. Fast US HTTP proxies (< 500ms):")
        fast_us = client.get_proxies(ProxyFilter(
            country="US",
            protocol="http",
            max_timeout=500,
            working_only=True,
            limit=3
        ))
        for proxy in fast_us:
            print(f"  {proxy.address}:{proxy.port} - {proxy.timeout_ms}ms")
        
        # Example 2: SOCKS5 proxies
        print("\n2. SOCKS5 proxies:")
        socks_proxies = client.get_proxies(ProxyFilter(
            protocol="socks5",
            limit=3
        ))
        for proxy in socks_proxies:
            print(f"  {proxy.address}:{proxy.port} ({proxy.protocol})")
        
        # Example 3: Specific timeout range
        print("\n3. Proxies with timeout 100-800ms:")
        timeout_range = client.get_proxies(ProxyFilter(
            min_timeout=100,
            max_timeout=800,
            limit=3
        ))
        for proxy in timeout_range:
            timeout = proxy.timeout_ms or "Unknown"
            print(f"  {proxy.address}:{proxy.port} - {timeout}ms")
        
        # Example 4: Multiple countries
        print("\n4. Proxies from specific countries:")
        for country in ["GB", "DE", "FR"]:
            country_proxies = client.get_proxies_by_country(
                country, 
                ProxyFilter(limit=2)
            )
            print(f"  {country}: {len(country_proxies)} proxies")
            
    finally:
        client.close()


def main():
    """Run all examples."""
    validation_example()
    asyncio.run(async_validation_example())
    rotation_example()
    formatting_example()
    filtering_examples()


if __name__ == "__main__":
    main()