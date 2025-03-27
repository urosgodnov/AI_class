# Session 1: Introduction to Crawl4AI and Basic Web Scraping
#
# Objectives:
# - Install Crawl4AI and understand its core concepts.
# - Fetch web pages and convert HTML content into Markdown.
# - Extract structured data using CSS and LLM-based methods.
#
# Prerequisites (run in terminal before starting):
# pip install crawl4ai
# pip install pydantic
# crawl4ai-setup



# Understanding the Core Concepts:
# AsyncWebCrawler:
# - The AsyncWebCrawler is the primary tool for web scraping provided by Crawl4AI.
# - It uses asynchronous operations (asyncio) for efficient handling of multiple web requests.
#   Important parameters:
#   - max_concurrency: limits concurrent requests (default: automatic).
#   - timeout: sets the maximum wait time for requests (default: 30 seconds).

# BrowserConfig:
# - Allows configuration of browser behaviors like headless mode (no visible browser window),
#   viewport size, user-agent strings, and proxy settings.
# - This configuration is useful for simulating real browser interactions and avoiding detection.
#   Important parameters:
#   - headless: run browser without GUI (default: True).
#   - viewport_width and viewport_height: set browser viewport size.
#   - user_agent: custom user agent for requests.

# CrawlerRunConfig:
# - Manages specific run configurations like extraction strategy, waiting times, caching,
#   and verbose logging for debugging purposes.
#   Important parameters:
#   - extraction_strategy: defines the strategy for data extraction (CSS, LLM-based).
#   - verbose: enables detailed logging (default: False).

# Pydantic:
# - A powerful data validation library that uses Python type annotations.
# - Helps in creating structured data models and ensures data integrity and validation.
# - Automatically generates JSON schemas, making it suitable for structured data extraction tasks.

# Example 1: Basic page crawl and markdown generation

# Import necessary modules
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json

async def basic_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="http://quotes.toscrape.com/")
        if result.success:
            print("Markdown preview:\n", result.markdown[:500])
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(basic_crawl())

