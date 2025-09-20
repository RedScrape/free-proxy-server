"""Configuration and utility functions for the free-proxy-server library."""

import socket
import requests
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from .models import Proxy
from .exceptions import ProxyValidationError, ProxyTimeoutError


class ProxyValidator:
    """Utility class for validating proxy functionality."""
    
    def __init__(self, timeout: int = 10, test_url: str = "http://httpbin.org/ip"):
        """
        Initialize the proxy validator.
        
        Args:
            timeout: Timeout for validation requests in seconds
            test_url: URL to use for testing proxy functionality
        """
        self.timeout = timeout
        self.test_url = test_url
    
    def validate_proxy(self, proxy: Proxy) -> bool:
        """
        Validate a single proxy by making a test request.
        
        Args:
            proxy: Proxy object to validate
            
        Returns:
            True if proxy is working, False otherwise
        """
        try:
            proxies = proxy.proxy_dict
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=self.timeout,
                headers={'User-Agent': 'free-proxy-server/1.0.0'}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def validate_proxies(self, proxies: List[Proxy]) -> List[Proxy]:
        """
        Validate a list of proxies and return only working ones.
        
        Args:
            proxies: List of Proxy objects to validate
            
        Returns:
            List of working Proxy objects
        """
        working_proxies = []
        for proxy in proxies:
            if self.validate_proxy(proxy):
                working_proxies.append(proxy)
        return working_proxies
    
    async def validate_proxy_async(self, proxy: Proxy, session: Optional[aiohttp.ClientSession] = None) -> bool:
        """
        Validate a single proxy asynchronously.
        
        Args:
            proxy: Proxy object to validate
            session: Optional aiohttp session to use
            
        Returns:
            True if proxy is working, False otherwise
        """
        try:
            close_session = False
            if session is None:
                session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
                close_session = True
            
            try:
                async with session.get(
                    self.test_url,
                    proxy=proxy.url,
                    headers={'User-Agent': 'free-proxy-server/1.0.0'}
                ) as response:
                    return response.status == 200
            finally:
                if close_session:
                    await session.close()
                    
        except Exception:
            return False
    
    async def validate_proxies_async(self, 
                                   proxies: List[Proxy], 
                                   max_concurrent: int = 10) -> List[Proxy]:
        """
        Validate a list of proxies asynchronously.
        
        Args:
            proxies: List of Proxy objects to validate
            max_concurrent: Maximum number of concurrent validation requests
            
        Returns:
            List of working Proxy objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        async def validate_with_semaphore(proxy: Proxy) -> Optional[Proxy]:
            async with semaphore:
                is_working = await self.validate_proxy_async(proxy, session)
                return proxy if is_working else None
        
        try:
            tasks = [validate_with_semaphore(proxy) for proxy in proxies]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            working_proxies = []
            for result in results:
                if isinstance(result, Proxy):
                    working_proxies.append(result)
            
            return working_proxies
        finally:
            await session.close()


class ProxyFormatter:
    """Utility class for formatting proxy data."""
    
    @staticmethod
    def to_curl_format(proxies: List[Proxy]) -> List[str]:
        """
        Format proxies for use with curl.
        
        Args:
            proxies: List of Proxy objects
            
        Returns:
            List of curl proxy strings
        """
        return [f"--proxy {proxy.url}" for proxy in proxies]
    
    @staticmethod
    def to_requests_format(proxies: List[Proxy]) -> List[Dict[str, str]]:
        """
        Format proxies for use with requests library.
        
        Args:
            proxies: List of Proxy objects
            
        Returns:
            List of proxy dictionaries for requests
        """
        return [proxy.proxy_dict for proxy in proxies]
    
    @staticmethod
    def to_simple_list(proxies: List[Proxy]) -> List[str]:
        """
        Format proxies as simple address:port strings.
        
        Args:
            proxies: List of Proxy objects
            
        Returns:
            List of address:port strings
        """
        return [str(proxy) for proxy in proxies]
    
    @staticmethod
    def to_csv(proxies: List[Proxy], include_headers: bool = True) -> str:
        """
        Format proxies as CSV string.
        
        Args:
            proxies: List of Proxy objects
            include_headers: Whether to include CSV headers
            
        Returns:
            CSV formatted string
        """
        lines = []
        
        if include_headers:
            lines.append("address,port,protocol,country,country_code,timeout_ms,is_working")
        
        for proxy in proxies:
            line = f"{proxy.address},{proxy.port},{proxy.protocol},"
            line += f"{proxy.country or ''},"
            line += f"{proxy.country_code or ''},"
            line += f"{proxy.timeout_ms or ''},"
            line += f"{proxy.is_working or ''}"
            lines.append(line)
        
        return '\n'.join(lines)


class ProxyRotator:
    """Utility class for rotating through a list of proxies."""
    
    def __init__(self, proxies: List[Proxy]):
        """
        Initialize the proxy rotator.
        
        Args:
            proxies: List of Proxy objects to rotate through
        """
        self.proxies = proxies
        self.current_index = 0
    
    def get_next(self) -> Optional[Proxy]:
        """
        Get the next proxy in rotation.
        
        Returns:
            Next Proxy object or None if list is empty
        """
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_random(self) -> Optional[Proxy]:
        """
        Get a random proxy from the list.
        
        Returns:
            Random Proxy object or None if list is empty
        """
        if not self.proxies:
            return None
        
        import random
        return random.choice(self.proxies)
    
    def remove_proxy(self, proxy: Proxy) -> bool:
        """
        Remove a proxy from the rotation list.
        
        Args:
            proxy: Proxy object to remove
            
        Returns:
            True if proxy was removed, False if not found
        """
        try:
            index = self.proxies.index(proxy)
            self.proxies.pop(index)
            
            # Adjust current index if necessary
            if index <= self.current_index and self.current_index > 0:
                self.current_index -= 1
            
            # Reset index if we're at the end
            if self.current_index >= len(self.proxies) and self.proxies:
                self.current_index = 0
            
            return True
        except ValueError:
            return False
    
    def add_proxy(self, proxy: Proxy):
        """
        Add a proxy to the rotation list.
        
        Args:
            proxy: Proxy object to add
        """
        self.proxies.append(proxy)
    
    def size(self) -> int:
        """Get the number of proxies in rotation."""
        return len(self.proxies)
    
    def is_empty(self) -> bool:
        """Check if the rotation list is empty."""
        return len(self.proxies) == 0


def is_valid_ip(ip: str) -> bool:
    """
    Check if a string is a valid IP address.
    
    Args:
        ip: String to validate
        
    Returns:
        True if valid IP address, False otherwise
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_port(port: int) -> bool:
    """
    Check if a port number is valid.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid port, False otherwise
    """
    return 1 <= port <= 65535


def parse_proxy_url(url: str) -> Proxy:
    """
    Parse a proxy URL into a Proxy object.
    
    Args:
        url: Proxy URL in format protocol://address:port
        
    Returns:
        Proxy object
        
    Raises:
        ProxyValidationError: If URL format is invalid
    """
    try:
        parsed = urlparse(url)
        
        if not parsed.hostname or not parsed.port:
            raise ProxyValidationError(f"Invalid proxy URL format: {url}")
        
        if not is_valid_ip(parsed.hostname):
            raise ProxyValidationError(f"Invalid IP address: {parsed.hostname}")
        
        if not is_valid_port(parsed.port):
            raise ProxyValidationError(f"Invalid port number: {parsed.port}")
        
        protocol = parsed.scheme or 'http'
        
        return Proxy(
            address=parsed.hostname,
            port=parsed.port,
            protocol=protocol
        )
        
    except Exception as e:
        raise ProxyValidationError(f"Failed to parse proxy URL: {str(e)}")


def filter_proxies_by_country(proxies: List[Proxy], country_codes: List[str]) -> List[Proxy]:
    """
    Filter proxies by country codes.
    
    Args:
        proxies: List of Proxy objects
        country_codes: List of country codes to filter by
        
    Returns:
        Filtered list of Proxy objects
    """
    country_codes_upper = [code.upper() for code in country_codes]
    return [
        proxy for proxy in proxies 
        if proxy.country_code and proxy.country_code.upper() in country_codes_upper
    ]


def filter_proxies_by_timeout(proxies: List[Proxy], max_timeout: int) -> List[Proxy]:
    """
    Filter proxies by maximum timeout.
    
    Args:
        proxies: List of Proxy objects
        max_timeout: Maximum timeout in milliseconds
        
    Returns:
        Filtered list of Proxy objects
    """
    return [
        proxy for proxy in proxies 
        if proxy.timeout_ms is not None and proxy.timeout_ms <= max_timeout
    ]