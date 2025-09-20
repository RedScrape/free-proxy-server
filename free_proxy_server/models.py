"""Data models for the free-proxy-server library using Pydantic."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Proxy(BaseModel):
    """Represents a single proxy server."""
    
    address: str = Field(..., description="The IP address of the proxy")
    port: int = Field(..., ge=1, le=65535, description="The port number of the proxy")
    protocol: str = Field(..., description="The protocol (http, https, socks4, socks5)")
    country: Optional[str] = Field(None, description="The country name where the proxy is located")
    country_code: Optional[str] = Field(None, description="The 2-letter country code")
    timeout_ms: Optional[int] = Field(None, ge=0, description="Response timeout in milliseconds")
    is_working: Optional[bool] = Field(None, description="Whether the proxy is currently working")
    last_checked: Optional[datetime] = Field(None, description="When the proxy was last checked")
    
    @validator('protocol')
    def validate_protocol(cls, v):
        """Validate that protocol is one of the supported types."""
        allowed_protocols = ['http', 'https', 'socks4', 'socks5']
        if v.lower() not in allowed_protocols:
            raise ValueError(f'Protocol must be one of: {", ".join(allowed_protocols)}')
        return v.lower()
    
    @property
    def url(self) -> str:
        """Return the proxy URL in the format protocol://address:port."""
        return f"{self.protocol}://{self.address}:{self.port}"
    
    @property
    def proxy_dict(self) -> dict:
        """Return a dictionary suitable for use with requests library."""
        return {
            'http': self.url,
            'https': self.url
        }
    
    def __str__(self) -> str:
        return f"{self.address}:{self.port}"


class ProxyFilter(BaseModel):
    """Filter options for proxy requests."""
    
    country: Optional[str] = Field(None, description="Filter by country code (e.g., 'US', 'GB')")
    protocol: Optional[str] = Field(None, description="Filter by protocol (http, https, socks4, socks5)")
    max_timeout: Optional[int] = Field(None, ge=0, description="Maximum timeout in milliseconds")
    min_timeout: Optional[int] = Field(None, ge=0, description="Minimum timeout in milliseconds")
    format: Optional[str] = Field('json', description="Response format (json, txt)")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Maximum number of proxies to return")
    working_only: Optional[bool] = Field(None, description="Return only working proxies")
    
    @validator('protocol')
    def validate_protocol(cls, v):
        """Validate that protocol is one of the supported types."""
        if v is not None:
            allowed_protocols = ['http', 'https', 'socks4', 'socks5']
            if v.lower() not in allowed_protocols:
                raise ValueError(f'Protocol must be one of: {", ".join(allowed_protocols)}')
            return v.lower()
        return v
    
    @validator('format')
    def validate_format(cls, v):
        """Validate that format is supported."""
        allowed_formats = ['json', 'txt']
        if v.lower() not in allowed_formats:
            raise ValueError(f'Format must be one of: {", ".join(allowed_formats)}')
        return v.lower()
    
    @validator('min_timeout', 'max_timeout')
    def validate_timeout_range(cls, v, values):
        """Validate timeout range."""
        if 'min_timeout' in values and values['min_timeout'] is not None:
            if v is not None and v < values['min_timeout']:
                raise ValueError('max_timeout must be greater than min_timeout')
        return v
    
    def to_params(self) -> dict:
        """Convert filter to URL parameters."""
        params = {}
        
        if self.country:
            params['country'] = self.country
        if self.protocol:
            params['protocol'] = self.protocol
        if self.max_timeout is not None:
            params['max_timeout'] = self.max_timeout
        if self.min_timeout is not None:
            params['min_timeout'] = self.min_timeout
        if self.format:
            params['format'] = self.format
        if self.limit is not None:
            params['limit'] = self.limit
        if self.working_only is not None:
            params['working_only'] = str(self.working_only).lower()
            
        return params


class ProxyResponse(BaseModel):
    """Response model for proxy API calls."""
    
    proxies: List[Proxy]
    total_count: int = Field(description="Total number of proxies returned")
    filters_applied: Optional[dict] = Field(None, description="Filters that were applied to the request")
    
    def __len__(self) -> int:
        return len(self.proxies)
    
    def __iter__(self):
        return iter(self.proxies)
    
    def __getitem__(self, index):
        return self.proxies[index]