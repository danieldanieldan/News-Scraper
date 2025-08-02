from typing import Optional, Dict
import logging
import requests
from news_scraper.utils import (
    find_first_element_by_class_substring,
    html_to_markdown,
    fetch_soup,
)

logger = logging.getLogger(__name__)


def extract_title_and_body(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 3,
    timeout: int = 10
) -> Dict[str, str]:
    """
    Extract the title and body text from a news article given its URL.

    Args:
        url (str): The full URL of the news article.
        headers (dict, optional): Optional HTTP headers to include in the request.
        retries (int): Number of retry attempts in case of request failure.
        timeout (int): Timeout in seconds for the HTTP request.

    Returns:
        dict: A dictionary with keys:
            - 'url': Original article URL
            - 'title': Article headline or a fallback string if extraction failed
            - 'body': Full body text or a fallback string if extraction failed
    """
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            soup = fetch_soup(url, headers=headers, timeout=timeout)

            title_element = find_first_element_by_class_substring(soup, "h1", "index_article-title-h1")
            body_element = (
                find_first_element_by_class_substring(soup, "div", "index_richTextContent")
                or find_first_element_by_class_substring(soup, "div", "index_markdownContent")
            )

            if not title_element:
                raise ValueError("Missing title on the page.")

            if not body_element:
                raise ValueError("Missing body content on the page.")

            title = title_element.get_text(strip=True)
            body = html_to_markdown(str(body_element))

            return {
                "url": url,
                "title": title,
                "body": body
            }

        except (requests.RequestException, ValueError) as e:
            last_error = str(e)
            continue

    # Fallback after all retries failed

    logger.warning("Failed to extract article after %d attempts: %s – %s", retries, url, last_error)
    return {
        "url": url,
        "title": f"Failed to extract title: {last_error}" if last_error else "Failed to extract title",
        "body": f"Failed to extract body: {last_error}" if last_error else "Failed to extract body"
    }

