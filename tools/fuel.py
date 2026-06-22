"""
VendorGuard - Fuel Price Tool
Parses the PPAC India retail selling prices page to extract the current diesel price.
Employs an in-memory cache to ensure only one HTTP request is made per scan.
"""

import asyncio
import re
import httpx
from bs4 import BeautifulSoup
from config import config

# Module-level cache to limit to 1 request per scan execution
_cached_diesel_price = None
_lock = asyncio.Lock()


async def get_fuel_price(enable_scraping: bool = True) -> float:
    """Retrieves the domestic diesel price per litre from PPAC India.

    Returns the parsed price (INR/L) or a fallback price (INR 89.62) if parsing fails.
    Guarantees at most 1 network call is made using an in-memory lock/cache.
    """
    global _cached_diesel_price

    async with _lock:
        if _cached_diesel_price is not None:
            return _cached_diesel_price

        if not enable_scraping:
            _cached_diesel_price = config.FALLBACK_DIESEL_PRICE_INR
            return _cached_diesel_price

        # Official PPAC India URL for Retail Selling Prices
        url = "https://ppac.gov.in"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            print("Fuel Tool: Fetching diesel prices from PPAC India...")
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    raise httpx.HTTPStatusError(f"HTTP Status {response.status_code}", request=response.request, response=response)

                soup = BeautifulSoup(response.text, "html.parser")
                
                # Scan for tables, cells or paragraphs containing diesel price.
                # Government sites often list tables of metro prices.
                # We will search for cells containing "Diesel" and look for adjacent numeric fields.
                diesel_price = None
                
                # Find all text elements with "diesel" (case-insensitive)
                diesel_cells = soup.find_all(string=re.compile(r"diesel", re.IGNORECASE))
                
                for cell in diesel_cells:
                    # Traversal: look at parent or siblings
                    parent = cell.parent
                    if not parent:
                        continue
                        
                    # Check parent's siblings or nested elements for numeric values (like 94.25, 89.62, etc.)
                    sibling_text = parent.get_text() + " " + (parent.parent.get_text() if parent.parent else "")
                    prices = re.findall(r"\b\d{2,3}\.\d{2}\b", sibling_text)
                    if prices:
                        # Pick the first valid-looking price in Indian retail diesel range (e.g. 80.0 to 110.0 INR)
                        for price_str in prices:
                            price_val = float(price_str)
                            if 80.0 <= price_val <= 120.0:
                                diesel_price = price_val
                                break
                    if diesel_price:
                        break
                
                if diesel_price:
                    print(f"Fuel Tool: Successfully parsed diesel price from PPAC: INR {diesel_price}/L")
                    _cached_diesel_price = diesel_price
                else:
                    print("Fuel Tool Warning: Could not locate retail diesel price in PPAC HTML. Using fallback.")
                    _cached_diesel_price = config.FALLBACK_DIESEL_PRICE_INR

        except Exception as e:
            print(f"Fuel Tool Warning: Scraping PPAC India failed due to: {e}. Using fallback.")
            _cached_diesel_price = config.FALLBACK_DIESEL_PRICE_INR

        return _cached_diesel_price


def clear_fuel_price_cache():
    """Helper to clear the cached price (e.g., between test runs)."""
    global _cached_diesel_price
    _cached_diesel_price = None
