from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="free-proxy-server",
    version="1.0.0",
    author="RedFree Team",
    author_email="contact@redfree.com",
    description="A professional Python library for fetching proxy lists from RedScrape API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redfree/free-proxy-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    keywords="proxy, scraping, redscrape, http, socks, async, sync",
    project_urls={
        "Bug Reports": "https://github.com/redfree/free-proxy-server/issues",
        "Source": "https://github.com/redfree/free-proxy-server",
        "Documentation": "https://free-proxy-server.readthedocs.io/",
    },
)