import os
import csv
import sys
import time
import requests
from lxml import html
from urllib.parse import urljoin

BASE_URL = "https://www.dtc-lease.nl"
LISTING_URL_TEMPLATE = (
    "https://www.dtc-lease.nl/voorraad"
    "?lease_type=financial"
    "&voertuigen%5Bpage%5D={page}"
    "&voertuigen%5BsortBy%5D=voertuigen_created_at_desc"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,nl;q=0.8",
    "Referer": "https://www.dtc-lease.nl/"
}

COOKIES = {
    # If special cookies or session data is required, set them here
}

CSV_COLUMNS = [
    "URL", "Title", "Subtitle", "Financial Lease Price", "Financial Lease Term",
    "Advertentienummer", "Merk", "Model", "Bouwjaar", "Km stand",
    "Transmissie", "Prijs", "Brandstof", "Btw/marge", "Opties & Accessoires",
    "Address", "Images"
]

def fetch_url(session, url):
    """
    Fetch a URL with backoff if we receive status 403 or 429.
    Backoff times: 10m, 30m, 1h, 2h. If still fails, exit.
    """
    backoff_times = [600, 1800, 3600, 7200]  # in seconds
    for wait_seconds in backoff_times + [None]:
        response = session.get(url, headers=HEADERS, cookies=COOKIES, timeout=15)
        print(f"GET {url} => {response.status_code}")
        if response.status_code not in (403, 429):
            return response
        if wait_seconds is None:
            print("Repeated 403/429 responses. Exiting the scraper.")
            sys.exit(1)
        print(f"Got {response.status_code}, sleeping {wait_seconds // 60} minutes...")
        time.sleep(wait_seconds)
    return None

def get_listing_links(session, page_number):
    """
    Fetch the listing page for 'page_number' and collect up to 16 product-result links:
      //main[@id="main-content"]//a[@data-testid="product-result-X"][@href]
    We'll gather them for X=1..16.
    If 'product-result-1' is not found, we return an empty list to signal we should stop pagination.
    """
    url = LISTING_URL_TEMPLATE.format(page=page_number)
    resp = fetch_url(session, url)
    if not resp or not resp.ok:
        return []

    tree = html.fromstring(resp.text)

    # Check if product-result-1 exists. If not, stop pagination.
    first_product = tree.xpath('//main[@id="main-content"]//a[@data-testid="product-result-1"]/@href')
    if not first_product:
        # Means no results on this page
        return []

    # Try to get product-result-i links up to 16
    links = []
    for i in range(1, 17):
        xp = f'//main[@id="main-content"]//a[@data-testid="product-result-{i}"]/@href'
        found = tree.xpath(xp)
        # If we find it, we add to the links list
        if found:
            # Usually it should be a single link, but let's handle if there's more
            links.extend(found)
        else:
            # If we don't find product-result-i, it means no more items on this page
            break

    # Convert relative to absolute
    full_links = [urljoin(BASE_URL, ln) for ln in links]
    return full_links

def parse_detail_page(session, detail_url):
    """
    Fetch detail page and extract data fields into a dict.
    Prints the record (debug) before returning.
    """
    data = dict.fromkeys(CSV_COLUMNS, None)
    data["URL"] = detail_url

    resp = fetch_url(session, detail_url)
    if not resp or not resp.ok:
        return data

    tree = html.fromstring(resp.text)
    t = lambda xp: tree.xpath(xp)

    title = t('//h1[@class="h1-sm tablet:h1 text-trustful-1"]/text()')
    data["Title"] = title[0].strip() if title else None

    subtitle = t('//p[@class="type-auto-sm tablet:type-auto-m text-trustful-1"]/text()')
    data["Subtitle"] = subtitle[0].strip() if subtitle else None

    fl_price = t('//div[@data-testid="price-block"]//h2/text()')
    data["Financial Lease Price"] = fl_price[0].strip() if fl_price else None

    fl_term = t('//div[@data-testid="price-block"]//p[contains(@class,"info-sm") and contains(text(),"mnd")]/text()')
    data["Financial Lease Term"] = fl_term[0].strip() if fl_term else None

    ad_num = t('//div[contains(@class,"p-sm") and contains(text(),"Advertentienummer")]/text()')
    if ad_num:
        data["Advertentienummer"] = ad_num[0].split(":", 1)[-1].strip()

    def spec(label):
        v = t(f'//div[@class="text-p-sm text-grey-1" and normalize-space(text())="{label}"]/following-sibling::div/text()')
        return v[0].strip() if v else None

    data["Merk"] = spec("Merk")
    data["Model"] = spec("Model")
    data["Bouwjaar"] = spec("Bouwjaar")
    data["Km stand"] = spec("Km stand")
    data["Transmissie"] = spec("Transmissie")
    data["Prijs"] = spec("Prijs")
    data["Brandstof"] = spec("Brandstof")
    data["Btw/marge"] = spec("Btw/marge")

    oa = t('//h2[contains(.,"Opties & Accessoires")]/following-sibling::ul/li/text()')
    if oa:
        data["Opties & Accessoires"] = ", ".join(i.strip() for i in oa if i.strip())

    addr = t('//div[@class="flex justify-between"]/div/p[@class="text-p-sm font-light text-black tablet:text-p"]/text()')
    data["Address"] = addr[0].strip() if addr else None

    imgs = t('//ul[@class="swiper-wrapper pb-10"]/li/img/@src')
    if imgs:
        data["Images"] = ",".join(
            urljoin(BASE_URL, i) if i.startswith("/") else i
            for i in imgs
        )

    print(f"Scraped data for {detail_url}: {data}")
    return data

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    if not os.path.exists("links.csv"):
        print("No links.csv found. Scraping listing pages to get all detail links...")
        all_links = []
        page_number = 1

        while True:
            print(f"\n=== Fetching listing page {page_number} ===")
            links = get_listing_links(session, page_number)
            # If no product-result-1 is found => no links => break
            if not links:
                print(f"No links found on page {page_number}. Stopping pagination.")
                break
            print(f"Found {len(links)} links on page {page_number}.")
            all_links.extend(links)
            page_number += 1
            time.sleep(2)  # Sleep between listing pages

        with open("links.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for ln in all_links:
                writer.writerow([ln])
        print(f"Saved {len(all_links)} links to links.csv.")
    else:
        print("links.csv found. Will skip listing-pages scrape.")

    all_links = []
    with open("links.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                all_links.append(row[0])
    print(f"Loaded {len(all_links)} links from links.csv.")

    append_file = os.path.exists("dtc_lease_results.csv")
    with open("dtc_lease_results.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not append_file:
            writer.writeheader()

        total_scraped = 0
        for idx, link in enumerate(all_links, start=1):
            print(f"Scraping detail {idx}/{len(all_links)} => {link}")
            record = parse_detail_page(session, link)
            writer.writerow(record)
            total_scraped += 1
            print(f"Total scraped so far: {total_scraped}")
            time.sleep(2)  # Sleep after each detail fetch

    print(f"Finished. Appended {total_scraped} records to dtc_lease_results.csv.")

if __name__ == "__main__":
    main()
