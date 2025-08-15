# filename: psx_bot_api.py
import os
import re
import time
import asyncio
from typing import Optional
from datetime import datetime, timedelta

import aiohttp
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="PSX Bot API", version="0.1")

# Simple in-memory cache {key: (timestamp, data)}
CACHE = {}
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "5"))  # default 5s for near-real-time

# Configuration via env vars
VENDOR = os.getenv("VENDOR", "")        # e.g., "twelvedata" or empty for scrape
VENDOR_API_KEY = os.getenv("VENDOR_API_KEY", "")
SCRAPE_BASE = os.getenv("SCRAPE_BASE", "https://dps.psx.com.pk/company/{symbol}")  # PSX DPS company page

class QuoteResponse(BaseModel):
    symbol: str
    price: Optional[float] = None
    time: Optional[str] = None
    source: str
    raw: Optional[dict] = None

def get_from_cache(key: str):
    row = CACHE.get(key)
    if not row:
        return None
    ts, data = row
    if time.time() - ts > CACHE_TTL:
        del CACHE[key]
        return None
    return data

def set_cache(key: str, data):
    CACHE[key] = (time.time(), data)

async def fetch_json(session: aiohttp.ClientSession, url: str, params=None, headers=None):
    async with session.get(url, params=params, headers=headers, timeout=15) as resp:
        text = await resp.text()
        # try parse json if content-type
        try:
            return await resp.json()
        except Exception:
            return {"_raw_text": text}

# Vendor example: TwelveData (as example of authorized API)
async def fetch_from_vendor(session: aiohttp.ClientSession, symbol: str):
    if VENDOR.lower() == "twelvedata":
        # TwelveData expects a symbol like "PAKS.KAR" or an exchange code; adjust per vendor docs
        url = "https://api.twelvedata.com/price"
        params = {"symbol": symbol, "apikey": VENDOR_API_KEY}
        j = await fetch_json(session, url, params=params)
        # TwelveData returns {"price":"xx.xx"}
        if "price" in j:
            return {"price": float(j["price"]), "raw": j}
        raise HTTPException(status_code=502, detail="Vendor returned unexpected response")
    else:
        raise HTTPException(status_code=501, detail="Configured vendor not implemented on server")

# Scraper: fetch company page and try to extract a numeric price from page
# NOTE: This is a heuristic fallback; you should inspect the PSX page's network/xhr for a stable JSON endpoint.
async def fetch_by_scrape(session: aiohttp.ClientSession, symbol: str):
    url = SCRAPE_BASE.format(symbol=symbol.upper())
    async with session.get(url, timeout=15) as resp:
        if resp.status != 200:
            raise HTTPException(status_code=resp.status, detail=f"Failed to fetch {url}")
        text = await resp.text()

    # Heuristic: look for JSON like patterns or labels like "lastPrice" or "ltp" or inline price.
    # These regexes try common patterns: "lastPrice":123.45 or "ltp": "123.45" or >123.45< near "price" words.
    patterns = [
        r'"lastPrice"\s*:\s*["\']?([0-9]{1,6}(?:\.[0-9]+)?)',
        r'"ltp"\s*:\s*["\']?([0-9]{1,6}(?:\.[0-9]+)?)',
        r'Last Price<\/.*?>\s*([0-9]{1,6}(?:\.[0-9]+)?)',
        r'([\d]{1,6}(?:\.[0-9]+)?)\s*(?:PKR|Rs\.|Rs|PKR\.)',  # price followed by currency
        r'(["\']price["\']\s*:\s*)([0-9]{1,6}(?:\.[0-9]+)?)'
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            # the last captured group likely contains number
            price_str = m.groups()[-1]
            try:
                price = float(price_str)
                return {"price": price, "raw": {"pattern": p}}
            except:
                continue

    # Fallback: try to find any numeric token near "price" keyword
    near_price = re.search(r'(price|last price|lastprice).{0,80}?([0-9]{1,6}(?:\.[0-9]+)?)', text, re.IGNORECASE)
    if near_price:
        try:
            price = float(near_price.group(2))
            return {"price": price, "raw": {"pattern": "near_price"}}
        except:
            pass

    # If still nothing, return the page snippet for inspection
    snippet = text[:2000]
    return {"price": None, "raw": {"html_snippet": snippet}}

@app.get("/api/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str, mode: Optional[str] = Query(None, description="optional: vendor or scrape")):
    key = f"{symbol}:{mode or VENDOR or 'scrape'}"
    cached = get_from_cache(key)
    if cached:
        return cached

    async with aiohttp.ClientSession() as session:
        if (mode or VENDOR).lower() in ("", "scrape") or (mode and mode.lower() == "scrape"):
            data = await fetch_by_scrape(session, symbol)
            source = "scrape"
        else:
            data = await fetch_from_vendor(session, symbol)
            source = f"vendor:{VENDOR}"

    result = QuoteResponse(
        symbol=symbol.upper(),
        price=data.get("price"),
        time=datetime.utcnow().isoformat() + "Z",
        source=source,
        raw=data.get("raw")
    )
    set_cache(key, result)
    return result

# simple health
@app.get("/api/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}