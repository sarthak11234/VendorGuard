"""
VendorGuard - Command Line Interface (CLI) Entry Point
Allows running supply chain risk scans directly from the terminal.
Cleaned of emoji characters to prevent UnicodeEncodeErrors on Windows terminals.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import date, datetime
from typing import Any, Dict

from agents.coordinator import Coordinator
from config import config


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime and date objects."""
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments for the VendorGuard CLI."""
    parser = argparse.ArgumentParser(
        description="VendorGuard CLI: AI-Powered Supply Chain Risk Assessment for SME Manufacturers."
    )
    
    # Define arguments
    parser.add_argument(
        "--vendor-sheet",
        type=str,
        required=True,
        help="Google Sheet URL or local CSV path containing the vendor register.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="report.json",
        help="Output JSON file path to write results (default: report.json).",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=65,
        help="Risk score threshold above which actions/drafts are triggered (default: 65).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed execution logs and per-vendor risk breakdown to stdout.",
    )

    return parser.parse_args()


async def run_cli_scan(args: argparse.Namespace) -> int:
    """Orchestrates the workflow execution from the command line."""
    print("====================================================")
    print("VendorGuard CLI: Initiating Risk Scan...")
    print("====================================================")
    
    # 1. Dynamically configure thresholds
    config.RISK_THRESHOLD = args.threshold
    config.MEDIUM_RISK_MAX = args.threshold
    
    # Determine if input is a URL or local file path
    sheet_url = ""
    csv_path = ""
    target_source = args.vendor_sheet
    if target_source.startswith("http://") or target_source.startswith("https://"):
        sheet_url = target_source
        print(f"Target Source: Remote Google Sheet ({sheet_url})")
    else:
        csv_path = target_source
        print(f"Target Source: Local CSV File ({csv_path})")
        if not os.path.exists(csv_path):
            print(f"Error: File not found at '{csv_path}'")
            return 1

    print(f"Risk Threshold: {args.threshold} (Scores > {args.threshold} flag HIGH risk)")
    
    # 2. Run Scan
    try:
        coordinator = Coordinator()
        results = await coordinator.run_mock_scan(sheet_url=sheet_url, csv_path=csv_path)
        
        vendors = results.get("vendors", [])
        assessments = results.get("assessments", [])
        drafts = results.get("drafts", [])
        
        print(f"\nScan Completed. Processed {len(vendors)} vendors.")
        
        # 3. Print Summary / Verbose output
        high_risk_vendors = [a for a in assessments if a.get("risk_band") == "HIGH"]
        print(f"High Risk Flags Detected: {len(high_risk_vendors)} / {len(vendors)}")
        
        print("\n" + "-" * 75)
        print(f"{'Vendor ID':<10} | {'Vendor Name':<30} | {'Score':<6} | {'Risk Band':<8}")
        print("-" * 75)
        for a in assessments:
            vendor = a.get("vendor", {})
            risk_sig = a.get("risk_signal", {})
            print(
                f"{vendor.get('vendor_id'):<10} | "
                f"{vendor.get('vendor_name')[:30]:<30} | "
                f"{risk_sig.get('total_score'):<6.1f} | "
                f"{a.get('risk_band'):<8}"
            )
        print("-" * 75)

        # Print details of drafts generated
        if drafts:
            print("\nDraft Procurement Actions Generated:")
            for idx, d in enumerate(drafts, 1):
                print(f"  {idx}. Alternate Supplier Recommended for {d.get('vendor_name')}: {d.get('alternate_supplier') or 'None'}")
                if args.verbose:
                    print(f"     Risk Summary: {d.get('risk_summary')}")
                    print(f"     WhatsApp Message: {d.get('whatsapp_message')}\n")

        # 4. Save results to output JSON file
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_parameters": {
                "input_source": target_source,
                "risk_threshold": args.threshold,
            },
            "summary": {
                "total_vendors": len(vendors),
                "high_risk_count": len(high_risk_vendors),
            },
            "assessments": assessments,
            "drafts": drafts,
        }
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, cls=DateTimeEncoder)
            
        print(f"\nReport saved successfully to: {args.output}")
        return 0
        
    except Exception as e:
        print(f"\nCLI Execution Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    args = parse_arguments()
    exit_code = asyncio.run(run_cli_scan(args))
    sys.exit(exit_code)
