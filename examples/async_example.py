"""
Basic asynchronous usage example for free-proxy-server library.
"""

import asyncio
import aiohttp
from free_proxy_server import AsyncProxyClient, ProxyFilter


async def main():
    """Demonstrate basic asynchronous usage."""
    
    print("Creating AsyncProxyClient...")
    
    # Using async context manager (recommended)
    async with AsyncProxyClient() as client:
        try:
            # 1. Get all proxies asynchronously
            print("\n1. Fetching all proxies...")
            all_proxies = await client.get_proxies()
            print(f"Found {len(all_proxies)} total proxies")
            
            # Show first few proxies
            for i, proxy in enumerate(all_proxies[:3]):
                print(f"  {i+1}. {proxy.address}:{proxy.port} ({proxy.protocol})")
            
            # 2. Get filtered proxies
            print("\n2. Fetching US HTTP proxies with filters...")
            filters = ProxyFilter(
                country="US",
                protocol="http",
                max_timeout=1000,
                working_only=True,
                limit=5
            )
            
            us_proxies = await client.get_proxies(filters)
            print(f"Found {len(us_proxies)} US HTTP proxies")
            
            for proxy in us_proxies:
                print(f"  {proxy.address}:{proxy.port} - {proxy.country} ({proxy.timeout_ms}ms)")
            
            # 3. Test proxy with aiohttp
            if us_proxies:
                print("\n3. Testing proxy with aiohttp...")
                proxy = us_proxies[0]
                print(f"Using proxy: {proxy.url}")
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            "http://httpbin.org/ip",
                            proxy=proxy.url,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                print(f"Success! Response: {result}")
                            else:
                                print(f"Failed with status: {response.status}")
                                
                except Exception as e:
                    print(f"Proxy test failed: {e}")
            
            # 4. Get proxies from multiple countries concurrently
            print("\n4. Fetching proxies from multiple countries concurrently...")
            country_codes = ["US", "GB", "DE", "FR", "CA"]
            
            # This runs all requests concurrently!
            country_proxies = await client.get_multiple_countries(
                country_codes,
                ProxyFilter(protocol="http", limit=2)
            )
            
            for i, proxies in enumerate(country_proxies):
                print(f"  {country_codes[i]}: {len(proxies)} proxies")
            
            # 5. Get working proxies only
            print("\n5. Fetching only working proxies...")
            working_proxies = await client.get_working_proxies()
            print(f"Found {len(working_proxies)} working proxies")
            
            # 6. Get proxy URLs as strings
            print("\n6. Getting proxy URLs...")
            proxy_urls = await client.get_proxy_urls(ProxyFilter(limit=3))
            for url in proxy_urls:
                print(f"  {url}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nClient closed automatically (context manager).")


async def concurrent_example():
    """Demonstrate concurrent operations."""
    
    print("\n" + "="*50)
    print("CONCURRENT OPERATIONS EXAMPLE")
    print("="*50)
    
    async with AsyncProxyClient() as client:
        # Create multiple concurrent tasks
        tasks = [
            client.get_proxies_by_country("US", ProxyFilter(limit=3)),
            client.get_proxies_by_country("GB", ProxyFilter(limit=3)),
            client.get_proxies_by_country("DE", ProxyFilter(limit=3)),
            client.get_working_proxies(ProxyFilter(limit=5)),
        ]
        
        print("Running 4 concurrent proxy requests...")
        start_time = asyncio.get_event_loop().time()
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        
        print(f"Completed in {end_time - start_time:.2f} seconds")
        print(f"Results: {[len(r) for r in results]} proxies respectively")


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Run the concurrent example
    asyncio.run(concurrent_example())