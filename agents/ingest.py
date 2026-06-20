"""
VendorGuard - Ingest Agent
Ingests vendor register data from a Google Sheet URL, a local CSV path,
or falls back to the default synthetic CSV register.
"""

import csv
import io
from typing import Any
import httpx

from google.adk import Context
from google.adk.workflow import node
from api.models import Vendor
from config import config


@node(name="IngestAgent")
async def ingest_agent(ctx: Context, node_input: Any) -> list[Vendor]:
    """Ingests vendor register data from local files or Google Sheets.

    Args:
        ctx: Workflow invocation context.
        node_input: The input data containing 'sheet_url' or 'csv_path', or a
          direct URL/path string.

    Returns:
        A list of validated Vendor objects.
    """
    csv_content = ""
    source_info = ""

    sheet_url = None
    csv_path = None

    # Determine input type
    if isinstance(node_input, dict):
        sheet_url = node_input.get("sheet_url")
        csv_path = node_input.get("csv_path")
    elif isinstance(node_input, str):
        if node_input.startswith("http://") or node_input.startswith("https://"):
            sheet_url = node_input
        else:
            csv_path = node_input

    # 1. Download Google Sheet if URL is provided
    if sheet_url:
        try:
            # Transform view/edit link to public CSV export URL
            export_url = sheet_url
            if "/edit" in sheet_url:
                export_url = sheet_url.split("/edit")[0] + "/export?format=csv"
            elif "/view" in sheet_url:
                export_url = sheet_url.split("/view")[0] + "/export?format=csv"
            elif not sheet_url.endswith("/export?format=csv") and "/d/" in sheet_url:
                export_url = sheet_url.rstrip("/") + "/export?format=csv"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(export_url, follow_redirects=True)
                if response.status_code == 200:
                    csv_content = response.text
                    source_info = f"Google Sheet export link: {export_url}"
                else:
                    raise Exception(f"HTTP status {response.status_code}")
        except Exception as e:
            print(f"IngestAgent Warning: Failed to fetch Google Sheet: {e}. Falling back...")

    # 2. Read local CSV file if path is provided or Sheet download failed
    if not csv_content and csv_path:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                csv_content = f.read()
                source_info = f"Local CSV file: {csv_path}"
        except Exception as e:
            print(f"IngestAgent Warning: Failed to read local CSV: {e}. Falling back...")

    # 3. Final fallback to seeded synthetic data
    if not csv_content:
        default_path = config.SYNTHETIC_DATA_PATH
        try:
            with open(default_path, "r", encoding="utf-8") as f:
                csv_content = f.read()
                source_info = f"Fallback synthetic file: {default_path}"
        except Exception as e:
            raise Exception(f"IngestAgent Critical: Failed to load synthetic vendor data: {e}")

    print(f"IngestAgent: Successfully loaded registry from {source_info}")

    # 4. Parse CSV data
    vendors = []
    f_buffer = io.StringIO(csv_content.strip())
    reader = csv.DictReader(f_buffer)

    for row in reader:
        # Strip whitespaces from keys and values
        cleaned_row = {
            k.strip(): v.strip() for k, v in row.items() if k is not None and v is not None
        }

        # Handle different casings and headers variations
        mappings = {
            "vendor_id": ["vendor_id", "vendor id", "id", "vendorid"],
            "vendor_name": ["vendor_name", "vendor name", "name", "vendorname"],
            "city": ["city", "vendor_city", "vendor city"],
            "state": ["state", "vendor_state", "vendor state"],
            "commodity": ["commodity", "item", "product"],
            "open_po_value_inr": [
                "open_po_value_inr",
                "open po value inr",
                "po value",
                "povalue",
                "open_po_value",
                "po_value",
            ],
            "lead_time_days": [
                "lead_time_days",
                "lead time days",
                "lead time",
                "leadtime",
                "lead_time_days",
            ],
            "historical_ontime_pct": [
                "historical_ontime_pct",
                "historical on-time pct",
                "historical_ontime",
                "ontime pct",
                "on time %",
                "on_time_pct",
            ],
            "last_delivery_date": [
                "last_delivery_date",
                "last delivery date",
                "last delivery",
                "last_delivery",
            ],
            "contact_whatsapp": [
                "contact_whatsapp",
                "contact whatsapp",
                "whatsapp",
                "contact_number",
                "phone",
            ],
            "backup_vendor_id": [
                "backup_vendor_id",
                "backup vendor id",
                "backup_vendor",
                "backup vendor",
            ],
        }

        mapped_row = {}
        for field_name, alternatives in mappings.items():
            for alt in alternatives:
                found_key = next(
                    (k for k in cleaned_row.keys() if k.lower() == alt.lower()), None
                )
                if found_key:
                    mapped_row[field_name] = cleaned_row[found_key]
                    break

        # Treat empty string values as None for optional fields
        for opt_field in ["last_delivery_date", "contact_whatsapp", "backup_vendor_id"]:
            if opt_field in mapped_row and not mapped_row[opt_field]:
                mapped_row[opt_field] = None

        # Convert numeric types
        try:
            if "open_po_value_inr" in mapped_row:
                mapped_row["open_po_value_inr"] = int(float(mapped_row["open_po_value_inr"]))
            if "lead_time_days" in mapped_row:
                mapped_row["lead_time_days"] = int(float(mapped_row["lead_time_days"]))
            if "historical_ontime_pct" in mapped_row:
                mapped_row["historical_ontime_pct"] = float(mapped_row["historical_ontime_pct"])
        except ValueError as e:
            print(f"IngestAgent Warning: Numeric field conversion error: {e} in row {row}")
            continue

        try:
            vendor_obj = Vendor(**mapped_row)
            vendors.append(vendor_obj)
        except Exception as e:
            print(f"IngestAgent Warning: Pydantic validation failed for row {row}: {e}")
            continue

    print(f"IngestAgent: Parsed {len(vendors)} vendors successfully.")
    ctx.state["vendors"] = [v.model_dump() for v in vendors]
    return vendors
