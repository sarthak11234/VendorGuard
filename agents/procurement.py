"""
VendorGuard - Procurement Drafting Agent
Generates early PO drafts and WhatsApp alerts for high-risk vendors using Gemini.
"""

from datetime import datetime
from typing import Any
from google.adk.workflow import node
from google.adk import Context
from google import genai
from api.models import RiskAssessment, ProcurementDraft, RiskBand
from config import config


@node(name="ProcurementAgent")
async def procurement_agent(ctx: Context, node_input: list[RiskAssessment]) -> list[ProcurementDraft]:
    """Generates procurement drafts and alerts for vendors flagged as HIGH risk.

    Args:
        ctx: Workflow invocation context.
        node_input: List of RiskAssessment objects from PredictionAgent.

    Returns:
        List of ProcurementDraft objects.
    """
    print("ProcurementAgent: Analyzing risk assessments to draft actions...")
    drafts = []

    # Filter to HIGH risk assessments only
    high_risk_assessments = [a for a in node_input if a.risk_band == RiskBand.HIGH]
    print(f"ProcurementAgent: Found {len(high_risk_assessments)} HIGH risk vendors.")

    # Limit drafts to 3 max to manage API latency and token usage
    target_assessments = high_risk_assessments[:3]

    # Initialize Gemini client if API key is available
    gemini_client = None
    if config.GEMINI_API_KEY:
        try:
            gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
        except Exception as e:
            print(f"ProcurementAgent Warning: Failed to initialize GenAI Client: {e}")

    # Helper map for backup vendors from the register
    vendors_list = ctx.state.get("vendors", [])
    vendors_map = {v["vendor_id"]: v for v in vendors_list}

    for assessment in target_assessments:
        vendor = assessment.vendor
        signal = assessment.risk_signal

        # Determine if backup vendor exists
        backup_name = None
        backup_id = vendor.backup_vendor_id
        if backup_id and backup_id in vendors_map:
            backup_name = vendors_map[backup_id].get("vendor_name")

        # Compile evidence summary
        evidences = []
        if signal.weather_risk.score > 15:
            evidences.append(f"Weather: {signal.weather_risk.evidence}")
        if signal.news_risk.score > 15:
            evidences.append(f"News: {signal.news_risk.evidence}")
        if signal.commodity_risk.score > 10:
            evidences.append(f"Commodity: {signal.commodity_risk.evidence}")
        if signal.historical_risk.score > 10:
            evidences.append(f"Performance: {signal.historical_risk.evidence}")

        evidence_str = "; ".join(evidences) if evidences else "General risk score elevation."

        # Initialize default mock draft texts in case Gemini is not used or fails
        risk_summary = f"Severe disruptions detected: {evidence_str}"
        recommended_action = (
            f"Pre-emptively place early order or shift procurement to backup supplier '{backup_name or 'N/A'}'."
        )
        draft_po_text = (
            f"DRAFT PURCHASE ORDER\n"
            f"To: {backup_name or vendor.vendor_name}\n"
            f"Item: {vendor.commodity}\n"
            f"Value: INR {vendor.open_po_value_inr:,}\n"
            f"Note: Expedited delivery request due to high risk at primary supplier."
        )
        whatsapp_message = (
            f"⚠️ *VendorGuard Risk Alert* ⚠️\n\n"
            f"Primary supplier *{vendor.vendor_name}* ({vendor.city}) is flagged at *HIGH RISK* (Score: {signal.total_score:.0f}).\n"
            f"Reason: {evidence_str}\n\n"
            f"Recommended: {recommended_action}"
        )

        # Attempt to use Gemini to generate rich, personalized content
        if gemini_client:
            try:
                prompt = (
                    f"You are a Senior Supply Chain Analyst at an SME manufacturing firm in India. "
                    f"Write a professional, concise summary and action plan for a high-risk vendor.\n\n"
                    f"Vendor Details:\n"
                    f"- Name: {vendor.vendor_name}\n"
                    f"- Commodity: {vendor.commodity}\n"
                    f"- City/State: {vendor.city}, {vendor.state}\n"
                    f"- Open PO Value: INR {vendor.open_po_value_inr:,}\n"
                    f"- Backup Vendor Name: {backup_name or 'None listed'}\n\n"
                    f"Risk Evidence: {evidence_str}\n\n"
                    f"Provide your response in JSON format matching this schema:\n"
                    f"{{\n"
                    f"  \"risk_summary\": \"<Concise 1-2 sentence risk explanation>\",\n"
                    f"  \"recommended_action\": \"<Clear next action: e.g. place early PO or switch to backup>\",\n"
                    f"  \"draft_po_text\": \"<A formal draft purchase order containing quantity, item name, and delivery terms>\",\n"
                    f"  \"whatsapp_message\": \"<A concise WhatsApp message starting with warning emojis, highlighting the risk and next step>\"\n"
                    f"}}\n"
                    f"Do not include any other text or markdown formatting except the raw JSON string."
                )

                response = gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                )
                import json
                cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned_text)

                risk_summary = data.get("risk_summary", risk_summary)
                recommended_action = data.get("recommended_action", recommended_action)
                draft_po_text = data.get("draft_po_text", draft_po_text)
                whatsapp_message = data.get("whatsapp_message", whatsapp_message)

            except Exception as e:
                print(f"ProcurementAgent: Gemini generation failed ({e}). Using robust fallback template.")

        draft = ProcurementDraft(
            vendor_id=vendor.vendor_id,
            vendor_name=vendor.vendor_name,
            risk_summary=risk_summary,
            recommended_action=recommended_action,
            alternate_supplier=backup_name,
            alternate_supplier_id=backup_id,
            draft_po_text=draft_po_text,
            whatsapp_message=whatsapp_message,
            urgency="HIGH",
            generated_at=datetime.utcnow(),
        )
        drafts.append(draft)

    # Save drafts to context state
    ctx.state["drafts"] = [d.model_dump() for d in drafts]

    print(f"ProcurementAgent: Completed drafting for {len(drafts)} high-risk vendors.")
    return drafts
