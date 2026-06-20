"""
VendorGuard - Phase 1 Foundation Unit Tests
"""

import asyncio
import unittest
from api.models import Vendor, RiskBand
from agents.ingest import ingest_agent
from agents.coordinator import Coordinator
from google.adk import Context
from google.adk.sessions import InMemorySessionService
from google.adk import Runner


class TestVendorGuardFoundation(unittest.TestCase):
    """Unit tests for IngestAgent and Coordinator Workflow."""

    def test_ingest_agent_parsing(self):
        """Test that IngestAgent reads and parses the default synthetic CSV correctly."""
        async def run_test():
            # Create a mock Context
            session_service = InMemorySessionService()
            runner = Runner(
                node=ingest_agent,
                session_service=session_service,
                auto_create_session=True,
            )
            # Retrieve standard context by starting a mock run
            session = await session_service.create_session(
                app_name="test_app", user_id="test_user", session_id="test_sess"
            )
            ic = runner._new_invocation_context(
                session,
                new_message=None,
                run_config=None,
            )
            ctx = Context(ic)
            
            # Execute agent
            vendors = await ingest_agent._func(ctx, None)
            
            # Assertions
            self.assertIsInstance(vendors, list)
            self.assertEqual(len(vendors), 15)
            self.assertTrue(all(isinstance(v, Vendor) for v in vendors))
            
            # Check specific seeded vendors
            nagpur_steel = next((v for v in vendors if v.vendor_id == "VND-001"), None)
            self.assertIsNotNone(nagpur_steel)
            self.assertEqual(nagpur_steel.vendor_name, "Nagpur Steel Traders Pvt Ltd")
            self.assertEqual(nagpur_steel.city, "Nagpur")
            self.assertEqual(nagpur_steel.state, "Maharashtra")
            self.assertEqual(nagpur_steel.commodity, "CRCA Steel Sheet")
            self.assertEqual(nagpur_steel.open_po_value_inr, 1850000)
            self.assertEqual(nagpur_steel.lead_time_days, 12)
            self.assertEqual(nagpur_steel.historical_ontime_pct, 74.5)
            self.assertEqual(nagpur_steel.backup_vendor_id, "VND-007")

        asyncio.run(run_test())

    def test_workflow_end_to_end(self):
        """Test that the complete Coordinator multi-agent workflow runs successfully end-to-end."""
        async def run_test():
            coord = Coordinator()
            results = await coord.run_mock_scan()
            
            # Assertions
            self.assertIn("vendors", results)
            self.assertIn("assessments", results)
            self.assertIn("drafts", results)
            
            self.assertEqual(len(results["vendors"]), 15)
            self.assertEqual(len(results["assessments"]), 15)
            self.assertEqual(len(results["drafts"]), 3)
            
            # Verify high-risk vendors are Nagpur (VND-001), Raipur (VND-002), Hubli (VND-013)
            high_risk_ids = [d["vendor_id"] for d in results["drafts"]]
            self.assertIn("VND-001", high_risk_ids)
            self.assertIn("VND-002", high_risk_ids)
            self.assertIn("VND-013", high_risk_ids)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
