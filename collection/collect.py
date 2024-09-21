import os
import hashlib
import json
import re
import subprocess
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "data/output"
ALL_URLS_FILE = os.path.join(OUTPUT_DIR, "all_urls.txt")
SCRAPED_DIR = os.path.join(OUTPUT_DIR, "scraped")
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.json")
SCRAPING_DEPTH = 4
CONCURRENT_DOWNLOAD_WORKERS = 3

os.makedirs(SCRAPED_DIR, exist_ok=True)

def run_katana_for_urls(target, all_urls_file):
    katana_cmd = [
        "katana",
        "-u", target,
        "-d", str(SCRAPING_DEPTH),
    ]
    try:
        with open(all_urls_file, "w") as f:
            subprocess.run(katana_cmd, stdout=f, check=True)
        print(f"URLs collected and saved in {all_urls_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run katana for URLs: {e}")
        exit(1)

def download_full_page_with_js(url, output_file):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page_content = page.content()
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(page_content)
            print(f"Downloaded and saved full content for {url}")
            browser.close()
        except Exception as e:
            print(f"Error parsing {url}: {e}")

def is_already_processed(url, list_of_scraped_dir_files):
    parsed_url = urlparse(url)
    path = os.path.join(SCRAPED_DIR, parsed_url.netloc, parsed_url.path.strip('/'))
    filename = os.path.basename(parsed_url.path) or "index.html"
    output_file = os.path.join(path, filename)
    return output_file in list_of_scraped_dir_files

def process_url(url, scraped_dir, metadata, collection_date):
    try:
        parsed_url = urlparse(url)
        path = os.path.join(scraped_dir, parsed_url.netloc, os.path.dirname(parsed_url.path.strip('/')))
        os.makedirs(path, exist_ok=True)

        filename = os.path.basename(parsed_url.path) or "index.html"
        output_file = os.path.join(path, filename)

        if os.path.exists(output_file):
            print(f"Skipping URL as it is already processed: {url}")
            return None

        download_full_page_with_js(url, output_file)

        metadata.append({
            "filepath": output_file,
            "url": url,
            "collection_date": collection_date
        })

        return metadata
    
    except Exception as e:
        print(f"Error processing {url}: {e}")
        time.sleep(15)
        return None

def run_playwright_for_content(urls_file, scraped_dir, metadata):
    with open(urls_file, "r") as f:
        urls = [url.strip() for url in f if url.strip()]

    collection_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with ThreadPoolExecutor(max_workers=CONCURRENT_DOWNLOAD_WORKERS) as executor:
        futures = [executor.submit(process_url, url, scraped_dir, metadata, collection_date) for url in urls]

        for future in as_completed(futures):
            result = future.result()
            if result:
                with open(METADATA_FILE, "w", encoding="utf-8") as json_file:
                    json.dump(metadata, json_file, ensure_ascii=False, indent=4)
                print(f"Metadata saved to {METADATA_FILE}")

def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def collect(target):
    METADATA = []

    if os.path.exists(ALL_URLS_FILE):
        choice = input(f"{ALL_URLS_FILE} exists. Do you want to start over and run katana again to collect URLs? (y/n): ")
        if choice.lower() == 'y':
            os.remove(ALL_URLS_FILE)
            run_katana_for_urls(target, ALL_URLS_FILE)
        else:
            print(f"Using existing URLs from {ALL_URLS_FILE}")
    else:
        run_katana_for_urls(target, ALL_URLS_FILE)

    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as metadata_file:
            METADATA = json.loads(metadata_file.read())

    run_playwright_for_content(ALL_URLS_FILE, SCRAPED_DIR, METADATA)

    print("Finished")