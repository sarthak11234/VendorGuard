"""
VendorGuard - Phase 4 API and CLI Unit Tests
"""

import asyncio
import json
import os
import subprocess
import time
import unittest
from fastapi.testclient import TestClient

from main import app
from api.models import ScanStage


class TestApiAndCli(unittest.TestCase):
    """Tests the FastAPI routes, background scanning pipeline, and CLI execution."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "1.0")

    def test_scan_lifecycle_api(self):
        """Test triggering, polling, and retrieving results of a scan run."""
        # 1. Trigger the scan
        payload = {
            "csv_path": "data/vendors_synthetic.csv",
            "threshold": 65
        }
        response = self.client.post("/api/scan", json=payload)
        self.assertEqual(response.status_code, 200)
        
        trigger_data = response.json()
        self.assertIn("scan_id", trigger_data)
        scan_id = trigger_data["scan_id"]
        
        # 2. Poll status until complete or failed (max 10 seconds since it runs local fallbacks)
        max_attempts = 15
        completed = False
        
        for _ in range(max_attempts):
            status_response = self.client.get(f"/api/scan/{scan_id}")
            self.assertEqual(status_response.status_code, 200)
            status_data = status_response.json()
            
            stage = status_data["status"]
            if stage == ScanStage.COMPLETE:
                completed = True
                break
            elif stage == ScanStage.FAILED:
                self.fail(f"Scan failed with error: {status_data.get('error')}")
                
            time.sleep(1.0)
            
        self.assertTrue(completed, "Scan did not complete within timeout")

        # 3. Retrieve assessments list
        vendors_response = self.client.get("/api/vendors")
        self.assertEqual(vendors_response.status_code, 200)
        vendors_data = vendors_response.json()
        self.assertEqual(len(vendors_data), 15)
        
        # Verify Nagpur Steel is high-risk
        nagpur = next((v for v in vendors_data if v["vendor"]["vendor_id"] == "VND-001"), None)
        self.assertIsNotNone(nagpur)
        self.assertEqual(nagpur["risk_band"], "HIGH")

        # 4. Retrieve single vendor detail
        detail_response = self.client.get(f"/api/vendors/VND-001")
        self.assertEqual(detail_response.status_code, 200)
        detail_data = detail_response.json()
        self.assertIn("assessment", detail_data)
        self.assertIn("draft", detail_data)
        self.assertEqual(detail_data["assessment"]["vendor"]["vendor_id"], "VND-001")
        self.assertIsNotNone(detail_data["draft"])
        self.assertEqual(detail_data["draft"]["vendor_id"], "VND-001")
        self.assertIn("Nagpur Steel", detail_data["draft"]["vendor_name"])

        # 5. Retrieve alerts
        alerts_response = self.client.get("/api/alerts")
        self.assertEqual(alerts_response.status_code, 200)
        alerts_data = alerts_response.json()
        self.assertEqual(len(alerts_data), 3)  # VND-001, VND-002, VND-013
        
        high_risk_ids = [d["vendor_id"] for d in alerts_data]
        self.assertIn("VND-001", high_risk_ids)
        self.assertIn("VND-002", high_risk_ids)
        self.assertIn("VND-013", high_risk_ids)

    def test_cli_execution(self):
        """Test running the scan via the command line interface."""
        output_file = "test_cli_report.json"
        
        # Clean up output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
            
        try:
            # Execute cli.py using the active virtual environment python
            cmd = [
                "venv\\Scripts\\python.exe",
                "cli.py",
                "--vendor-sheet", "data/vendors_synthetic.csv",
                "--output", output_file,
                "--threshold", "65"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Assertions
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(output_file), "CLI did not write output report file")
            
            with open(output_file, "r", encoding="utf-8") as f:
                report = json.load(f)
                
            self.assertIn("summary", report)
            self.assertEqual(report["summary"]["total_vendors"], 15)
            self.assertEqual(report["summary"]["high_risk_count"], 3)
            self.assertEqual(len(report["assessments"]), 15)
            self.assertEqual(len(report["drafts"]), 3)
            
            draft_ids = [d["vendor_id"] for d in report["drafts"]]
            self.assertIn("VND-001", draft_ids)
            self.assertIn("VND-002", draft_ids)
            self.assertIn("VND-013", draft_ids)
            
        finally:
            # Clean up test output file
            if os.path.exists(output_file):
                os.remove(output_file)


if __name__ == "__main__":
    unittest.main()
