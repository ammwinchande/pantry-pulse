from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.domain.models import (
    DonationAlert, DispatchProposal, Dispatch, Volunteer,
    SystemStats, AgentTraceLog
)
from src.core.services import PantryPulseService
from src.ports.driven.agent_port import AgentPort
from src.ports.driven.notification_port import NotificationPort

class ApproveDecisionRequest(BaseModel):
    approved_by: str = "Coordinator Sarah L."

class CustomOverrideRequest(BaseModel):
    volunteer_id: str
    notes: str
    approved_by: str = "Coordinator Sarah L."

class RejectDecisionRequest(BaseModel):
    reason: str

class PickupConfirmationRequest(BaseModel):
    verification_code: str

class DeliveryConfirmationRequest(BaseModel):
    final_weight_lbs: Optional[int] = None

class ToggleAvailabilityRequest(BaseModel):
    is_available: bool

def create_router(
    service: PantryPulseService,
    agent_adapter: AgentPort,
    notifier_adapter: NotificationPort
) -> APIRouter:
    router = APIRouter(prefix="/api")

    # --- System Stats ---
    @router.get("/stats", response_model=SystemStats)
    def get_stats():
        return service.get_system_stats()

    # --- Donations ---
    @router.get("/donations", response_model=List[DonationAlert])
    def get_donations():
        return service.list_donations()

    @router.post("/donations", response_model=DispatchProposal)
    def create_donation(donation: DonationAlert):
        return service.ingest_donation_alert(donation)

    @router.post("/donations/simulate", response_model=DispatchProposal)
    def simulate_donation():
        return service.simulate_random_alert()

    # --- Decisions (Human-in-the-Loop) ---
    @router.get("/decisions/pending", response_model=List[DispatchProposal])
    def get_pending_decisions():
        return service.list_pending_decisions()

    @router.post("/decisions/{proposal_id}/approve", response_model=Dispatch)
    def approve_decision(proposal_id: str, req: ApproveDecisionRequest):
        try:
            return service.approve_proposal(proposal_id, approved_by=req.approved_by)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/decisions/{proposal_id}/override-alternative", response_model=Dispatch)
    def override_with_alternative(proposal_id: str, req: ApproveDecisionRequest):
        try:
            return service.override_with_alternative(proposal_id, approved_by=req.approved_by)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/decisions/{proposal_id}/custom-override", response_model=Dispatch)
    def custom_override(proposal_id: str, req: CustomOverrideRequest):
        try:
            return service.custom_override(
                proposal_id,
                volunteer_id=req.volunteer_id,
                notes=req.notes,
                approved_by=req.approved_by
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/decisions/{proposal_id}/reject")
    def reject_decision(proposal_id: str, req: RejectDecisionRequest):
        try:
            service.reject_proposal(proposal_id, reason=req.reason)
            return {"status": "rejected", "proposal_id": proposal_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # --- Dispatches & Delivery Confirmations ---
    @router.get("/dispatches", response_model=List[Dispatch])
    def get_dispatches():
        return service.list_dispatches()

    @router.post("/dispatches/{dispatch_id}/pickup", response_model=Dispatch)
    def confirm_pickup(dispatch_id: str, req: PickupConfirmationRequest):
        try:
            return service.confirm_pickup(dispatch_id, verification_code=req.verification_code)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/dispatches/{dispatch_id}/deliver", response_model=Dispatch)
    def confirm_delivery(dispatch_id: str, req: DeliveryConfirmationRequest):
        try:
            return service.confirm_delivery(dispatch_id, final_weight_lbs=req.final_weight_lbs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # --- Volunteers ---
    @router.get("/volunteers", response_model=List[Volunteer])
    def get_volunteers():
        return service.list_volunteers()

    @router.post("/volunteers/{volunteer_id}/toggle-availability", response_model=Volunteer)
    def toggle_volunteer_availability(volunteer_id: str, req: ToggleAvailabilityRequest):
        try:
            return service.toggle_availability(volunteer_id, is_available=req.is_available)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # --- Observability Traces & Notifications ---
    @router.get("/agent/traces", response_model=List[AgentTraceLog])
    def get_agent_traces():
        return agent_adapter.get_traces()

    @router.get("/notifications")
    def get_notifications():
        return notifier_adapter.get_sent_messages()

    return router
