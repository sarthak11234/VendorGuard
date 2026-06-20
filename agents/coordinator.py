"""
VendorGuard - Coordinator / Orchestrator Agent
Defines the main ADK Workflow graph linking all sub-agents together.
"""

from typing import Any
from google.adk.workflow import START, Workflow
from google.adk.sessions import InMemorySessionService
from google.adk import Runner

from agents.ingest import ingest_agent
from agents.risk_monitor import risk_monitor_agent
from agents.prediction import prediction_agent
from agents.procurement import procurement_agent


def create_coordinator() -> Workflow:
    """Compiles and returns the master VendorGuard Workflow graph."""
    # Define sequential agent transitions
    edges = [
        (START, ingest_agent),
        (ingest_agent, risk_monitor_agent),
        (risk_monitor_agent, prediction_agent),
        (prediction_agent, procurement_agent),
    ]

    return Workflow(
        name="VendorGuardCoordinator",
        edges=edges,
    )


class Coordinator:
    """Wrapper class to manage running the VendorGuard multi-agent pipeline."""

    def __init__(self):
        self.workflow = create_coordinator()

    async def run_mock_scan(self, sheet_url: str = "", csv_path: str = "") -> dict[str, Any]:
        """Runs a complete scan pipeline in-memory for testing or CLI invocation.

        Args:
            sheet_url: Google Sheet URL containing the vendor register.
            csv_path: Local CSV path to the vendor register.

        Returns:
            A dictionary containing processed results (assessments and drafts).
        """
        session_service = InMemorySessionService()
        runner = Runner(
            node=self.workflow,
            session_service=session_service,
            auto_create_session=True,
        )

        input_data = {
            "sheet_url": sheet_url,
            "csv_path": csv_path,
        }

        print("Coordinator: Starting pipeline execution...")
        
        # We need to construct types.Content for Runner input
        from google.genai import types
        import json

        # Convert dictionary to JSON string input
        input_message = types.Content(
            parts=[types.Part.from_text(text=json.dumps(input_data))]
        )

        # Execute workflow
        from google.adk.events.event import Event
        
        results = {}
        async for event in runner.run_async(
            user_id="cli_user",
            session_id="cli_session",
            new_message=input_message,
        ):
            # Print agent status changes or output
            if event.author != "user" and event.output:
                node_name = event.node_info.path.split("/")[-1] if event.node_info else "unknown"
                print(f"[{node_name}] Yielded output.")

        # Re-fetch session state to extract accumulated data
        session = await session_service.get_session(
            app_name=runner.app_name, user_id="cli_user", session_id="cli_session"
        )
        state = session.state if session else {}
        
        return {
            "vendors": state.get("vendors", []),
            "assessments": state.get("assessments", []),
            "drafts": state.get("drafts", []),
        }
