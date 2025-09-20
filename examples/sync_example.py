"""
Basic synchronous usage example for free-proxy-server library.
"""

from free_proxy_server import ProxyClient, ProxyFilter
import requests


def main():
    """Demonstrate basic synchronous usage."""
    
    # Create a client
    print("Creating ProxyClient...")
    client = ProxyClient()
    
    try:
        # 1. Get all proxies
        print("\n1. Fetching all proxies...")
        all_proxies = client.get_proxies()
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
        
        us_proxies = client.get_proxies(filters)
        print(f"Found {len(us_proxies)} US HTTP proxies")
        
        for proxy in us_proxies:
            print(f"  {proxy.address}:{proxy.port} - {proxy.country} ({proxy.timeout_ms}ms)")
        
        # 3. Use a proxy with requests
        if us_proxies:
            print("\n3. Testing proxy with requests...")
            proxy = us_proxies[0]
            print(f"Using proxy: {proxy.url}")
            
            try:
                response = requests.get(
                    "http://httpbin.org/ip",
                    proxies=proxy.proxy_dict,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Success! Response: {result}")
                else:
                    print(f"Failed with status: {response.status_code}")
                    
            except Exception as e:
                print(f"Proxy test failed: {e}")
        
        # 4. Get proxies by country
        print("\n4. Fetching German proxies...")
        german_proxies = client.get_proxies_by_country("DE")
        print(f"Found {len(german_proxies)} German proxies")
        
        # 5. Get working proxies only
        print("\n5. Fetching only working proxies...")
        working_proxies = client.get_working_proxies()
        print(f"Found {len(working_proxies)} working proxies")
        
        # 6. Get proxy URLs as strings
        print("\n6. Getting proxy URLs...")
        proxy_urls = client.get_proxy_urls(ProxyFilter(limit=3))
        for url in proxy_urls:
            print(f"  {url}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Always close the client
        client.close()
        print("\nClient closed.")


if __name__ == "__main__":
    main()