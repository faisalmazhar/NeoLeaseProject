# utils.py

import re
import logging

def parse_price(raw_price_str):
    """
    Parse a Dutch/EU price string, e.g.:
      '20.950,-' => 20950.0
      '47,900.50' => 47900.50
      '€ 1.234,56' => 1234.56
    If it fails, return 0.0
    """
    if not raw_price_str:
        logging.debug("[parse_price] Empty or None => 0.0")
        return 0.0

    logging.debug(f"[parse_price] Raw input => {raw_price_str!r}")

    # 1) Remove currency symbols and trailing ',-'
    cleaned = raw_price_str.upper()
    cleaned = cleaned.replace('€', '').replace('EUR', '').strip()
    cleaned = re.sub(r',-*$', '', cleaned)  # remove trailing ,- etc.

    # 2) Remove spaces or other thousand separators (like " ")
    cleaned = cleaned.replace(' ', '')

    # 3) Handle typical Dutch format: a dot as thousands
    #    if there's a pattern like "(\d)\.(\d{3})(\D|$)", remove that dot
    #    e.g. "20.950" => "20950"
    cleaned = re.sub(r'(\d)\.(\d{3})(\D|$)', r'\1\2\3', cleaned)

    # 4) If there's still a comma, treat it as decimal
    #    If there's a dot near the end, it might be decimal; but usually in NL comma is decimal
    #    We'll do a quick check: if the string has BOTH '.' and ',' => guess '.' is thousands, remove them
    if '.' in cleaned and ',' in cleaned:
        # remove all dots
        cleaned = cleaned.replace('.', '')
        # then convert comma to dot
        cleaned = cleaned.replace(',', '.')

    else:
        # just convert any leftover comma to dot
        cleaned = cleaned.replace(',', '.')

    # 5) Parse float
    try:
        val = float(cleaned)
        logging.debug(f"[parse_price] Cleaned => {cleaned!r}, Parsed => {val}")
        return val
    except ValueError:
        logging.debug(f"[parse_price] FAILED parse => {cleaned!r} => fallback 0.0")
        return 0.0
