# OKX News Scraper

This Python project scrapes news articles from the OKX crypto exchange announcement sections. It allows you to download structured article data (including title, body, category, and publication date) for a given date range and store the results as `.json` and `.xlsx` files.


## Features

- Scrapes all article categories individually to ensure complete coverage.
- Handles input validation and permission errors.
- Accepts flexible date ranges.
- Converts article bodies to clean Markdown using `html2text`.
- Outputs data to both `.json` and `.xlsx` formats.


## Installation

1. Clone or download this project folder.
2. Ensure Python 3.10+ is installed on your system.
3. Install dependencies by running:

   pip install -r requirements.txt


## Usage

The scraper is executed from the command line from the root folder of the project using:

    python -m scripts/run_scraper.py START_DATE END_DATE FOLDER

Arguments:

    START_DATE (required): Start date in YYYY-MM-DD format.
    END_DATE (required): End date in YYYY-MM-DD format.
    FOLDER (required): Destination folder for the output files.

Example:

    python -m scripts.run_scraper 2025-01-01 2025-02-01 ./output

This command downloads all OKX announcements published between January 1 and February 1, 2025, and saves them into the ./output folder.

Alternatively, one can import the function run_scraper(start_date: str, end_date: str, folder: str) from scripts.run_scraper and use it normally inside another python file


## Output:

The script will generate two output files in the specified folder:

    A .json file containing all scraped articles.
    A .xlsx file (Excel format) with the same data.

Each article record includes:

    date
    title
    body
    category


## Known Limitations and Future Improvements

New Articles During Scan
The scraper does not lock the state of the website. If a new article is published mid-scan, results may vary slightly on repeated executions.

Inefficient Page Scanning
Currently, the scraper scans all pages in a category until it finds all articles within the specified range. While effective, this can be slow if the date range is far in the past. A smarter approach using date estimation or binary search could reduce unnecessary page scans.

Threading Limitations
An earlier version implemented multithreading to speed up downloads, but the OKX website frequently failed under concurrent requests, occasionally omitting articles. Due to time constraints, threading was removed. For future development, it may be worth investigating a more controlled or asynchronous solution that better respects server limits.

Failure detecting
i'mplement logging, output checking and automated alerting to catach loud and silent errors

## License
This project is provided under the MIT License.