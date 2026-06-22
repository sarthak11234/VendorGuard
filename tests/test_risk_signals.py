"""
VendorGuard - Phase 2 Risk Signals Unit Tests
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock
import httpx

from api.models import Vendor, RiskSignal, RiskSource
from config import config
from tools.weather import get_weather_risk
from tools.news import get_news_risk
from tools.commodity import get_commodity_risk
from tools.fuel import get_fuel_price, clear_fuel_price_cache
from agents.risk_monitor import risk_monitor_agent

from google.adk import Context
from google.adk.sessions import InMemorySessionService
from google.adk import Runner


class TestRiskSignals(unittest.TestCase):
    """Tests the functionality of individual risk signal tools and the RiskMonitorAgent."""

    def setUp(self):
        # Clear the fuel price cache before each test
        clear_fuel_price_cache()

    def test_weather_fallback(self):
        """Test weather tool fallback scores when API key is missing."""
        async def run_test():
            # Seeded city Raipur
            res_raipur = await get_weather_risk("Raipur", "")
            self.assertEqual(res_raipur["score"], 28.0)
            self.assertIn("Heavy monsoon", res_raipur["evidence"])
            self.assertEqual(res_raipur["url"], "https://openweathermap.org/city/1258980")

            # Seeded city Hubli
            res_hubli = await get_weather_risk("Hubli", "")
            self.assertEqual(res_hubli["score"], 25.0)
            self.assertIn("waterlogging", res_hubli["evidence"])

            # Non-seeded city (should return low risk default)
            res_default = await get_weather_risk("Pune", "")
            self.assertEqual(res_default["score"], 5.0)
            self.assertIn("No severe weather", res_default["evidence"])

        asyncio.run(run_test())

    def test_news_fallback(self):
        """Test news tool fallback scores when API key is missing."""
        async def run_test():
            # Seeded city Nagpur
            res_nagpur = await get_news_risk("Nagpur", "")
            self.assertEqual(res_nagpur["score"], 28.0)
            self.assertIn("strike", res_nagpur["evidence"])

            # Seeded city Raipur
            res_raipur = await get_news_risk("Raipur", "")
            self.assertEqual(res_raipur["score"], 25.0)
            self.assertIn("power cuts", res_raipur["evidence"])

            # Non-seeded city
            res_default = await get_news_risk("Pune", "")
            self.assertEqual(res_default["score"], 5.0)

        asyncio.run(run_test())

    def test_commodity_fallback(self):
        """Test commodity tool fallback scores when API is disabled."""
        async def run_test():
            # Seeded CRCA Steel Sheet (VND-001)
            res_steel = await get_commodity_risk("CRCA Steel Sheet", enable_api=False)
            self.assertEqual(res_steel["score"], 18.0)
            self.assertIn("steel", res_steel["evidence"].lower())

            # Seeded CI Castings (VND-002)
            res_castings = await get_commodity_risk("CI Castings", enable_api=False)
            self.assertEqual(res_castings["score"], 12.0)

            # Non-seeded commodity
            res_default = await get_commodity_risk("Rubber Gaskets", enable_api=False)
            self.assertEqual(res_default["score"], 4.0)

        asyncio.run(run_test())

    def test_fuel_fallback_and_cache(self):
        """Test fuel price scraper fallback logic and cached response."""
        async def run_test():
            # Without scraping
            price_no_scrape = await get_fuel_price(enable_scraping=False)
            self.assertEqual(price_no_scrape, config.FALLBACK_DIESEL_PRICE_INR)

            # Test that multiple calls fetch only once (uses cached result)
            clear_fuel_price_cache()
            
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_get.return_value = MagicMock(status_code=500)
                
                # Fetch fuel price twice concurrently
                prices = await asyncio.gather(
                    get_fuel_price(enable_scraping=True),
                    get_fuel_price(enable_scraping=True)
                )
                
                # Assert both calls returned the fallback
                self.assertEqual(prices[0], config.FALLBACK_DIESEL_PRICE_INR)
                self.assertEqual(prices[1], config.FALLBACK_DIESEL_PRICE_INR)
                
                # Ensure the network request was only initiated once
                mock_get.assert_called_once()

        asyncio.run(run_test())

    def test_risk_monitor_agent_execution(self):
        """Test that RiskMonitorAgent runs parallel fetches and scores vendors."""
        async def run_test():
            # Setup mock ADK Context
            session_service = InMemorySessionService()
            runner = Runner(
                node=risk_monitor_agent,
                session_service=session_service,
                auto_create_session=True,
            )
            session = await session_service.create_session(
                app_name="test_app", user_id="test_user", session_id="test_sess"
            )
            ic = runner._new_invocation_context(session, new_message=None, run_config=None)
            ctx = Context(ic)

            # Create standard test vendors
            vendors = [
                Vendor(
                    vendor_id="VND-001",
                    vendor_name="Nagpur Steel Traders Pvt Ltd",
                    city="Nagpur",
                    state="Maharashtra",
                    commodity="CRCA Steel Sheet",
                    open_po_value_inr=1850000,
                    lead_time_days=12,
                    historical_ontime_pct=74.5,
                ),
                Vendor(
                    vendor_id="VND-002",
                    vendor_name="Raipur Casting Works",
                    city="Raipur",
                    state="Chhattisgarh",
                    commodity="CI Castings",
                    open_po_value_inr=1200000,
                    lead_time_days=15,
                    historical_ontime_pct=68.0,
                ),
                Vendor(
                    vendor_id="VND-013",
                    vendor_name="Hubli Alloys Ltd",
                    city="Hubli",
                    state="Karnataka",
                    commodity="Aluminum Ingot",
                    open_po_value_inr=2200000,
                    lead_time_days=18,
                    historical_ontime_pct=76.0,
                ),
                Vendor(
                    vendor_id="VND-010",
                    vendor_name="Satara Rubber Works",
                    city="Satara",
                    state="Maharashtra",
                    commodity="Rubber Gaskets",
                    open_po_value_inr=320000,
                    lead_time_days=6,
                    historical_ontime_pct=95.0,
                )
            ]

            # Execute agent
            signals = await risk_monitor_agent._func(ctx, vendors)

            # Assertions
            self.assertEqual(len(signals), 4)
            self.assertTrue(all(isinstance(s, RiskSignal) for s in signals))

            # Nagpur check (VND-001)
            nagpur_sig = next(s for s in signals if s.vendor_id == "VND-001")
            self.assertEqual(nagpur_sig.weather_risk.score, 18.0)
            self.assertEqual(nagpur_sig.news_risk.score, 28.0)
            self.assertEqual(nagpur_sig.commodity_risk.score, 18.0)
            # historical = (100 - 74.5) * 0.2 = 5.1
            self.assertEqual(nagpur_sig.historical_risk.score, 5.1)
            # total = 18 + 28 + 18 + 5.1 = 69.1
            self.assertEqual(nagpur_sig.total_score, 69.1)
            self.assertIn("Logistics Fuel Impact", nagpur_sig.news_risk.evidence)

            # Raipur check (VND-002)
            raipur_sig = next(s for s in signals if s.vendor_id == "VND-002")
            self.assertEqual(raipur_sig.weather_risk.score, 28.0)
            self.assertEqual(raipur_sig.news_risk.score, 25.0)
            self.assertEqual(raipur_sig.commodity_risk.score, 12.0)
            # historical = (100 - 68.0) * 0.2 = 6.4
            self.assertEqual(raipur_sig.historical_risk.score, 6.4)
            # total = 28 + 25 + 12 + 6.4 = 71.4
            self.assertEqual(raipur_sig.total_score, 71.4)

            # Hubli check (VND-013)
            hubli_sig = next(s for s in signals if s.vendor_id == "VND-013")
            self.assertEqual(hubli_sig.weather_risk.score, 25.0)
            self.assertEqual(hubli_sig.news_risk.score, 25.0)
            self.assertEqual(hubli_sig.commodity_risk.score, 12.0)
            # historical = (100 - 76.0) * 0.2 = 4.8
            self.assertEqual(hubli_sig.historical_risk.score, 4.8)
            # total = 25 + 25 + 12 + 4.8 = 66.8
            self.assertEqual(hubli_sig.total_score, 66.8)

            # Satara check (VND-010)
            satara_sig = next(s for s in signals if s.vendor_id == "VND-010")
            self.assertEqual(satara_sig.weather_risk.score, 5.0)
            self.assertEqual(satara_sig.news_risk.score, 5.0)
            self.assertEqual(satara_sig.commodity_risk.score, 4.0)
            # historical = (100 - 95.0) * 0.2 = 1.0
            self.assertEqual(satara_sig.historical_risk.score, 1.0)
            # total = 5 + 5 + 4 + 1.0 = 15.0
            self.assertEqual(satara_sig.total_score, 15.0)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
