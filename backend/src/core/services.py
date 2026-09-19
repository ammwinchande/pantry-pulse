import logging
import random
import secrets
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from src.domain.models import (
    DonationAlert, DonationStatus, FoodCategory, GeoLocation,
    Volunteer, VolunteerStatus, DispatchProposal, Dispatch,
    DispatchStatus, SystemStats
)
from src.domain.exceptions import (
    DonationNotFoundError, VolunteerNotFoundError, ProposalNotFoundError,
    DispatchNotFoundError, IncompatibleVolunteerError, InvalidStateTransitionError
)
from src.ports.driving.donation_use_case import DonationUseCase
from src.ports.driving.dispatch_use_case import DispatchUseCase
from src.ports.driving.volunteer_use_case import VolunteerUseCase
from src.ports.driven.volunteer_repo_port import VolunteerRepositoryPort
from src.ports.driven.donation_repo_port import DonationRepositoryPort
from src.ports.driven.dispatch_repo_port import DispatchRepositoryPort
from src.ports.driven.agent_port import AgentPort
from src.ports.driven.notification_port import NotificationPort

logger = logging.getLogger("PantryPulseService")


class PantryPulseService(DonationUseCase, DispatchUseCase, VolunteerUseCase):
    def __init__(
        self,
        volunteer_repo: VolunteerRepositoryPort,
        donation_repo: DonationRepositoryPort,
        dispatch_repo: DispatchRepositoryPort,
        agent: AgentPort,
        notifier: NotificationPort
    ):
        self._volunteers = volunteer_repo
        self._donations = donation_repo
        self._dispatches = dispatch_repo
        self._agent = agent
        self._notifier = notifier

    # --- Donation Use Case Implementation ---
    def ingest_donation_alert(self, donation: DonationAlert) -> DispatchProposal:
        logger.info(
            "Donation alert received: %s (%s, %s lbs, cold_chain=%s, fragile=%s)",
            donation.id, donation.donor_name, donation.estimated_weight_lbs,
            donation.requires_cold_chain, donation.is_fragile,
        )

        # Save donation alert
        saved_donation = self._donations.save(donation)
        self._donations.update_status(saved_donation.id, DonationStatus.ANALYZING)

        # Notify coordinator dashboard that an alert is being processed
        self._notifier.notify_coordinator_urgent_decision(saved_donation)

        # Query active available volunteers
        available_volunteers = self._volunteers.list_available()
        if not available_volunteers:
            # If all are off-duty/dispatched, include all registered for emergency triage
            available_volunteers = self._volunteers.list_all()
            logger.warning(
                "No available volunteers for %s — falling back to full fleet (%d) for emergency triage.",
                saved_donation.id, len(available_volunteers),
            )

        # Run Strands Agent evaluation
        proposal = self._agent.evaluate_and_propose(saved_donation, available_volunteers)

        # Save proposal and update donation state
        saved_proposal = self._dispatches.save_proposal(proposal)
        self._donations.update_status(saved_donation.id, DonationStatus.PENDING_DECISION)

        primary = saved_proposal.primary_candidate
        alt = saved_proposal.alternative_candidate
        logger.info(
            "Dispatch proposal generated for %s: primary=%s (match=%.2f)%s, urgency=%s.",
            saved_donation.id,
            primary.name,
            primary.match_score,
            f", alternative={alt.name}" if alt else "",
            saved_proposal.urgency_level,
        )

        return saved_proposal

    def list_donations(self) -> List[DonationAlert]:
        return self._donations.list_all()

    def get_donation(self, donation_id: str) -> Optional[DonationAlert]:
        return self._donations.get_by_id(donation_id)

    def simulate_random_alert(self) -> DispatchProposal:
        scenarios = [
            {
                "donor_name": "Whole Foods Market - Downtown",
                "contact": "Dave Manager",
                "phone": "+1 (206) 555-3344",
                "address": "2210 Westlake Ave",
                "neighborhood": "South Lake Union",
                "lat": 47.6185,
                "lon": -122.3382,
                "category": FoodCategory.PRODUCE,
                "description": "5 crates crisp organic apples, celery, and heirloom carrots",
                "weight": 110,
                "boxes": 5,
                "cold_chain": False,
                "fragile": False,
                "minutes": 90,
                "instructions": "Loading dock entrance on 8th Ave. Ring bell for produce manager."
            },
            {
                "donor_name": "Catering By Design (Convention Center)",
                "contact": "Chef Monique",
                "phone": "+1 (206) 555-7721",
                "address": "705 Pike St",
                "neighborhood": "Downtown",
                "lat": 47.6114,
                "lon": -122.3325,
                "category": FoodCategory.PREPARED_MEALS,
                "description": "70 gourmet catered boxed lunches (chicken, quinoa & vegan wraps)",
                "weight": 75,
                "boxes": 6,
                "cold_chain": True,
                "fragile": True,
                "minutes": 60,
                "instructions": "Convention ended early. Food packed in Cambro thermal boxes."
            },
            {
                "donor_name": "Metropolitan Market - Uptown",
                "contact": "Julian Vance",
                "phone": "+1 (206) 555-9922",
                "address": "100 Mercer St",
                "neighborhood": "Lower Queen Anne",
                "lat": 47.6248,
                "lon": -122.3530,
                "category": FoodCategory.DAIRY_FROZEN,
                "description": "Yogurt cases, artisan cheeses, and frozen prepared family meals",
                "weight": 160,
                "boxes": 8,
                "cold_chain": True,
                "fragile": False,
                "minutes": 75,
                "instructions": "Must have cold storage capability. Ask for dairy lead in back bay."
            },
            {
                "donor_name": "Macrina Bakery & Cafe",
                "contact": "Chef Roberto",
                "phone": "+1 (206) 555-4411",
                "address": "2408 1st Ave",
                "neighborhood": "Belltown",
                "lat": 47.6148,
                "lon": -122.3486,
                "category": FoodCategory.BAKERY_DRY,
                "description": "45 loaves seeded sourdough, brioche rolls, and focaccia trays",
                "weight": 65,
                "boxes": 4,
                "cold_chain": False,
                "fragile": False,
                "minutes": 45,
                "instructions": "Pick up at back kitchen alley entrance before 5 PM."
            }
        ]

        pick = random.choice(scenarios)
        now = datetime.now(timezone.utc)
        alert = DonationAlert(
            donor_name=pick["donor_name"],
            donor_contact_name=pick["contact"],
            donor_phone=pick["phone"],
            donor_address=GeoLocation(
                latitude=pick["lat"],
                longitude=pick["lon"],
                address=pick["address"],
                neighborhood=pick["neighborhood"]
            ),
            food_category=pick["category"],
            item_description=pick["description"],
            estimated_weight_lbs=pick["weight"],
            box_count=pick["boxes"],
            requires_cold_chain=pick["cold_chain"],
            is_fragile=pick["fragile"],
            reported_at=now,
            pickup_deadline=now + timedelta(minutes=pick["minutes"]),
            status=DonationStatus.REPORTED,
            special_instructions=pick["instructions"]
        )

        return self.ingest_donation_alert(alert)

    # --- Dispatch Use Case Implementation ---
    def list_pending_decisions(self) -> List[DispatchProposal]:
        return self._dispatches.list_pending_proposals()

    def approve_proposal(self, proposal_id: str, approved_by: str = "Coordinator Sarah L.") -> Dispatch:
        proposal = self._dispatches.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ProposalNotFoundError(proposal_id)
        self._ensure_proposal_pending(proposal)

        donation = self._donations.get_by_id(proposal.donation_id)
        if not donation:
            raise DonationNotFoundError(proposal.donation_id)

        primary_candidate = proposal.primary_candidate
        volunteer = self._volunteers.get_by_id(primary_candidate.volunteer_id)
        if not volunteer:
            raise VolunteerNotFoundError(primary_candidate.volunteer_id)

        return self._execute_dispatch(
            proposal=proposal,
            donation=donation,
            volunteer=volunteer,
            approved_by=approved_by,
            notes=f"Approved AI recommendation: {primary_candidate.name}"
        )

    def override_with_alternative(self, proposal_id: str, approved_by: str = "Coordinator Sarah L.") -> Dispatch:
        proposal = self._dispatches.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ProposalNotFoundError(proposal_id)
        self._ensure_proposal_pending(proposal)

        if not proposal.alternative_candidate:
            raise IncompatibleVolunteerError("No alternative candidate specified in proposal.")

        donation = self._donations.get_by_id(proposal.donation_id)
        if not donation:
            raise DonationNotFoundError(proposal.donation_id)

        alt_candidate = proposal.alternative_candidate
        volunteer = self._volunteers.get_by_id(alt_candidate.volunteer_id)
        if not volunteer:
            raise VolunteerNotFoundError(alt_candidate.volunteer_id)

        return self._execute_dispatch(
            proposal=proposal,
            donation=donation,
            volunteer=volunteer,
            approved_by=approved_by,
            notes=f"Coordinator override: selected alternative candidate {alt_candidate.name}"
        )

    def custom_override(
        self, proposal_id: str, volunteer_id: str, notes: str, approved_by: str = "Coordinator Sarah L."
    ) -> Dispatch:
        proposal = self._dispatches.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ProposalNotFoundError(proposal_id)
        self._ensure_proposal_pending(proposal)

        donation = self._donations.get_by_id(proposal.donation_id)
        if not donation:
            raise DonationNotFoundError(proposal.donation_id)

        volunteer = self._volunteers.get_by_id(volunteer_id)
        if not volunteer:
            raise VolunteerNotFoundError(volunteer_id)

        return self._execute_dispatch(
            proposal=proposal,
            donation=donation,
            volunteer=volunteer,
            approved_by=approved_by,
            notes=f"Manual coordinator assignment: {notes}"
        )

    def reject_proposal(self, proposal_id: str, reason: str) -> None:
        proposal = self._dispatches.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ProposalNotFoundError(proposal_id)

        proposal.status = DispatchStatus.REJECTED
        self._dispatches.save_proposal(proposal)

        donation = self._donations.get_by_id(proposal.donation_id)
        if donation:
            donation.status = DonationStatus.CANCELLED
            self._donations.save(donation)

        logger.info("Proposal %s rejected (donation %s cancelled): %s",
                    proposal_id, proposal.donation_id, reason)

    def confirm_pickup(self, dispatch_id: str, verification_code: str) -> Dispatch:
        dispatch = self._dispatches.get_dispatch_by_id(dispatch_id)
        if not dispatch:
            raise DispatchNotFoundError(dispatch_id)
        if dispatch.status != DispatchStatus.APPROVED:
            raise InvalidStateTransitionError(
                "dispatch", dispatch.status.value, DispatchStatus.PICKED_UP.value
            )
        if not secrets.compare_digest(verification_code, dispatch.pickup_verification_code):
            raise IncompatibleVolunteerError("Invalid pickup verification code.")

        now = datetime.now(timezone.utc)
        dispatch.status = DispatchStatus.PICKED_UP
        dispatch.picked_up_at = now
        self._dispatches.save_dispatch(dispatch)

        # Update donation and volunteer states
        self._donations.update_status(dispatch.donation_id, DonationStatus.IN_TRANSIT)
        self._volunteers.update_status(dispatch.volunteer_id, VolunteerStatus.EN_ROUTE)

        logger.info("Pickup confirmed for dispatch %s (%s) — food in transit.",
                    dispatch_id, dispatch.volunteer_name)

        return dispatch

    def confirm_delivery(self, dispatch_id: str, final_weight_lbs: Optional[int] = None) -> Dispatch:
        dispatch = self._dispatches.get_dispatch_by_id(dispatch_id)
        if not dispatch:
            raise DispatchNotFoundError(dispatch_id)
        if dispatch.status != DispatchStatus.PICKED_UP:
            raise InvalidStateTransitionError(
                "dispatch", dispatch.status.value, DispatchStatus.DELIVERED.value
            )

        now = datetime.now(timezone.utc)
        dispatch.status = DispatchStatus.DELIVERED
        dispatch.delivered_at = now
        if final_weight_lbs is not None:
            dispatch.weight_rescued_lbs = final_weight_lbs

        self._dispatches.save_dispatch(dispatch)

        # Update donation state to COMPLETED
        self._donations.update_status(dispatch.donation_id, DonationStatus.COMPLETED)

        # Volunteer completed shift, increment count and reset status to AVAILABLE
        vol = self._volunteers.get_by_id(dispatch.volunteer_id)
        if vol:
            vol.status = VolunteerStatus.AVAILABLE
            vol.weekly_shifts_completed += 1
            self._volunteers.save(vol)

        shifts = vol.weekly_shifts_completed if vol else 0
        logger.info(
            "Delivery confirmed for dispatch %s: %s lbs rescued, %s completed shift (%d this week).",
            dispatch_id, dispatch.weight_rescued_lbs,
            dispatch.volunteer_name, shifts,
        )

        return dispatch

    def list_dispatches(self) -> List[Dispatch]:
        return self._dispatches.list_dispatches()

    # --- Volunteer Use Case Implementation ---
    def list_volunteers(self) -> List[Volunteer]:
        return self._volunteers.list_all()

    def get_volunteer(self, volunteer_id: str) -> Optional[Volunteer]:
        return self._volunteers.get_by_id(volunteer_id)

    def toggle_availability(self, volunteer_id: str, is_available: bool) -> Volunteer:
        status = VolunteerStatus.AVAILABLE if is_available else VolunteerStatus.OFF_DUTY
        updated = self._volunteers.update_status(volunteer_id, status)
        if not updated:
            raise VolunteerNotFoundError(volunteer_id)
        logger.info("Volunteer %s (%s) set to %s.",
                    updated.name, volunteer_id, status.value)
        return updated

    def register_volunteer(self, volunteer: Volunteer) -> Volunteer:
        saved = self._volunteers.save(volunteer)
        logger.info("Volunteer registered: %s (%s, %s).",
                    saved.name, saved.id, saved.vehicle_type.value)
        return saved

    # --- System Metrics & Observability ---
    def get_system_stats(self) -> SystemStats:
        all_dispatches = self._dispatches.list_dispatches()
        delivered = [d for d in all_dispatches if d.status == DispatchStatus.DELIVERED]
        total_rescued = sum(d.weight_rescued_lbs for d in delivered)

        # Standard food bank conversion: 1.2 lbs of food per meal
        meals = int(total_rescued / 1.2) if total_rescued > 0 else 0

        # Carbon offset: 2.5 kg CO2e per 1 lb of rescued food
        carbon = round(total_rescued * 2.5, 1)

        available_vols = len(self._volunteers.list_available())
        pending = len(self._dispatches.list_pending_proposals())
        active_disp = len([d for d in all_dispatches if d.status in [DispatchStatus.APPROVED, DispatchStatus.PICKED_UP]])

        return SystemStats(
            total_rescued_lbs=total_rescued,
            meals_provided=meals,
            active_volunteers=available_vols,
            pending_decisions_count=pending,
            active_dispatches_count=active_disp,
            carbon_offset_kg=carbon
        )

    # --- Internal State-Machine Helper ---
    @staticmethod
    def _ensure_proposal_pending(proposal: DispatchProposal) -> None:
        """A proposal may only be decided while it is still PROPOSED."""
        if proposal.status != DispatchStatus.PROPOSED:
            raise InvalidStateTransitionError(
                "proposal", proposal.status.value, "decision"
            )

    # --- Internal Dispatch Execution Helper ---
    def _execute_dispatch(
        self,
        proposal: DispatchProposal,
        donation: DonationAlert,
        volunteer: Volunteer,
        approved_by: str,
        notes: str
    ) -> Dispatch:
        # Mark proposal as approved
        proposal.status = DispatchStatus.APPROVED
        self._dispatches.save_proposal(proposal)

        logger.info(
            "Dispatch approved for %s by %s: volunteer=%s, %s",
            proposal.id, approved_by, volunteer.name, notes,
        )

        # Generate a cryptographically secure 4-digit verification code
        code = f"{secrets.randbelow(10000):04d}"

        # Create Dispatch record
        dispatch = Dispatch(
            proposal_id=proposal.id,
            donation_id=donation.id,
            volunteer_id=volunteer.id,
            volunteer_name=volunteer.name,
            donor_name=donation.donor_name,
            donor_address=f"{donation.donor_address.address}, {donation.donor_address.neighborhood or ''}".strip(", "),
            pickup_verification_code=code,
            status=DispatchStatus.APPROVED,
            approved_by=approved_by,
            weight_rescued_lbs=donation.estimated_weight_lbs,
            notes=notes
        )
        saved_dispatch = self._dispatches.save_dispatch(dispatch)

        # Update volunteer status to DISPATCHED
        self._volunteers.update_status(volunteer.id, VolunteerStatus.DISPATCHED)

        # Update donation status to DISPATCHED
        self._donations.update_status(donation.id, DonationStatus.DISPATCHED)

        # Send multi-channel notifications
        self._notifier.notify_volunteer_dispatch(volunteer, saved_dispatch, donation)
        self._notifier.notify_donor_eta(donation, saved_dispatch, volunteer, eta_minutes=12)

        logger.info(
            "Dispatch %s created: %s -> %s (%s), %d lbs, pickup code issued.",
            saved_dispatch.id, volunteer.name, donation.donor_name,
            donation.donor_address.neighborhood, donation.estimated_weight_lbs,
        )
        logger.debug("Dispatch %s pickup verification code: %s", saved_dispatch.id, code)

        return saved_dispatch
