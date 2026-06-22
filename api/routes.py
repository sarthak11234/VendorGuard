"""
VendorGuard - FastAPI Router
Implements the web API endpoints and background scan pipeline orchestration.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from api.models import (
    ScanTriggerRequest,
    ScanTriggerResponse,
    ScanStatus,
    ScanStage,
    RiskAssessment,
    ProcurementDraft,
)

router = APIRouter()

# In-memory scan database: scan_id -> dict
scans_db: Dict[str, Dict[str, Any]] = {}
latest_scan_id: Optional[str] = None


async def run_scan_pipeline(scan_id: str, request: ScanTriggerRequest):
    """Executes the Google ADK workflow in the background and updates the scan status."""
    from google.adk.sessions import InMemorySessionService
    from google.adk import Runner
    from google.genai import types
    import json
    
    from agents.coordinator import create_coordinator
    
    start_time = datetime.utcnow()
    scans_db[scan_id]["status"].status = ScanStage.INGESTING
    scans_db[scan_id]["status"].stage_message = "Ingesting vendor data from registry..."
    
    try:
        # Build ADK Workflow and Runner
        workflow = create_coordinator()
        session_service = InMemorySessionService()
        runner = Runner(
            node=workflow,
            session_service=session_service,
            auto_create_session=True,
        )
        
        # Prepare input JSON payload
        input_payload = {
            "sheet_url": request.sheet_url or "",
            "csv_path": request.csv_path or "",
        }
        
        input_message = types.Content(
            parts=[types.Part.from_text(text=json.dumps(input_payload))]
        )
        
        # Execute workflow asynchronously and capture events
        async for event in runner.run_async(
            user_id="web_user",
            session_id=scan_id,
            new_message=input_message,
        ):
            # Update elapsed time
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            scans_db[scan_id]["status"].elapsed_seconds = round(elapsed, 1)
            
            # Map node completions/outputs to workflow stages
            if event.author != "user" and event.output:
                node_name = event.node_info.path.split("/")[-1] if event.node_info else "unknown"
                
                # Access current state from session
                session = await session_service.get_session(
                    app_name=runner.app_name, user_id="web_user", session_id=scan_id
                )
                
                if node_name == "IngestAgent":
                    vendors = session.state.get("vendors", [])
                    scans_db[scan_id]["status"].vendor_count = len(vendors)
                    scans_db[scan_id]["status"].status = ScanStage.MONITORING
                    scans_db[scan_id]["status"].stage_message = f"Ingested {len(vendors)} vendors. Evaluating risk signals..."
                    
                elif node_name == "RiskMonitorAgent":
                    scans_db[scan_id]["status"].status = ScanStage.PREDICTING
                    scans_db[scan_id]["status"].stage_message = "Synthesizing risk bands and composite scores..."
                    
                elif node_name == "PredictionAgent":
                    scans_db[scan_id]["status"].status = ScanStage.DRAFTING
                    scans_db[scan_id]["status"].stage_message = "Drafting early POs and action alerts..."

        # Retrieve completed session state
        session = await session_service.get_session(
            app_name=runner.app_name, user_id="web_user", session_id=scan_id
        )
        state = session.state if session else {}
        
        # Validate and store final assessments and drafts
        assessments_data = state.get("assessments", [])
        drafts_data = state.get("drafts", [])
        
        assessments = [RiskAssessment(**a) for a in assessments_data]
        drafts = [ProcurementDraft(**d) for d in drafts_data]
        
        scans_db[scan_id]["assessments"] = assessments
        scans_db[scan_id]["drafts"] = drafts
        
        # Update status to COMPLETE
        scans_db[scan_id]["status"].status = ScanStage.COMPLETE
        scans_db[scan_id]["status"].stage_message = "Scan completed successfully."
        scans_db[scan_id]["status"].completed_at = datetime.utcnow()
        scans_db[scan_id]["status"].elapsed_seconds = round((datetime.utcnow() - start_time).total_seconds(), 1)
        
        # Set this scan as the latest completed scan
        global latest_scan_id
        latest_scan_id = scan_id
        print(f"Scan {scan_id} completed successfully in {scans_db[scan_id]['status'].elapsed_seconds}s.")
        
    except Exception as e:
        print(f"Scan {scan_id} failed: {e}")
        scans_db[scan_id]["status"].status = ScanStage.FAILED
        scans_db[scan_id]["status"].stage_message = f"Scan failed: {str(e)}"
        scans_db[scan_id]["status"].error = str(e)
        scans_db[scan_id]["status"].completed_at = datetime.utcnow()
        scans_db[scan_id]["status"].elapsed_seconds = round((datetime.utcnow() - start_time).total_seconds(), 1)


@router.post("/scan", response_model=ScanTriggerResponse, tags=["Scans"])
async def trigger_scan(request: ScanTriggerRequest, background_tasks: BackgroundTasks):
    """Triggers a supply chain risk scan asynchronously."""
    scan_id = str(uuid.uuid4())
    
    # Initialize ScanStatus record
    status_record = ScanStatus(
        scan_id=scan_id,
        status=ScanStage.QUEUED,
        stage_message="Queuing scan execution...",
        started_at=datetime.utcnow(),
    )
    
    scans_db[scan_id] = {
        "status": status_record,
        "assessments": [],
        "drafts": [],
    }
    
    background_tasks.add_task(run_scan_pipeline, scan_id, request)
    return ScanTriggerResponse(scan_id=scan_id, message="Scan started successfully")


@router.get("/scan/{scan_id}", response_model=ScanStatus, tags=["Scans"])
async def get_scan_status(scan_id: str):
    """Retrieves the status of a specific scan run."""
    if scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    # Update elapsed time if still running
    status = scans_db[scan_id]["status"]
    if status.status not in [ScanStage.COMPLETE, ScanStage.FAILED]:
        status.elapsed_seconds = round((datetime.utcnow() - status.started_at).total_seconds(), 1)
        
    return status


@router.get("/vendors", response_model=List[RiskAssessment], tags=["Results"])
async def get_vendors(scan_id: Optional[str] = None):
    """Returns the list of RiskAssessments from the specified or latest completed scan."""
    target_scan_id = scan_id or latest_scan_id
    if not target_scan_id:
        # Return empty list if no scans have run yet
        return []
        
    if target_scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return scans_db[target_scan_id]["assessments"]


@router.get("/vendors/{vendor_id}", response_model=Dict[str, Any], tags=["Results"])
async def get_vendor_detail(vendor_id: str, scan_id: Optional[str] = None):
    """Returns the full RiskAssessment and optional ProcurementDraft for a vendor."""
    target_scan_id = scan_id or latest_scan_id
    if not target_scan_id:
        raise HTTPException(status_code=400, detail="No scan execution results available")
        
    if target_scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    assessments = scans_db[target_scan_id]["assessments"]
    drafts = scans_db[target_scan_id]["drafts"]
    
    # Find the specific vendor assessment
    assessment = next((a for a in assessments if a.vendor.vendor_id == vendor_id), None)
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found in this scan")
        
    # Find procurement draft if vendor is high-risk
    draft = next((d for d in drafts if d.vendor_id == vendor_id), None)
    
    return {
        "assessment": assessment,
        "draft": draft,
    }


@router.get("/alerts", response_model=List[ProcurementDraft], tags=["Results"])
async def get_alerts(scan_id: Optional[str] = None):
    """Returns the list of generated ProcurementDrafts for high-risk vendors."""
    target_scan_id = scan_id or latest_scan_id
    if not target_scan_id:
        return []
        
    if target_scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return scans_db[target_scan_id]["drafts"]
