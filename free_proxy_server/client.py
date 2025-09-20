"""Synchronous client for the RedScrape proxy API."""

import requests
from typing import List, Optional, Union
from urllib.parse import urljoin

from .models import Proxy, ProxyFilter, ProxyResponse
from .exceptions import ProxyAPIError, ProxyTimeoutError, ProxyValidationError


class ProxyClient:
    """Synchronous client for fetching proxies from RedScrape API."""
    
    def __init__(self, 
                 base_url: str = "https://free.redscrape.com/api/",
                 timeout: int = 30,
                 user_agent: str = "free-proxy-server/1.0.0"):
        """
        Initialize the proxy client.
        
        Args:
            base_url: Base URL for the RedScrape API
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
        """
        self.base_url = base_url.rstrip('/') + '/'
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_proxies(self, 
                   filters: Optional[Union[ProxyFilter, dict]] = None,
                   raw_response: bool = False) -> Union[ProxyResponse, List[str]]:
        """
        Fetch proxies from the API.
        
        Args:
            filters: Filtering options for the request
            raw_response: If True, return raw text response instead of parsed objects
            
        Returns:
            ProxyResponse object containing parsed proxies or list of proxy strings
            
        Raises:
            ProxyAPIError: If the API returns an error
            ProxyTimeoutError: If the request times out
            ProxyValidationError: If response data is invalid
        """
        try:
            url = urljoin(self.base_url, 'proxies')
            params = {}
            
            # Handle filters
            if filters:
                if isinstance(filters, dict):
                    params = filters
                elif isinstance(filters, ProxyFilter):
                    params = filters.to_params()
                else:
                    raise ProxyValidationError("Filters must be ProxyFilter object or dict")
            
            # Make the request
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Check for HTTP errors
            if response.status_code != 200:
                raise ProxyAPIError(
                    f"API request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            
            # Handle different response formats
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                return self._parse_json_response(response.json(), filters)
            else:
                # Handle plain text response
                if raw_response:
                    return response.text.strip().split('\n')
                else:
                    return self._parse_text_response(response.text, filters)
                    
        except requests.exceptions.Timeout:
            raise ProxyTimeoutError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise ProxyAPIError(f"Request failed: {str(e)}")
    
    def _parse_json_response(self, data: Union[list, dict], filters: Optional[Union[ProxyFilter, dict]]) -> ProxyResponse:
        """Parse JSON response into ProxyResponse object."""
        try:
            proxies = []
            
            if isinstance(data, list):
                # List of proxy objects
                for item in data:
                    if isinstance(item, dict):
                        proxy = Proxy(**item)
                        proxies.append(proxy)
                    else:
                        raise ProxyValidationError(f"Invalid proxy data format: {item}")
            elif isinstance(data, dict):
                # Single proxy object or wrapped response
                if 'proxies' in data:
                    for item in data['proxies']:
                        proxy = Proxy(**item)
                        proxies.append(proxy)
                else:
                    proxy = Proxy(**data)
                    proxies.append(proxy)
            else:
                raise ProxyValidationError(f"Unexpected response format: {type(data)}")
            
            return ProxyResponse(
                proxies=proxies,
                total_count=len(proxies),
                filters_applied=filters.to_params() if isinstance(filters, ProxyFilter) else filters
            )
            
        except Exception as e:
            raise ProxyValidationError(f"Failed to parse API response: {str(e)}")
    
    def _parse_text_response(self, text: str, filters: Optional[Union[ProxyFilter, dict]]) -> ProxyResponse:
        """Parse plain text response into ProxyResponse object."""
        try:
            proxies = []
            lines = text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse IP:PORT format
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        address = parts[0].strip()
                        try:
                            port = int(parts[1].strip())
                            proxy = Proxy(
                                address=address,
                                port=port,
                                protocol='http'  # Default protocol for text format
                            )
                            proxies.append(proxy)
                        except ValueError:
                            continue  # Skip invalid port numbers
            
            return ProxyResponse(
                proxies=proxies,
                total_count=len(proxies),
                filters_applied=filters.to_params() if isinstance(filters, ProxyFilter) else filters
            )
            
        except Exception as e:
            raise ProxyValidationError(f"Failed to parse text response: {str(e)}")
    
    def get_proxy_urls(self, filters: Optional[Union[ProxyFilter, dict]] = None) -> List[str]:
        """
        Get a list of proxy URLs in format protocol://address:port.
        
        Args:
            filters: Filtering options for the request
            
        Returns:
            List of proxy URLs
        """
        response = self.get_proxies(filters)
        return [proxy.url for proxy in response.proxies]
    
    def get_proxy_dicts(self, filters: Optional[Union[ProxyFilter, dict]] = None) -> List[dict]:
        """
        Get a list of proxy dictionaries suitable for use with requests library.
        
        Args:
            filters: Filtering options for the request
            
        Returns:
            List of proxy dictionaries
        """
        response = self.get_proxies(filters)
        return [proxy.proxy_dict for proxy in response.proxies]
    
    def get_working_proxies(self, filters: Optional[Union[ProxyFilter, dict]] = None) -> ProxyResponse:
        """
        Get only working proxies.
        
        Args:
            filters: Filtering options for the request
            
        Returns:
            ProxyResponse object containing only working proxies
        """
        if filters is None:
            filters = ProxyFilter(working_only=True)
        elif isinstance(filters, dict):
            filters['working_only'] = True
        elif isinstance(filters, ProxyFilter):
            filters.working_only = True
        
        return self.get_proxies(filters)
    
    def get_proxies_by_country(self, country_code: str, 
                              additional_filters: Optional[Union[ProxyFilter, dict]] = None) -> ProxyResponse:
        """
        Get proxies from a specific country.
        
        Args:
            country_code: Two-letter country code (e.g., 'US', 'GB')
            additional_filters: Additional filtering options
            
        Returns:
            ProxyResponse object containing proxies from the specified country
        """
        if additional_filters is None:
            filters = ProxyFilter(country=country_code)
        elif isinstance(additional_filters, dict):
            additional_filters['country'] = country_code
            filters = additional_filters
        elif isinstance(additional_filters, ProxyFilter):
            additional_filters.country = country_code
            filters = additional_filters
        
        return self.get_proxies(filters)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()