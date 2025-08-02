from bs4 import BeautifulSoup, Tag
from typing import Optional
import html2text
import requests
import logging

logger = logging.getLogger(__name__)

def find_first_element_by_class_substring(
    soup: BeautifulSoup,
    tag: str,
    class_substring: str
) -> Optional[Tag]:
    """
    Find the first HTML element of a given tag where the class attribute contains a specific substring.

    Args:
        soup (BeautifulSoup): A BeautifulSoup-parsed HTML document.
        tag (str): The name of the HTML tag to search for (e.g., 'h1', 'div').
        class_substring (str): Substring to look for within the class attribute.

    Returns:
        Optional[Tag]: The first BeautifulSoup Tag matching the criteria, or None if not found.
    """
    return soup.find(
        tag,
        class_=lambda c: c and class_substring in c
    )


def html_to_markdown(html: str, ignore_links: bool = False, ignore_images: bool = True) -> str:
    """
    Convert an HTML string to Markdown-style plain text.
    Falls back to raw text if conversion fails.

    Args:
        html (str): Raw HTML content to convert.
        ignore_links (bool): Whether to omit hyperlinks in the output (default: False).
        ignore_images (bool): Whether to omit image tags from the output (default: True).

    Returns:
        str: Cleaned Markdown-style text, or plain text fallback if conversion fails.
    """
    try:
        converter = html2text.HTML2Text()
        converter.ignore_links = ignore_links
        converter.ignore_images = ignore_images
        converter.ignore_emphasis = False  
        converter.bypass_tables = False

        return converter.handle(html)

    except Exception as e:
        logger.warning("html2text failed, falling back to plain text: %s", e)
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    

def fetch_soup(url: str, headers: Optional[dict] = None, timeout: int = 10) -> BeautifulSoup:
    """
    Makes an HTTP GET request to the given URL and returns a BeautifulSoup object.

    Args:
        url (str): The full URL to fetch.
        headers (dict, optional): Optional headers to include (e.g., User-Agent).
        timeout (int): Timeout in seconds (default: 10).

    Returns:
        BeautifulSoup: Parsed HTML content of the response.

    Raises:
        requests.RequestException: If the request fails.
    """

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Request failed for %s: %s", url, e)
        raise
    return BeautifulSoup(response.text, "html.parser")

