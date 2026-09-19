"""
SQLAlchemy ORM models — the persistence detail behind the repository ports.

These map the hexagonal *domain* models (``src.domain.models``) onto database
tables. Nested value objects (``GeoLocation``, ``CandidateVolunteer``) are
stored as JSON columns so the schema stays flat and portable across SQLite,
PostgreSQL and MySQL.

The domain layer never imports this module; only the outbound adapters do.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class VolunteerORM(Base):
    __tablename__ = "volunteers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(160))
    current_location: Mapped[dict] = mapped_column(JSON)
    vehicle_type: Mapped[str] = mapped_column(String(32))
    cargo_capacity_lbs: Mapped[int] = mapped_column(Integer)
    has_cooler: Mapped[bool] = mapped_column(Boolean, default=False)
    can_lift_heavy: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32))
    weekly_shifts_completed: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=4.9)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class DonationORM(Base):
    __tablename__ = "donations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    donor_name: Mapped[str] = mapped_column(String(160))
    donor_contact_name: Mapped[str] = mapped_column(String(120))
    donor_phone: Mapped[str] = mapped_column(String(40))
    donor_address: Mapped[dict] = mapped_column(JSON)
    food_category: Mapped[str] = mapped_column(String(32))
    item_description: Mapped[str] = mapped_column(Text)
    estimated_weight_lbs: Mapped[int] = mapped_column(Integer)
    box_count: Mapped[int] = mapped_column(Integer)
    requires_cold_chain: Mapped[bool] = mapped_column(Boolean, default=False)
    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    pickup_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32))
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DispatchProposalORM(Base):
    __tablename__ = "dispatch_proposals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    donation_id: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    primary_candidate: Mapped[dict] = mapped_column(JSON)
    alternative_candidate: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tradeoff_summary: Mapped[str] = mapped_column(Text)
    agent_reasoning: Mapped[str] = mapped_column(Text)
    urgency_level: Mapped[str] = mapped_column(String(16), default="HIGH")
    estimated_carbon_saved_kg: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32))


class DispatchORM(Base):
    __tablename__ = "dispatches"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    proposal_id: Mapped[str] = mapped_column(String(64), index=True)
    donation_id: Mapped[str] = mapped_column(String(64), index=True)
    volunteer_id: Mapped[str] = mapped_column(String(64), index=True)
    volunteer_name: Mapped[str] = mapped_column(String(120))
    donor_name: Mapped[str] = mapped_column(String(160))
    donor_address: Mapped[str] = mapped_column(String(255))
    pantry_address: Mapped[str] = mapped_column(String(255))
    pickup_verification_code: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32))
    approved_by: Mapped[str] = mapped_column(String(120))
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    picked_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    weight_rescued_lbs: Mapped[int] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(32))
    organization: Mapped[str] = mapped_column(String(160), default="Downtown Community Pantry")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
