"""
VendorGuard - News Risk Tool
Integrates with Newscatcher API v3 to fetch news articles and calculate risk scores.
"""

import httpx
from typing import Any, Dict


async def get_news_risk(city: str, api_key: str) -> Dict[str, Any]:
    """Fetches supply chain disruption news for a city and calculates a risk score (0-30).

    If API key is missing or request fails, falls back gracefully.
    """
    # 1. Graceful Fallback if API key is not configured
    if not api_key:
        city_lower = city.lower()
        if city_lower == "nagpur":
            return {
                "score": 28.0,
                "evidence": f"Local transport union strike scheduled in {city}, affecting logistics (Pre-seeded fallback).",
                "url": "https://newscatcherapi.com/mock/nagpur-strike",
            }
        elif city_lower == "raipur":
            return {
                "score": 25.0,
                "evidence": f"Industrial power cuts reported in {city} region, affecting casting foundries (Pre-seeded fallback).",
                "url": "https://newscatcherapi.com/mock/raipur-power-cuts",
            }
        elif city_lower == "hubli":
            return {
                "score": 25.0,
                "evidence": f"Local labor dispute and lockouts reported at fastener factories in {city} area (Pre-seeded fallback).",
                "url": "https://newscatcherapi.com/mock/hubli-lockout",
            }
        return {
            "score": 5.0,
            "evidence": f"No significant supply chain disruptions reported for {city} (Mock fallback).",
            "url": "https://newscatcherapi.com",
        }

    # 2. Call Newscatcher API v3
    url = "https://v3-api.newscatcherapi.com/api/search"
    headers = {
        "x-api-token": api_key,
        "Content-Type": "application/json",
    }
    
    # Search query targeting supply chain disruptions and the specific city
    query = f"(strike OR flood OR lockdown OR factory OR closure OR shutdown) AND \"{city}\""
    
    payload = {
        "q": query,
        "lang": "en",
        "countries": "IN",
        "from_": "48h",
        "page_size": 10,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"News Tool Warning: API returned status {response.status_code} for {city}. Using mock fallback.")
                return await get_news_risk(city, "")

            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return {
                    "score": 5.0,
                    "evidence": f"No significant supply chain disruptions reported for {city} in the last 48 hours.",
                    "url": "https://newscatcherapi.com",
                }

            # Score logic based on relevance:
            # - Keywords "strike", "lockout", "floods", "shutdown", "closure" + matching city = 25-30 points.
            # - General logistics or commodity volatility = 10-15 points.
            max_score = 5.0
            evidence = f"No severe disruptions reported for {city}."
            citation_url = "https://newscatcherapi.com"

            for article in articles:
                title = article.get("title", "").lower()
                summary = (article.get("summary") or article.get("description") or "").lower()
                link = article.get("link", "https://newscatcherapi.com")

                text_to_check = f"{title} {summary}"
                score = 5.0
                
                # Check for severe disruption keywords
                severe_keywords = ["strike", "lockout", "lock-out", "floods", "flooding", "shutdown", "closure", "lockdown"]
                moderate_keywords = ["delay", "logistics", "supply chain", "shortage", "congestion", "disruption"]
                
                if any(kw in text_to_check for kw in severe_keywords):
                    score = 28.0 if "strike" in text_to_check or "lockout" in text_to_check or "floods" in text_to_check else 25.0
                elif any(kw in text_to_check for kw in moderate_keywords):
                    score = 15.0
                else:
                    score = 10.0

                if score > max_score:
                    max_score = score
                    evidence = f"News Alert: {article.get('title')} (Source: {article.get('domain_url') or 'News'})"
                    citation_url = link

            return {
                "score": round(max_score, 1),
                "evidence": evidence,
                "url": citation_url,
            }

    except Exception as e:
        print(f"News Tool Warning: Failed to fetch news for {city} due to exception: {e}. Using mock fallback.")
        return await get_news_risk(city, "")
