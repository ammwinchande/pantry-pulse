from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta

from src.domain.models import (
    Volunteer, VolunteerStatus, VehicleType, GeoLocation,
    DonationAlert, DonationStatus, FoodCategory,
    DispatchProposal, Dispatch, DispatchStatus
)
from src.ports.driven.volunteer_repo_port import VolunteerRepositoryPort
from src.ports.driven.donation_repo_port import DonationRepositoryPort
from src.ports.driven.dispatch_repo_port import DispatchRepositoryPort

class SharedInMemoryStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedInMemoryStore, cls).__new__(cls)
            cls._instance.volunteers: Dict[str, Volunteer] = {}
            cls._instance.donations: Dict[str, DonationAlert] = {}
            cls._instance.proposals: Dict[str, DispatchProposal] = {}
            cls._instance.dispatches: Dict[str, Dispatch] = {}
            cls._instance._seed_data()
        return cls._instance

    def _seed_data(self):
        volunteers_seed = [
            Volunteer(
                id="vol-01",
                name="Sarah Lin",
                phone="+1 (206) 555-0142",
                email="sarah.lin@example.com",
                current_location=GeoLocation(
                    latitude=47.6101,
                    longitude=-122.3421,
                    address="2100 2nd Ave",
                    neighborhood="Belltown"
                ),
                vehicle_type=VehicleType.HATCHBACK_SUV,
                cargo_capacity_lbs=300,
                has_cooler=True,
                can_lift_heavy=True,
                status=VolunteerStatus.AVAILABLE,
                weekly_shifts_completed=1,
                rating=4.95,
                avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
            ),
            Volunteer(
                id="vol-02",
                name="Marcus Vance",
                phone="+1 (206) 555-0198",
                email="marcus.v@example.com",
                current_location=GeoLocation(
                    latitude=47.6205,
                    longitude=-122.3493,
                    address="400 Broad St",
                    neighborhood="Seattle Center"
                ),
                vehicle_type=VehicleType.VAN_TRUCK,
                cargo_capacity_lbs=1200,
                has_cooler=True,
                can_lift_heavy=True,
                status=VolunteerStatus.AVAILABLE,
                weekly_shifts_completed=3,
                rating=4.88,
                avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
            ),
            Volunteer(
                id="vol-03",
                name="Elena Rostova",
                phone="+1 (206) 555-0164",
                email="elena.r@example.com",
                current_location=GeoLocation(
                    latitude=47.6152,
                    longitude=-122.3210,
                    address="1115 E Pike St",
                    neighborhood="Capitol Hill"
                ),
                vehicle_type=VehicleType.SEDAN,
                cargo_capacity_lbs=150,
                has_cooler=False,
                can_lift_heavy=False,
                status=VolunteerStatus.AVAILABLE,
                weekly_shifts_completed=0,
                rating=4.92,
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
            ),
            Volunteer(
                id="vol-04",
                name="Jamal Washington",
                phone="+1 (206) 555-0177",
                email="jamal.w@example.com",
                current_location=GeoLocation(
                    latitude=47.6020,
                    longitude=-122.3310,
                    address="500 S Jackson St",
                    neighborhood="Pioneer Square"
                ),
                vehicle_type=VehicleType.HATCHBACK_SUV,
                cargo_capacity_lbs=350,
                has_cooler=False,
                can_lift_heavy=True,
                status=VolunteerStatus.AVAILABLE,
                weekly_shifts_completed=2,
                rating=4.85,
                avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"
            ),
            Volunteer(
                id="vol-05",
                name="Priya Patel",
                phone="+1 (206) 555-0123",
                email="priya.p@example.com",
                current_location=GeoLocation(
                    latitude=47.6250,
                    longitude=-122.3350,
                    address="900 Mercer St",
                    neighborhood="South Lake Union"
                ),
                vehicle_type=VehicleType.BICYCLE_CARGO,
                cargo_capacity_lbs=50,
                has_cooler=False,
                can_lift_heavy=False,
                status=VolunteerStatus.AVAILABLE,
                weekly_shifts_completed=0,
                rating=5.0,
                avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150"
            )
        ]
        for v in volunteers_seed:
            self.volunteers[v.id] = v

        now = datetime.now(timezone.utc)
        completed_donation = DonationAlert(
            id="don-seed-01",
            donor_name="Grand Central Bakery",
            donor_contact_name="Claire Chef",
            donor_phone="+1 (206) 555-8812",
            donor_address=GeoLocation(
                latitude=47.6015,
                longitude=-122.3320,
                address="214 1st Ave S",
                neighborhood="Pioneer Square"
            ),
            food_category=FoodCategory.BAKERY_DRY,
            item_description="Surplus sourdough loaves, croissants, and baguettes",
            estimated_weight_lbs=85,
            box_count=6,
            requires_cold_chain=False,
            is_fragile=False,
            reported_at=now - timedelta(hours=3),
            pickup_deadline=now - timedelta(hours=1),
            status=DonationStatus.COMPLETED
        )
        self.donations[completed_donation.id] = completed_donation

        completed_dispatch = Dispatch(
            id="disp-seed-01",
            proposal_id="prop-seed-01",
            donation_id=completed_donation.id,
            volunteer_id="vol-01",
            volunteer_name="Sarah Lin",
            donor_name="Grand Central Bakery",
            donor_address="214 1st Ave S, Pioneer Square",
            pickup_verification_code="3914",
            status=DispatchStatus.DELIVERED,
            approved_by="Coordinator Sarah L.",
            approved_at=now - timedelta(hours=2, minutes=45),
            picked_up_at=now - timedelta(hours=2, minutes=15),
            delivered_at=now - timedelta(hours=1, minutes=40),
            weight_rescued_lbs=85,
            notes="Freshly baked morning surplus. Delivered straight to food pantry storage."
        )
        self.dispatches[completed_dispatch.id] = completed_dispatch


class InMemoryVolunteerRepository(VolunteerRepositoryPort):
    def __init__(self, store: Optional[SharedInMemoryStore] = None):
        self._store = store or SharedInMemoryStore()

    def list_all(self) -> List[Volunteer]:
        return list(self._store.volunteers.values())

    def get_by_id(self, volunteer_id: str) -> Optional[Volunteer]:
        return self._store.volunteers.get(volunteer_id)

    def list_available(self) -> List[Volunteer]:
        return [v for v in self._store.volunteers.values() if v.status == VolunteerStatus.AVAILABLE]

    def save(self, volunteer: Volunteer) -> Volunteer:
        self._store.volunteers[volunteer.id] = volunteer
        return volunteer

    def update_status(self, volunteer_id: str, status: VolunteerStatus) -> Optional[Volunteer]:
        vol = self._store.volunteers.get(volunteer_id)
        if vol:
            vol.status = status
            return vol
        return None


class InMemoryDonationRepository(DonationRepositoryPort):
    def __init__(self, store: Optional[SharedInMemoryStore] = None):
        self._store = store or SharedInMemoryStore()

    def list_all(self) -> List[DonationAlert]:
        return list(reversed(list(self._store.donations.values())))

    def get_by_id(self, donation_id: str) -> Optional[DonationAlert]:
        return self._store.donations.get(donation_id)

    def save(self, donation: DonationAlert) -> DonationAlert:
        self._store.donations[donation.id] = donation
        return donation

    def update_status(self, donation_id: str, status: DonationStatus) -> Optional[DonationAlert]:
        don = self._store.donations.get(donation_id)
        if don:
            don.status = status
            return don
        return None


class InMemoryDispatchRepository(DispatchRepositoryPort):
    def __init__(self, store: Optional[SharedInMemoryStore] = None):
        self._store = store or SharedInMemoryStore()

    def save_proposal(self, proposal: DispatchProposal) -> DispatchProposal:
        self._store.proposals[proposal.id] = proposal
        return proposal

    def get_proposal_by_id(self, proposal_id: str) -> Optional[DispatchProposal]:
        return self._store.proposals.get(proposal_id)

    def list_pending_proposals(self) -> List[DispatchProposal]:
        return [p for p in self._store.proposals.values() if p.status == DispatchStatus.PROPOSED]

    def save_dispatch(self, dispatch: Dispatch) -> Dispatch:
        self._store.dispatches[dispatch.id] = dispatch
        return dispatch

    def list_dispatches(self) -> List[Dispatch]:
        return list(reversed(list(self._store.dispatches.values())))

    def get_dispatch_by_id(self, dispatch_id: str) -> Optional[Dispatch]:
        return self._store.dispatches.get(dispatch_id)

    def update_dispatch_status(self, dispatch_id: str, status: DispatchStatus) -> Optional[Dispatch]:
        disp = self._store.dispatches.get(dispatch_id)
        if disp:
            disp.status = status
            return disp
        return None
