#!/usr/bin/env python3

import time
from concurrent.futures import ThreadPoolExecutor

import requests

API = "https://prices.runescape.wiki/api/v1/osrs"
HEADERS = {"User-Agent": "osrs-price-scraper (student project; you@example.com)"}

ITEMS = {
    "Abyssal whip": 4151,
    "Dragon scimitar": 4587,
    "Twisted bow": 20997,
    "Armadyl godsword": 11802,
}


# Fetch the price history for one item from the API
def get_price_history(item_id):
    response = requests.get(
        f"{API}/timeseries",
        headers=HEADERS,
        params={"timestep": "1h", "id": item_id},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# Average the high prices from the history data
def average_price(history):
    prices = []
    for point in history.get("data", []):
        if point.get("avgHighPrice"):
            prices.append(point["avgHighPrice"])

    if not prices:
        return None

    return sum(prices) / len(prices)


# Get the average price for one (name, id) pair
def scrape_item(name_and_id):
    name, item_id = name_and_id
    history = get_price_history(item_id)
    return name, average_price(history)


# Scrape items one at a time
def run_sequential(items):
    return list(map(scrape_item, items.items()))


# Scrape items several at a time using threads
def run_concurrent(items, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(scrape_item, items.items()))


if __name__ == "__main__":
    # Run both versions, time them, and print the prices
    timings = {}

    for runner in (run_sequential, run_concurrent):
        start = time.perf_counter()
        results = runner(ITEMS)
        elapsed = time.perf_counter() - start
        timings[runner.__name__] = elapsed
        print(f"{runner.__name__}: {elapsed:.2f} seconds")

    print()
    for name, avg in results:
        if avg:
            print(f"{name}: {avg:,.0f} gp")
        else:
            print(f"{name}: no data")
