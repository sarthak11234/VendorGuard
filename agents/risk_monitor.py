"""
VendorGuard - Risk Monitor Agent
Monitors risk signals for each vendor across Weather, News, Commodity, and Historical performance.
"""

from datetime import datetime
from typing import Any
from google.adk.workflow import node
from api.models import Vendor, RiskSignal, RiskSource


@node(name="RiskMonitorAgent")
async def risk_monitor_agent(node_input: list[Vendor]) -> list[RiskSignal]:
    """Monitors weather, news, commodity, and historical performance risk signals for each vendor.

    Args:
        node_input: List of Vendor objects.

    Returns:
        List of RiskSignal objects.
    """
    print(f"RiskMonitorAgent: Monitoring risk signals for {len(node_input)} vendors...")
    signals = []

    for vendor in node_input:
        # Mock weather risk (Max 30)
        weather_score = 5.0
        weather_evidence = f"No severe weather forecast for {vendor.city}."
        if vendor.vendor_id == "VND-001":
            weather_score = 18.0
            weather_evidence = f"Unseasonal heavy rains disrupting material handling in {vendor.city}."
        elif vendor.vendor_id == "VND-002":
            weather_score = 28.0
            weather_evidence = f"Heavy monsoon alert and potential flooding in {vendor.city} over the next 48 hours."
        elif vendor.vendor_id == "VND-013":
            weather_score = 25.0
            weather_evidence = f"Heavy monsoon and traffic disruptions in {vendor.city} road corridors."

        # Mock news risk (Max 30)
        news_score = 5.0
        news_evidence = f"No significant supply chain disruptions reported in {vendor.state}."
        if vendor.vendor_id == "VND-001":
            news_score = 28.0
            news_evidence = f"Local transport union strike scheduled in {vendor.city}, affecting logistics."
        elif vendor.vendor_id == "VND-002":
            news_score = 25.0
            news_evidence = f"Industrial power cuts reported in {vendor.state}, affecting casting foundries."
        elif vendor.vendor_id == "VND-013":
            news_score = 25.0
            news_evidence = f"Local labor dispute and lockouts reported at fastener factories in {vendor.state}."

        # Mock commodity risk (Max 20)
        commodity_score = 4.0
        commodity_evidence = f"Commodity price trend for {vendor.commodity} is stable."
        if vendor.vendor_id == "VND-001":
            commodity_score = 18.0
            commodity_evidence = f"Sudden price spike and supply constraints for {vendor.commodity} globally."
        elif vendor.vendor_id == "VND-002":
            commodity_score = 12.0
            commodity_evidence = f"Rising prices of raw iron ore affecting castings production costs."
        elif vendor.vendor_id == "VND-013":
            commodity_score = 12.0
            commodity_evidence = f"Price volatility in alloy steel wire rods."

        # Historical risk based on vendor historical_ontime_pct (Max 20)
        # Formula: (100 - historical_ontime_pct) * 0.2
        historical_score = round((100.0 - vendor.historical_ontime_pct) * 0.2, 1)
        historical_evidence = f"Historical on-time delivery rate is {vendor.historical_ontime_pct}%."

        total_score = weather_score + news_score + commodity_score + historical_score
        total_score = min(max(total_score, 0.0), 100.0)

        signal = RiskSignal(
            vendor_id=vendor.vendor_id,
            weather_risk=RiskSource(
                source_name="OpenWeatherMap",
                category="weather",
                score=weather_score,
                max_score=30.0,
                evidence=weather_evidence,
            ),
            news_risk=RiskSource(
                source_name="Newscatcher",
                category="news",
                score=news_score,
                max_score=30.0,
                evidence=news_evidence,
            ),
            commodity_risk=RiskSource(
                source_name="GoogleTrends",
                category="commodity",
                score=commodity_score,
                max_score=20.0,
                evidence=commodity_evidence,
            ),
            historical_risk=RiskSource(
                source_name="InternalERP",
                category="historical",
                score=historical_score,
                max_score=20.0,
                evidence=historical_evidence,
            ),
            total_score=total_score,
            timestamp=datetime.utcnow(),
        )
        signals.append(signal)

    print(f"RiskMonitorAgent: Generated {len(signals)} risk signals.")
    return signals
