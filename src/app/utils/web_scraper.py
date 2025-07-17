import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

async def fetch_html_content(url: str, timeout: int = 10) -> str:
    """Fetches HTML content from a given URL."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (compatible; YourAppName/1.0)"})
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            return response.text
    except httpx.RequestError as exc:
        logger.error(f"HTTPX request error for {url}: {exc}")
        raise ValueError(f"Could not fetch content from URL: {exc.detail}")
    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP error {exc.response.status_code} for {url}: {exc.response.text}")
        raise ValueError(f"Failed to fetch content, status code: {exc.response.status_code}")
    except Exception as exc:
        logger.error(f"An unexpected error occurred while fetching {url}: {exc}")
        raise ValueError(f"An unexpected error occurred: {exc}")

def extract_text_from_html(html_content: str) -> str:
    """Extracts readable text content from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script, style, and other non-visible elements
    for script_or_style in soup(["script", "style", "header", "footer", "nav", "form", "aside"]):
        script_or_style.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text