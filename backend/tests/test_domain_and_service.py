import pytest
from datetime import datetime, timezone, timedelta

from src.domain.models import (
    DonationAlert, FoodCategory, GeoLocation, Volunteer,
    VolunteerStatus, VehicleType, DispatchStatus, DonationStatus
)
from src.adapters.outbound.persistence.in_memory_repo import (
    SharedInMemoryStore, InMemoryVolunteerRepository,
    InMemoryDonationRepository, InMemoryDispatchRepository
)
from src.adapters.outbound.agent.strands_agent_adapter import StrandsAgentAdapter
from src.adapters.outbound.notification.mock_notifier import MockNotificationAdapter
from src.core.services import PantryPulseService
from src.domain.exceptions import IncompatibleVolunteerError

@pytest.fixture
def test_service():
    # Fresh store for testing
    store = SharedInMemoryStore()
    v_repo = InMemoryVolunteerRepository(store)
    d_repo = InMemoryDonationRepository(store)
    disp_repo = InMemoryDispatchRepository(store)
    agent = StrandsAgentAdapter()
    notifier = MockNotificationAdapter()
    return PantryPulseService(v_repo, d_repo, disp_repo, agent, notifier)

def test_system_stats(test_service):
    stats = test_service.get_system_stats()
    assert stats.total_rescued_lbs >= 85
    assert stats.meals_provided >= 70
    assert stats.active_volunteers >= 4

def test_ingest_and_propose(test_service):
    now = datetime.now(timezone.utc)
    alert = DonationAlert(
        donor_name="Pike Place Fish Market",
        donor_contact_name="Hal",
        donor_phone="+1 (206) 555-9000",
        donor_address=GeoLocation(
            latitude=47.6087,
            longitude=-122.3400,
            address="86 Pike St",
            neighborhood="Downtown"
        ),
        food_category=FoodCategory.DAIRY_FROZEN,
        item_description="Fresh salmon fillets and iced seafood chowder",
        estimated_weight_lbs=80,
        box_count=3,
        requires_cold_chain=True,
        is_fragile=False,
        reported_at=now,
        pickup_deadline=now + timedelta(hours=1),
        status=DonationStatus.REPORTED
    )

    proposal = test_service.ingest_donation_alert(alert)
    assert proposal is not None
    assert proposal.status == DispatchStatus.PROPOSED
    assert proposal.primary_candidate is not None
    # Because requires_cold_chain=True, candidate MUST have cooler
    assert proposal.primary_candidate.has_cooler is True

def test_approve_dispatch_and_complete(test_service):
    # Simulate an alert
    proposal = test_service.simulate_random_alert()
    assert proposal.status == DispatchStatus.PROPOSED

    # 1-Click Coordinator Approval
    dispatch = test_service.approve_proposal(proposal.id, approved_by="Coordinator Sarah L.")
    assert dispatch.status == DispatchStatus.APPROVED
    assert dispatch.pickup_verification_code is not None

    # Driver confirms pickup
    picked_up = test_service.confirm_pickup(dispatch.id, verification_code=dispatch.pickup_verification_code)
    assert picked_up.status == DispatchStatus.PICKED_UP

    # Loading dock confirms delivery
    delivered = test_service.confirm_delivery(dispatch.id, final_weight_lbs=dispatch.weight_rescued_lbs)
    assert delivered.status == DispatchStatus.DELIVERED
    assert delivered.delivered_at is not None

def test_pickup_rejects_invalid_verification_code(test_service):
    proposal = test_service.simulate_random_alert()
    dispatch = test_service.approve_proposal(proposal.id)

    with pytest.raises(IncompatibleVolunteerError):
        test_service.confirm_pickup(dispatch.id, verification_code="0000")
