"""
Demo / seed data — the single source of truth for initial application data.

Used by both the in-memory repositories (fast unit tests) and the database
seeder (``seeder.py``) so the two persistence backends always start from the
same fixtures.

The demo *user* is described here as plain data (no password hash) so this
module stays free of any credential-port dependency; hashing happens in the
seeder.
"""
from datetime import datetime, timedelta, timezone
from typing import List

from src.domain.models import (
    Volunteer, VolunteerStatus, VehicleType, GeoLocation,
    DonationAlert, DonationStatus, FoodCategory,
    Dispatch, DispatchStatus,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def seed_volunteers() -> List[Volunteer]:
    return [
        Volunteer(
            id="vol-01",
            name="Sarah Lin",
            phone="+1 (206) 555-0142",
            email="sarah.lin@example.com",
            current_location=GeoLocation(
                latitude=47.6101, longitude=-122.3421,
                address="2100 2nd Ave", neighborhood="Belltown"),
            vehicle_type=VehicleType.HATCHBACK_SUV,
            cargo_capacity_lbs=300,
            has_cooler=True, can_lift_heavy=True,
            status=VolunteerStatus.AVAILABLE,
            weekly_shifts_completed=1, rating=4.95,
            avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
        ),
        Volunteer(
            id="vol-02",
            name="Marcus Vance",
            phone="+1 (206) 555-0198",
            email="marcus.v@example.com",
            current_location=GeoLocation(
                latitude=47.6205, longitude=-122.3493,
                address="400 Broad St", neighborhood="Seattle Center"),
            vehicle_type=VehicleType.VAN_TRUCK,
            cargo_capacity_lbs=1200,
            has_cooler=True, can_lift_heavy=True,
            status=VolunteerStatus.AVAILABLE,
            weekly_shifts_completed=3, rating=4.88,
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
        ),
        Volunteer(
            id="vol-03",
            name="Elena Rostova",
            phone="+1 (206) 555-0164",
            email="elena.r@example.com",
            current_location=GeoLocation(
                latitude=47.6152, longitude=-122.3210,
                address="1115 E Pike St", neighborhood="Capitol Hill"),
            vehicle_type=VehicleType.SEDAN,
            cargo_capacity_lbs=150,
            has_cooler=False, can_lift_heavy=False,
            status=VolunteerStatus.AVAILABLE,
            weekly_shifts_completed=0, rating=4.92,
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
        ),
        Volunteer(
            id="vol-04",
            name="Jamal Washington",
            phone="+1 (206) 555-0177",
            email="jamal.w@example.com",
            current_location=GeoLocation(
                latitude=47.6020, longitude=-122.3310,
                address="500 S Jackson St", neighborhood="Pioneer Square"),
            vehicle_type=VehicleType.HATCHBACK_SUV,
            cargo_capacity_lbs=350,
            has_cooler=False, can_lift_heavy=True,
            status=VolunteerStatus.AVAILABLE,
            weekly_shifts_completed=2, rating=4.85,
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
        ),
        Volunteer(
            id="vol-05",
            name="Priya Patel",
            phone="+1 (206) 555-0123",
            email="priya.p@example.com",
            current_location=GeoLocation(
                latitude=47.6250, longitude=-122.3350,
                address="900 Mercer St", neighborhood="South Lake Union"),
            vehicle_type=VehicleType.BICYCLE_CARGO,
            cargo_capacity_lbs=50,
            has_cooler=False, can_lift_heavy=False,
            status=VolunteerStatus.AVAILABLE,
            weekly_shifts_completed=0, rating=5.0,
            avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150",
        ),
    ]


def seed_donations() -> List[DonationAlert]:
    now = _now()
    return [
        DonationAlert(
            id="don-seed-01",
            donor_name="Grand Central Bakery",
            donor_contact_name="Claire Chef",
            donor_phone="+1 (206) 555-8812",
            donor_address=GeoLocation(
                latitude=47.6015, longitude=-122.3320,
                address="214 1st Ave S", neighborhood="Pioneer Square"),
            food_category=FoodCategory.BAKERY_DRY,
            item_description="Surplus sourdough loaves, croissants, and baguettes",
            estimated_weight_lbs=85,
            box_count=6,
            requires_cold_chain=False, is_fragile=False,
            reported_at=now - timedelta(hours=3),
            pickup_deadline=now - timedelta(hours=1),
            status=DonationStatus.COMPLETED,
        ),
    ]


def seed_dispatches() -> List[Dispatch]:
    now = _now()
    return [
        Dispatch(
            id="disp-seed-01",
            proposal_id="prop-seed-01",
            donation_id="don-seed-01",
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
            notes="Freshly baked morning surplus. Delivered straight to food pantry storage.",
        ),
    ]


# --- Demo user (plain data; password is hashed by the seeder) ---
DEMO_USER = {
    "id": "user-demo-coordinator",
    "name": "Coordinator Sarah L.",
    "email": "coordinator@pantrypulse.org",
    "role": "COORDINATOR",
    "organization": "Downtown Community Pantry",
    "password": "Coordinator123!",
}
