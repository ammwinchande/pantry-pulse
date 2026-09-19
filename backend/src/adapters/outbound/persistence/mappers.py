"""
Bidirectional mappers between domain models and ORM models.

Shared by the seeder and the SQLAlchemy repositories so the conversion logic
lives in exactly one place. Domain models use enums + nested value objects;
ORM models store plain strings + JSON columns.
"""
from typing import Optional

from src.domain.models import (
    Volunteer, VolunteerStatus, VehicleType, GeoLocation,
    DonationAlert, DonationStatus, FoodCategory,
    DispatchProposal, Dispatch, DispatchStatus, CandidateVolunteer,
    User, UserRole,
)
from src.adapters.outbound.persistence.orm_models import (
    VolunteerORM, DonationORM, DispatchProposalORM, DispatchORM, UserORM,
)


# --- Volunteer ---
def volunteer_to_orm(v: Volunteer) -> VolunteerORM:
    return VolunteerORM(
        id=v.id, name=v.name, phone=v.phone, email=v.email,
        current_location=v.current_location.model_dump(),
        vehicle_type=v.vehicle_type.value,
        cargo_capacity_lbs=v.cargo_capacity_lbs,
        has_cooler=v.has_cooler, can_lift_heavy=v.can_lift_heavy,
        status=v.status.value,
        weekly_shifts_completed=v.weekly_shifts_completed,
        rating=v.rating, avatar_url=v.avatar_url,
    )


def volunteer_from_orm(r: VolunteerORM) -> Volunteer:
    return Volunteer(
        id=r.id, name=r.name, phone=r.phone, email=r.email,
        current_location=GeoLocation(**r.current_location),
        vehicle_type=VehicleType(r.vehicle_type),
        cargo_capacity_lbs=r.cargo_capacity_lbs,
        has_cooler=r.has_cooler, can_lift_heavy=r.can_lift_heavy,
        status=VolunteerStatus(r.status),
        weekly_shifts_completed=r.weekly_shifts_completed,
        rating=r.rating, avatar_url=r.avatar_url,
    )


# --- Donation ---
def donation_to_orm(d: DonationAlert) -> DonationORM:
    return DonationORM(
        id=d.id, donor_name=d.donor_name,
        donor_contact_name=d.donor_contact_name, donor_phone=d.donor_phone,
        donor_address=d.donor_address.model_dump(),
        food_category=d.food_category.value,
        item_description=d.item_description,
        estimated_weight_lbs=d.estimated_weight_lbs, box_count=d.box_count,
        requires_cold_chain=d.requires_cold_chain, is_fragile=d.is_fragile,
        reported_at=d.reported_at, pickup_deadline=d.pickup_deadline,
        status=d.status.value, special_instructions=d.special_instructions,
    )


def donation_from_orm(r: DonationORM) -> DonationAlert:
    return DonationAlert(
        id=r.id, donor_name=r.donor_name,
        donor_contact_name=r.donor_contact_name, donor_phone=r.donor_phone,
        donor_address=GeoLocation(**r.donor_address),
        food_category=FoodCategory(r.food_category),
        item_description=r.item_description,
        estimated_weight_lbs=r.estimated_weight_lbs, box_count=r.box_count,
        requires_cold_chain=r.requires_cold_chain, is_fragile=r.is_fragile,
        reported_at=r.reported_at, pickup_deadline=r.pickup_deadline,
        status=DonationStatus(r.status), special_instructions=r.special_instructions,
    )


# --- Dispatch proposal ---
def proposal_to_orm(p: DispatchProposal) -> DispatchProposalORM:
    return DispatchProposalORM(
        id=p.id, donation_id=p.donation_id, created_at=p.created_at,
        primary_candidate=p.primary_candidate.model_dump(),
        alternative_candidate=(
            p.alternative_candidate.model_dump() if p.alternative_candidate else None
        ),
        tradeoff_summary=p.tradeoff_summary, agent_reasoning=p.agent_reasoning,
        urgency_level=p.urgency_level,
        estimated_carbon_saved_kg=p.estimated_carbon_saved_kg,
        status=p.status.value,
    )


def proposal_from_orm(r: DispatchProposalORM) -> DispatchProposal:
    return DispatchProposal(
        id=r.id, donation_id=r.donation_id, created_at=r.created_at,
        primary_candidate=CandidateVolunteer(**r.primary_candidate),
        alternative_candidate=(
            CandidateVolunteer(**r.alternative_candidate) if r.alternative_candidate else None
        ),
        tradeoff_summary=r.tradeoff_summary, agent_reasoning=r.agent_reasoning,
        urgency_level=r.urgency_level,
        estimated_carbon_saved_kg=r.estimated_carbon_saved_kg,
        status=DispatchStatus(r.status),
    )


# --- Dispatch ---
def dispatch_to_orm(dp: Dispatch) -> DispatchORM:
    return DispatchORM(
        id=dp.id, proposal_id=dp.proposal_id, donation_id=dp.donation_id,
        volunteer_id=dp.volunteer_id, volunteer_name=dp.volunteer_name,
        donor_name=dp.donor_name, donor_address=dp.donor_address,
        pantry_address=dp.pantry_address,
        pickup_verification_code=dp.pickup_verification_code,
        status=dp.status.value, approved_by=dp.approved_by,
        approved_at=dp.approved_at, picked_up_at=dp.picked_up_at,
        delivered_at=dp.delivered_at, weight_rescued_lbs=dp.weight_rescued_lbs,
        notes=dp.notes,
    )


def dispatch_from_orm(r: DispatchORM) -> Dispatch:
    return Dispatch(
        id=r.id, proposal_id=r.proposal_id, donation_id=r.donation_id,
        volunteer_id=r.volunteer_id, volunteer_name=r.volunteer_name,
        donor_name=r.donor_name, donor_address=r.donor_address,
        pantry_address=r.pantry_address,
        pickup_verification_code=r.pickup_verification_code,
        status=DispatchStatus(r.status), approved_by=r.approved_by,
        approved_at=r.approved_at, picked_up_at=r.picked_up_at,
        delivered_at=r.delivered_at, weight_rescued_lbs=r.weight_rescued_lbs,
        notes=r.notes,
    )


# --- User ---
def user_to_orm(u: User) -> UserORM:
    return UserORM(
        id=u.id, name=u.name, email=u.email, role=u.role.value,
        organization=u.organization, is_active=u.is_active,
        email_verified_at=u.email_verified_at, password_hash=u.password_hash,
        created_at=u.created_at,
    )


def user_from_orm(r: UserORM) -> User:
    return User(
        id=r.id, name=r.name, email=r.email, role=UserRole(r.role),
        organization=r.organization, is_active=r.is_active,
        email_verified_at=r.email_verified_at, password_hash=r.password_hash,
        created_at=r.created_at,
    )
