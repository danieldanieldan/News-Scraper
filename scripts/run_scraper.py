import argparse
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from okx_news_scraper.archive_scraper import (
    get_all_categories,
    get_articles_on_page
)
from okx_news_scraper.article_scraper import extract_title_and_body
from okx_news_scraper.constants import ARCHIVE_HOMEPAGE_URL, MAX_PAGES


def validate_args(start_date: str, end_date: str, folder: str):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format.")

    today = datetime.today()
    if start > today or end > today:
        raise ValueError("Dates must not be in the future.")

    if end < start:
        raise ValueError("END_DATE must be on or after START_DATE.")

    output_path = Path(folder)
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True)
        except Exception as e:
            raise PermissionError(f"Could not create output folder: {e}")
    elif not os.access(output_path, os.W_OK):
        raise PermissionError("Output folder is not writable.")

    return start, end, output_path


def run_scraper(start_date: str, end_date: str, folder: str):
    start_dt, end_dt, output_path = validate_args(start_date, end_date, folder)
    categories = get_all_categories(ARCHIVE_HOMEPAGE_URL)
    article_metadata = []

    for category, url in categories.items():
        articles_in_category = 0
        print(f"\n[+] Processing category: {category}")
        articles_page1, actual_total_pages = get_articles_on_page(url, 1)
        if actual_total_pages is None:
            actual_total_pages = 1

        if actual_total_pages > MAX_PAGES:
            print(
                f"[!] WARNING: Category '{category}' has {actual_total_pages} pages, "
                f"which exceeds the MAX_PAGES limit of {MAX_PAGES}. "
                "You may be missing articles. Please review scraper logic or "
                f"check whether the OKX website accepts requests beyond page {MAX_PAGES}. "
                "If so, update the MAX_PAGES constant."
            )
        total_pages = min(actual_total_pages, MAX_PAGES)

        for page in range(1, total_pages + 1):
            if page == 1:
                articles = articles_page1
            else:
                articles, _ = get_articles_on_page(url, page)

            for article in articles:
                published = article["published"]
                if start_dt <= published <= end_dt:
                    articles_in_category += 1
                    article_metadata.append({
                        "url": article["url"],
                        "published": published,
                        "category": category
                    })

            if page > 1 and any(article["published"] < start_dt for article in articles):
                break
            
        print(f"[+] Finished processing category: {category}. Total articles found in category: {articles_in_category}")

    print(f"\n[+] Total articles to process: {len(article_metadata)}")
    print("[~] Extracting title and body content...")

    records = []
    for meta in tqdm(article_metadata, desc="Scraping articles"):
        try:
            content = extract_title_and_body(meta["url"], timeout=60)
            records.append({
                "date": meta["published"].strftime("%Y-%m-%d"),
                "title": content["title"],
                "body": content["body"],
                "category": meta["category"]
            })
        except Exception as e:
            print(f"[!] Failed to extract {meta['url']}: {e}")
            records.append({
                "date": meta["published"].strftime("%Y-%m-%d"),
                "title": f"Failed to extract title: {e}",
                "body": f"Failed to extract body: {e}",
                "category": meta["category"]
            })

    # Save with timestamp prefix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_file = output_path / f"{timestamp}_okx_articles_{start_date}_to_{end_date}.json"
    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(records, jf, indent=2, ensure_ascii=False)

    xlsx_file = output_path / f"{timestamp}_okx_articles_{start_date}_to_{end_date}.xlsx"
    pd.DataFrame(records).to_excel(xlsx_file, index=False)

    print(f"\n[+] Scraping complete. Saved {len(records)} articles to:")
    print(f"  - JSON: {json_file}")
    print(f"  - XLSX: {xlsx_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape OKX news articles by date range.")
    parser.add_argument("START_DATE", help="Start date in YYYY-MM-DD format")
    parser.add_argument("END_DATE", help="End date in YYYY-MM-DD format")
    parser.add_argument("FOLDER", help="Folder to save the scraped files")
    args = parser.parse_args()

    run_scraper(args.START_DATE, args.END_DATE, args.FOLDER)
