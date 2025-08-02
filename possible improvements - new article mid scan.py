MAX_RETRIES = 3  # Avoid infinite loops just in case

for category, url in categories.items():
    print(f"\n[+] Processing category: {category}")
    retries = 0
    seen_urls = set()

    while True:
        retries += 1
        if retries > MAX_RETRIES:
            print(f"[!] Max retries reached for category: {category}. Skipping.")
            break

        duplicate_found = False
        category_articles = []
        seen_urls.clear()  # reset for fresh scan

        articles_page1, total_pages = get_articles_on_page(url, 1)
        if total_pages is None:
            total_pages = 1
        total_pages = min(total_pages, MAX_PAGES)

        for page in range(1, total_pages + 1):
            if page == 1:
                articles = articles_page1
            else:
                articles, _ = get_articles_on_page(url, page)

            for article in articles:
                if article["url"] in seen_urls:
                    print(f"[!] Duplicate article found on page {page}: {article['url']}")
                    duplicate_found = True
                    break  # stop inner loop

                seen_urls.add(article["url"])
                published = article["published"]
                if start_dt <= published <= end_dt:
                    category_articles.append({
                        "url": article["url"],
                        "published": published,
                        "category": category
                    })

            if duplicate_found:
                break  # stop page loop

        if not duplicate_found:
            article_metadata.extend(category_articles)
            print(f"[+] Finished processing category: {category}. Total: {len(category_articles)}")
            break  # exit while True
        else:
            print("[~] Detected race condition, restarting category scan...")
