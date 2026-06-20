"""
VendorGuard - Prediction & Synthesis Agent
Combines risk signals and historical vendor records to predict overall risk and band.
"""

from typing import Any
from google.adk.workflow import node
from google.adk import Context
from api.models import RiskSignal, RiskAssessment, RiskBand, Vendor
from config import config


@node(name="PredictionAgent")
async def prediction_agent(ctx: Context, node_input: list[RiskSignal]) -> list[RiskAssessment]:
    """Evaluates risk signals against vendor profiles to compute composite risk and bands.

    Args:
        ctx: Workflow invocation context (contains shared state).
        node_input: List of RiskSignal objects from RiskMonitorAgent.

    Returns:
        List of RiskAssessment objects.
    """
    print(f"PredictionAgent: Running synthesis for {len(node_input)} risk signals...")

    # Retrieve vendors list from context state
    vendors_list = ctx.state.get("vendors", [])
    vendors_map = {v["vendor_id"]: Vendor(**v) if isinstance(v, dict) else v for v in vendors_list}

    assessments = []
    for signal in node_input:
        vendor = vendors_map.get(signal.vendor_id)
        if not vendor:
            print(f"PredictionAgent Warning: Vendor {signal.vendor_id} not found in state. Skipping...")
            continue

        score = signal.total_score

        # Determine risk band
        if score <= config.LOW_RISK_MAX:
            band = RiskBand.LOW
            action = False
            summary = "Status OK. Regular monitoring."
        elif score <= config.MEDIUM_RISK_MAX:
            band = RiskBand.MEDIUM
            action = False
            summary = "Elevated risk. Monitor closely."
        else:
            band = RiskBand.HIGH
            action = True
            summary = "HIGH RISK. Immediate procurement intervention recommended."

        assessment = RiskAssessment(
            vendor=vendor,
            risk_signal=signal,
            risk_band=band,
            requires_action=action,
            action_summary=summary,
            at_risk_po_value=vendor.open_po_value_inr if action else 0,
        )
        assessments.append(assessment)

    # Store assessments in context state for downstream nodes and API reference
    ctx.state["assessments"] = [a.model_dump() for a in assessments]

    # Sort assessments: High risk first, then by score descending
    assessments.sort(key=lambda x: (x.risk_band == RiskBand.HIGH, x.risk_signal.total_score), reverse=True)

    print(f"PredictionAgent: Generated {len(assessments)} risk assessments.")
    return assessments
