"""
VendorGuard - Pydantic Data Models
Shared data schemas for all agents and API endpoints.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================

class RiskBand(str, Enum):
    """Risk classification bands."""
    LOW = "LOW"          # 0-40: monitor only
    MEDIUM = "MEDIUM"    # 41-65: flag on dashboard
    HIGH = "HIGH"        # 66-100: auto-trigger procurement


class ScanStage(str, Enum):
    """Scan pipeline stages."""
    QUEUED = "QUEUED"
    INGESTING = "INGESTING"
    MONITORING = "MONITORING"
    PREDICTING = "PREDICTING"
    DRAFTING = "DRAFTING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


# ============================================
# Vendor Models (Input from CSV/Sheet)
# ============================================

class Vendor(BaseModel):
    """Vendor record from manufacturer's register."""
    vendor_id: str = Field(..., description="Unique vendor identifier, e.g. VND-001")
    vendor_name: str = Field(..., description="Full vendor company name")
    city: str = Field(..., description="Vendor's city location")
    state: str = Field(..., description="Vendor's state")
    commodity: str = Field(..., description="Primary commodity supplied")
    open_po_value_inr: int = Field(..., description="Current open PO value in INR")
    lead_time_days: int = Field(..., description="Standard lead time in days")
    historical_ontime_pct: float = Field(..., description="Historical on-time delivery percentage")
    last_delivery_date: Optional[date] = Field(None, description="Date of last delivery")
    contact_whatsapp: Optional[str] = Field(None, description="WhatsApp contact number")
    backup_vendor_id: Optional[str] = Field(None, description="Backup vendor ID if available")


# ============================================
# Risk Signal Models (from Risk Monitor Agent)
# ============================================

class RiskSource(BaseModel):
    """Individual risk signal from a specific data source."""
    source_name: str = Field(..., description="Data source name, e.g. 'OpenWeatherMap'")
    category: str = Field(..., description="Risk category: weather, news, commodity, historical")
    score: float = Field(..., ge=0, description="Risk score for this source")
    max_score: float = Field(..., gt=0, description="Maximum possible score for this category")
    evidence: str = Field(..., description="Evidence text explaining the risk signal")
    source_url: Optional[str] = Field(None, description="URL citation for the evidence")


class RiskSignal(BaseModel):
    """Aggregated risk signals for a single vendor."""
    vendor_id: str
    weather_risk: RiskSource = Field(..., description="Weather risk signal (max 30 points)")
    news_risk: RiskSource = Field(..., description="News/disruption risk signal (max 30 points)")
    commodity_risk: RiskSource = Field(..., description="Commodity price risk signal (max 20 points)")
    historical_risk: RiskSource = Field(..., description="Historical performance risk (max 20 points)")
    total_score: float = Field(..., ge=0, le=100, description="Composite risk score 0-100")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Risk Assessment (from Prediction Agent)
# ============================================

class RiskAssessment(BaseModel):
    """Complete risk assessment for a vendor."""
    vendor: Vendor
    risk_signal: RiskSignal
    risk_band: RiskBand
    requires_action: bool = Field(..., description="Whether immediate action is needed")
    action_summary: Optional[str] = Field(None, description="Brief recommended action text")
    at_risk_po_value: Optional[int] = Field(None, description="Value of POs currently at risk")


# ============================================
# Procurement Draft (from Procurement Agent)
# ============================================

class ProcurementDraft(BaseModel):
    """AI-generated procurement action for a high-risk vendor."""
    vendor_id: str
    vendor_name: str
    risk_summary: str = Field(..., description="Plain-language risk summary")
    recommended_action: str = Field(..., description="Recommended procurement action")
    alternate_supplier: Optional[str] = Field(None, description="Alternate supplier recommendation")
    alternate_supplier_id: Optional[str] = Field(None, description="Backup vendor ID")
    draft_po_text: str = Field(..., description="Draft purchase order text")
    whatsapp_message: str = Field(..., description="WhatsApp-ready alert message")
    urgency: str = Field(default="HIGH", description="Urgency level")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Scan Status (for API polling)
# ============================================

class ScanStatus(BaseModel):
    """Current status of a running scan."""
    scan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: ScanStage = Field(default=ScanStage.QUEUED)
    stage_message: Optional[str] = Field(None, description="Human-readable status message")
    vendor_count: Optional[int] = Field(None, description="Number of vendors being scanned")
    elapsed_seconds: Optional[float] = Field(None, description="Time elapsed since scan start")
    error: Optional[str] = Field(None, description="Error message if status is FAILED")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ScanResult(BaseModel):
    """Complete scan result returned on completion."""
    scan_id: str
    status: ScanStage
    vendor_count: int
    assessments: list[RiskAssessment] = []
    drafts: list[ProcurementDraft] = []
    elapsed_seconds: float
    started_at: datetime
    completed_at: datetime


# ============================================
# API Response Models
# ============================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0"


class ScanTriggerRequest(BaseModel):
    """Request body for POST /api/scan."""
    sheet_url: Optional[str] = Field(None, description="Google Sheet URL")
    csv_path: Optional[str] = Field(None, description="Local CSV file path")
    threshold: int = Field(default=65, ge=0, le=100, description="Risk score threshold")


class ScanTriggerResponse(BaseModel):
    """Response body for POST /api/scan."""
    scan_id: str
    message: str = "Scan started successfully"
