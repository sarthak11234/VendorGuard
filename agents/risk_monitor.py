"""
VendorGuard - Risk Monitor Agent
Monitors risk signals for each vendor across Weather, News, Commodity, and Historical performance.
Executes data collection tools in parallel with graceful degradation.
"""

import asyncio
from datetime import datetime
from google.adk.workflow import node
from google.adk import Context
from api.models import Vendor, RiskSignal, RiskSource
from config import config

# Import risk tools
from tools.weather import get_weather_risk
from tools.news import get_news_risk
from tools.commodity import get_commodity_risk
from tools.fuel import get_fuel_price


async def process_vendor_risk(vendor: Vendor, diesel_price: float) -> RiskSignal:
    """Queries all tools in parallel for a single vendor and returns a RiskSignal."""
    # Determine whether to use real external APIs (run in mock/demo mode if API keys are missing)
    enable_trends = bool(config.OPENWEATHERMAP_API_KEY or config.NEWSCATCHER_API_KEY)

    weather_task = get_weather_risk(vendor.city, config.OPENWEATHERMAP_API_KEY)
    news_task = get_news_risk(vendor.city, config.NEWSCATCHER_API_KEY)
    commodity_task = get_commodity_risk(vendor.commodity, enable_api=enable_trends)
    
    weather_res, news_res, commodity_res = await asyncio.gather(
        weather_task, news_task, commodity_task
    )
    
    weather_score = weather_res["score"]
    weather_evidence = weather_res["evidence"]
    weather_url = weather_res.get("url")
    
    news_score = news_res["score"]
    news_evidence = news_res["evidence"]
    news_url = news_res.get("url")
    
    # Append logistics fuel price info to news evidence
    fuel_info = f" [Logistics Fuel Impact: Diesel price is INR {diesel_price:.2f}/L (Baseline: INR {config.FALLBACK_DIESEL_PRICE_INR:.2f}/L)]"
    news_evidence += fuel_info
    
    commodity_score = commodity_res["score"]
    commodity_evidence = commodity_res["evidence"]
    commodity_url = commodity_res.get("url")
    
    # Historical risk based on vendor historical_ontime_pct (Max 20)
    # Formula: (100 - historical_ontime_pct) * 0.2
    historical_score = round((100.0 - vendor.historical_ontime_pct) * 0.2, 1)
    historical_evidence = f"Historical on-time delivery rate is {vendor.historical_ontime_pct}%."
    
    total_score = weather_score + news_score + commodity_score + historical_score
    total_score = min(max(total_score, 0.0), 100.0)
    
    return RiskSignal(
        vendor_id=vendor.vendor_id,
        weather_risk=RiskSource(
            source_name="OpenWeatherMap",
            category="weather",
            score=weather_score,
            max_score=30.0,
            evidence=weather_evidence,
            source_url=weather_url,
        ),
        news_risk=RiskSource(
            source_name="Newscatcher",
            category="news",
            score=news_score,
            max_score=30.0,
            evidence=news_evidence,
            source_url=news_url,
        ),
        commodity_risk=RiskSource(
            source_name="GoogleTrends",
            category="commodity",
            score=commodity_score,
            max_score=20.0,
            evidence=commodity_evidence,
            source_url=commodity_url,
        ),
        historical_risk=RiskSource(
            source_name="InternalERP",
            category="historical",
            score=historical_score,
            max_score=20.0,
            evidence=historical_evidence,
        ),
        total_score=round(total_score, 1),
        timestamp=datetime.utcnow(),
    )


@node(name="RiskMonitorAgent")
async def risk_monitor_agent(ctx: Context, node_input: list[Vendor]) -> list[RiskSignal]:
    """Monitors weather, news, commodity, and historical performance risk signals for each vendor.

    Args:
        ctx: Workflow invocation context.
        node_input: List of Vendor objects.

    Returns:
        List of RiskSignal objects.
    """
    print(f"RiskMonitorAgent: Monitoring risk signals for {len(node_input)} vendors...")
    
    # 1. Fetch fuel/diesel price once per scan to optimize network requests
    diesel_price = await get_fuel_price()
    print(f"RiskMonitorAgent: Diesel price fetched: INR {diesel_price}/L")
    
    # 2. Process all vendors in parallel using asyncio.gather
    tasks = [process_vendor_risk(vendor, diesel_price) for vendor in node_input]
    signals = await asyncio.gather(*tasks)
    
    print(f"RiskMonitorAgent: Generated {len(signals)} risk signals.")
    return list(signals)
