from langchain_core.tools import tool
from firecrawl import scrape_website

@tool
def firecrawl_scrape(url: str) -> str:
    """Scrape content from a website URL using Firecrawl API."""
    return scrape_website(url)
