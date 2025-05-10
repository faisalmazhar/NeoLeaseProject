#!/usr/bin/env python3
import sys
import time
import requests
import csv
from lxml import html
from urllib.parse import urljoin

BASE_URL = "https://www.dtc-lease.nl"
LISTING_URL_TEMPLATE = (
    "https://www.dtc-lease.nl/voorraad"
    "?lease_type=financial"
    "&voertuigen%5Bpage%5D={page}"  # simpler correct param
    "&voertuigen%5BsortBy%5D=voertuigen_created_at_desc"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "*/*",
}

def robust_fetch(url, session, max_retries=4):
    """
    Fetch URL with basic retry/backoff for 403/429 or timeouts.
    Returns requests.Response or None if all fails.
    """
    backoffs = [10, 30, 60, 120]  # seconds
    attempt = 0
    while attempt < max_retries:
        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
            print(f"[fetch] GET {url} => {resp.status_code}")
            # If we get 403/429 => might be block => backoff
            if resp.status_code in (403, 429):
                if attempt < max_retries - 1:
                    wait = backoffs[attempt]
                    print(f"[warn] {resp.status_code} => wait {wait}s, retry...")
                    time.sleep(wait)
                    attempt += 1
                    continue
                else:
                    print(f"[error] {resp.status_code} after {max_retries} tries => skip.")
                    return None
            return resp
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                wait = backoffs[attempt]
                print(f"[warn] {type(e).__name__} => wait {wait}s, retry {url}...")
                time.sleep(wait)
                attempt += 1
            else:
                print(f"[error] {type(e).__name__} after {max_retries} tries => skip {url}")
                return None
    return None

def get_listing_links(page_number, session):
    """Return up to 16 product links from the listing page. If no product found => return []."""
    url = LISTING_URL_TEMPLATE.format(page=page_number)
    resp = robust_fetch(url, session)
    if not resp or not resp.ok:
        return []
    tree = html.fromstring(resp.text)

    # Check if first product found => if not => no more
    first_sel = '//main[@id="main-content"]//a[@data-testid="product-result-1"]/@href'
    first_link = tree.xpath(first_sel)
    if not first_link:
        return []

    # Try up to product-result-16
    links = []
    for i in range(1, 17):
        xp = f'//main[@id="main-content"]//a[@data-testid="product-result-{i}"]/@href'
        found = tree.xpath(xp)
        if found:
            links.extend(found)

    abs_links = [urljoin(BASE_URL, ln) for ln in links]
    return abs_links

def parse_detail(detail_url, session):
    """Scrape detail page, return dict with fields + list of image URLs. If fails => return None."""
    record = {
        "url": detail_url,
        "title": None,
        "subtitle": None,
        "financial_lease_price": None,
        "financial_lease_term": None,
        "advertentienummer": None,
        "merk": None,
        "model": None,
        "bouwjaar": None,
        "km_stand": None,
        "transmissie": None,
        "prijs": None,
        "brandstof": None,
        "btw_marge": None,
        "opties_accessoires": None,
        "address": None,
        "images": [],
    }
    resp = robust_fetch(detail_url, session)
    if not resp or not resp.ok:
        print(f"[error] Cannot fetch detail => {detail_url}")
        return None

    tree = html.fromstring(resp.text)
    t = lambda xp: tree.xpath(xp)

    # Title etc
    title = t('//h1[@class="h1-sm tablet:h1 text-trustful-1"]/text()')
    if title: record["title"] = title[0].strip()

    subtitle = t('//p[@class="type-auto-sm tablet:type-auto-m text-trustful-1"]/text()')
    if subtitle: record["subtitle"] = subtitle[0].strip()

    flp = t('//div[@data-testid="price-block"]//h2/text()')
    if flp: record["financial_lease_price"] = flp[0].strip()

    flt = t('//div[@data-testid="price-block"]//p[contains(@class,"info-sm") and contains(text(),"mnd")]/text()')
    if flt: record["financial_lease_term"] = flt[0].strip()

    adnum = t('//div[contains(@class,"p-sm") and contains(text(),"Advertentienummer")]/text()')
    if adnum:
        record["advertentienummer"] = adnum[0].split(":",1)[-1].strip()

    def spec(label):
        xp = f'//div[@class="text-p-sm text-grey-1" and normalize-space(text())="{label}"]/following-sibling::div/text()'
        val = t(xp)
        return val[0].strip() if val else None

    record["merk"] = spec("Merk")
    record["model"] = spec("Model")
    record["bouwjaar"] = spec("Bouwjaar")
    record["km_stand"] = spec("Km stand")
    record["transmissie"] = spec("Transmissie")
    record["prijs"] = spec("Prijs")
    record["brandstof"] = spec("Brandstof")
    record["btw_marge"] = spec("Btw/marge")

    # Opties & Accessoires
    oa = t('//h2[contains(.,"Opties & Accessoires")]/following-sibling::ul/li/text()')
    if oa:
        cleaned = [x.strip() for x in oa if x.strip()]
        record["opties_accessoires"] = ", ".join(cleaned)

    # Address
    addr_sel = '//div[@class="flex justify-between"]/div/p[@class="text-p-sm font-light text-black tablet:text-p"]/text()'
    addr = t(addr_sel)
    if addr:
        record["address"] = addr[0].strip()

    # Images
    img_sel = '//ul[@class="swiper-wrapper pb-10"]/li/img/@src'
    imgs = t(img_sel)
    if imgs:
        for i in imgs:
            if i.startswith("/"):
                i = urljoin(BASE_URL, i)
            record["images"].append(i)

    return record

def main():
    print("[info] Starting DTC scraper (local CSV version)...")
    session = requests.Session()

    all_results = []
    page = 1
    while True:
        print(f"[info] Fetching listing page {page} ...")
        links = get_listing_links(page, session)
        if not links:
            print(f"[info] No links found on page {page}. Stop.")
            break

        print(f"[info] Found {len(links)} links on page {page}.")
        for ln in links:
            print(f"  -> detail: {ln}")
            rec = parse_detail(ln, session)
            if rec:
                all_results.append(rec)
            time.sleep(1)  # short delay

        page += 1
        # if you want some max page limit as a safety net:
        if page > 100:
            print("[warn] Reached 100 pages => stop just in case.")
            break

        time.sleep(2)  # short delay between pages

    print(f"[info] Done scraping. Total results = {len(all_results)}")

    # Write to CSV locally
    if not all_results:
        print("[warn] No results. We'll just end.")
        return

    # Write to dtc_lease_results.csv
    print("[info] Writing data to dtc_lease_results.csv ...")
    fieldnames = [
        "url", "title", "subtitle", "financial_lease_price", "financial_lease_term",
        "advertentienummer", "merk", "model", "bouwjaar", "km_stand",
        "transmissie", "prijs", "brandstof", "btw_marge", "opties_accessoires",
        "address", "images"
    ]
    with open("dtc_lease_results.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_results:
            # Join images into comma string for CSV
            images_str = ",".join(item["images"]) if item["images"] else ""
            rowdict = {
                "url": item["url"],
                "title": item["title"],
                "subtitle": item["subtitle"],
                "financial_lease_price": item["financial_lease_price"],
                "financial_lease_term": item["financial_lease_term"],
                "advertentienummer": item["advertentienummer"],
                "merk": item["merk"],
                "model": item["model"],
                "bouwjaar": item["bouwjaar"],
                "km_stand": item["km_stand"],
                "transmissie": item["transmissie"],
                "prijs": item["prijs"],
                "brandstof": item["brandstof"],
                "btw_marge": item["btw_marge"],
                "opties_accessoires": item["opties_accessoires"],
                "address": item["address"],
                "images": images_str
            }
            writer.writerow(rowdict)

    print("[info] Wrote CSV file successfully.")

if __name__ == "__main__":
    main()
