from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from .constants import BASE_DOMAIN
from .utils import fetch_soup


def get_all_categories(archive_homepage_url: str) -> Dict[str, str]:
    """
    Scrapes the OKX announcements category page and returns a dictionary
    of category slugs and their full URLs.

    Args:
        archive_homepage_url (str): The URL of the announcements homepage.

    Returns:
        Dict[str, str]: Keys are category slugs (e.g., 'earn'), values are full URLs.
    """
    soup = fetch_soup(archive_homepage_url)

    category_links = {}

    # Locate the <nav> element labeled as "Announcements"
    nav = soup.find("nav", {"aria-label": "Announcements"})
    if not nav:
        raise ValueError("Could not find announcements navigation on the page.")

    for a in nav.find_all("a", href=True):
        href = a["href"]
        if "/help/section/announcements-" in href:
            # Skip the "Latest announcements" category
            # This category is an aggregate of all news types and is capped at 100 pages,
            # so we cannot rely on it for full coverage. We use individual categories instead.
            if "announcements-latest-announcements" in href:
                continue

            full_url = BASE_DOMAIN + href
            slug = href.split("announcements-")[-1].rstrip("/")
            category_links[slug] = full_url

    return category_links


def get_articles_on_page(category_url: str, page: int) -> Tuple[List[Dict[str, Any]], Optional[int]]:
    """
    Scrapes a single category page and returns:
    - a list of articles on that page
    - total number of pages (only returned when page == 1)

    Args:
        category_url (str): Category base URL.
        page (int): Page number to scrape.

    Returns:
        Tuple:
            - List of dicts: each with 'url' and 'published'
            - Optional[int]: total number of pages (only returned on page 1)
    """
    url = f"{category_url}/page/{page}" if page > 1 else category_url
    soup = fetch_soup(url, timeout=120)

    articles = []

    article_items = soup.find_all("li", class_="index_articleItem__d-8iK")
    for item in article_items:
        link_tag = item.find("a", href=True)
        date_tag = item.find("span", attrs={"data-testid": "DateDisplay"})

        if not link_tag or not date_tag:
            continue

        href = link_tag["href"]
        full_url = BASE_DOMAIN + href
        raw_date = date_tag.text.strip().replace("Published on ", "")

        try:
            published = datetime.strptime(raw_date, "%b %d, %Y")
        except ValueError as e:
            print(f"[!] Could not parse date '{raw_date}' on {full_url}: {e}")
            continue

        articles.append({
            "url": full_url,
            "published": published
        })

    total_pages = None
    if page == 1:
        pagination = soup.select("ul.okui-pagination a[data-e2e-okd-pagination-pager]")
        page_numbers = [
            int(a.get_text(strip=True))
            for a in pagination
            if a.get_text(strip=True).isdigit()
        ]
        if page_numbers:
            total_pages = max(page_numbers)

    return articles, total_pages