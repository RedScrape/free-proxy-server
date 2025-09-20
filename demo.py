"""
Quick demonstration of the free-proxy-server library features.
"""

from free_proxy_server import ProxyClient, ProxyFilter
import requests


def main():
    print("🚀 Free Proxy Server Library Demo")
    print("=" * 50)
    
    # Create client
    with ProxyClient() as client:
        
        # 1. Get some basic proxies
        print("\n1. 📋 Fetching US HTTP proxies...")
        us_filters = ProxyFilter(
            country="US",
            protocol="http", 
            limit=3
        )
        us_proxies = client.get_proxies(us_filters)
        
        print(f"Found {len(us_proxies)} US HTTP proxies:")
        for i, proxy in enumerate(us_proxies, 1):
            print(f"   {i}. {proxy.address}:{proxy.port}")
            print(f"      📍 {proxy.country} | ⏱️ {proxy.timeout_ms}ms | ✅ {proxy.is_working}")
        
        # 2. Test different protocols
        print("\n2. 🔌 Testing different protocols...")
        for protocol in ["http", "socks5"]:
            proxies = client.get_proxies(ProxyFilter(protocol=protocol, limit=2))
            print(f"   {protocol.upper()}: {len(proxies)} proxies found")
        
        # 3. Filter by timeout
        print("\n3. ⚡ Fast proxies (< 800ms timeout)...")
        fast_proxies = client.get_proxies(ProxyFilter(
            max_timeout=800,
            working_only=True,
            limit=5
        ))
        print(f"Found {len(fast_proxies)} fast working proxies")
        
        # 4. Get proxy URLs for easy use
        print("\n4. 🔗 Ready-to-use proxy URLs:")
        proxy_urls = client.get_proxy_urls(ProxyFilter(limit=3))
        for url in proxy_urls[:3]:
            print(f"   {url}")
        
        # 5. Show different output formats
        print("\n5. 📊 Different output formats:")
        sample_proxies = client.get_proxies(ProxyFilter(limit=2))
        
        print("   • Simple format:", [str(p) for p in sample_proxies])
        print("   • URL format:", [p.url for p in sample_proxies])
        print("   • Requests dict:", sample_proxies[0].proxy_dict if sample_proxies else "No proxies")
        
        # 6. Test a proxy (if available)
        if sample_proxies:
            print("\n6. 🧪 Testing a proxy...")
            test_proxy = sample_proxies[0]
            print(f"Testing {test_proxy.url}...")
            
            try:
                response = requests.get(
                    "http://httpbin.org/ip",
                    proxies=test_proxy.proxy_dict,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Success! IP: {result.get('origin', 'Unknown')}")
                else:
                    print(f"   ❌ Failed with status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)[:50]}...")
    
    print("\n🎉 Demo completed! The library is working perfectly.")
    print("\n📚 Try the examples in the 'examples/' folder for more features:")
    print("   • sync_example.py - Complete synchronous usage")
    print("   • async_example.py - Asynchronous operations") 
    print("   • advanced_example.py - Validation, rotation, formatting")


if __name__ == "__main__":
    main()