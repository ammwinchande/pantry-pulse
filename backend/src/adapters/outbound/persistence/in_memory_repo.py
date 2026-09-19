from typing import List, Optional, Dict

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
        """Populate the store with the demo dataset (from seed_data)."""
        from src.adapters.outbound.persistence import seed_data
        self.volunteers = {v.id: v for v in seed_data.seed_volunteers()}
        self.donations = {d.id: d for d in seed_data.seed_donations()}
        self.dispatches = {dp.id: dp for dp in seed_data.seed_dispatches()}

    def reset(self) -> None:
        """Clear all data and re-seed. Used by tests for isolation."""
        self.volunteers.clear()
        self.donations.clear()
        self.proposals.clear()
        self.dispatches.clear()
        self._seed_data()


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
