"""
Database seeder — loads demo data idempotently.

Replaces the previously hardcoded demo user in ``main.py`` and the inline seed
in the in-memory store. It is safe to run on every boot: each record is only
inserted if it does not already exist (keyed by the stable demo IDs).

The demo user's password is hashed here via the ``CredentialPort`` so this
module never stores or logs plaintext credentials.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.ports.driven.credential_port import CredentialPort
from src.adapters.outbound.persistence import seed_data
from src.adapters.outbound.persistence import mappers
from src.adapters.outbound.persistence.orm_models import (
    VolunteerORM, DonationORM, DispatchORM, UserORM,
)

logger = logging.getLogger("PantryPulseSeeder")


def seed(session: Session, credential_port: Optional[CredentialPort] = None) -> None:
    """Insert demo data if not already present. Idempotent."""
    # Volunteers
    existing_vol = set(session.execute(select(VolunteerORM.id)).scalars())
    added_vol = 0
    for v in seed_data.seed_volunteers():
        if v.id not in existing_vol:
            session.add(mappers.volunteer_to_orm(v))
            added_vol += 1

    # Donations
    existing_don = set(session.execute(select(DonationORM.id)).scalars())
    added_don = 0
    for d in seed_data.seed_donations():
        if d.id not in existing_don:
            session.add(mappers.donation_to_orm(d))
            added_don += 1

    # Dispatches
    existing_disp = set(session.execute(select(DispatchORM.id)).scalars())
    added_disp = 0
    for dp in seed_data.seed_dispatches():
        if dp.id not in existing_disp:
            session.add(mappers.dispatch_to_orm(dp))
            added_disp += 1

    # Demo user (hashed password)
    demo = seed_data.DEMO_USER
    existing_user = session.execute(
        select(UserORM).where(UserORM.id == demo["id"])
    ).scalar_one_or_none()
    added_user = 0
    if existing_user is None:
        password_hash = (
            credential_port.hash_password(demo["password"])
            if credential_port is not None else None
        )
        session.add(UserORM(
            id=demo["id"], name=demo["name"], email=demo["email"],
            role=demo["role"], organization=demo["organization"],
            is_active=True, email_verified_at=None,
            password_hash=password_hash,
            created_at=datetime.now(timezone.utc),
        ))
        added_user = 1

    session.commit()

    if added_vol or added_don or added_disp or added_user:
        logger.info(
            "Seeded demo data: %d volunteer(s), %d donation(s), %d dispatch(es), %d user(s).",
            added_vol, added_don, added_disp, added_user,
        )
    else:
        logger.info("Database already seeded — nothing to insert.")


def reset(session: Session) -> None:
    """Wipe all seeded tables (used by tests for isolation)."""
    for model in (DispatchORM, DonationORM, VolunteerORM, UserORM):
        session.execute(model.__table__.delete())
    session.commit()
    logger.info("Database reset — all seeded tables cleared.")
