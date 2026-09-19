"""
Database seeder — loads demo data idempotently.

Replaces the previously hardcoded demo user in ``main.py`` and the inline seed
in the in-memory store. It is safe to run on every boot: each record is only
inserted if it does not already exist (keyed by the stable demo IDs).

The demo user's password is hashed here via the ``CredentialPort`` so this
module never stores or logs plaintext credentials.
"""
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


def seed(session: Session, credential_port: Optional[CredentialPort] = None) -> None:
    """Insert demo data if not already present. Idempotent."""
    # Volunteers
    existing_vol = set(session.execute(select(VolunteerORM.id)).scalars())
    for v in seed_data.seed_volunteers():
        if v.id not in existing_vol:
            session.add(mappers.volunteer_to_orm(v))

    # Donations
    existing_don = set(session.execute(select(DonationORM.id)).scalars())
    for d in seed_data.seed_donations():
        if d.id not in existing_don:
            session.add(mappers.donation_to_orm(d))

    # Dispatches
    existing_disp = set(session.execute(select(DispatchORM.id)).scalars())
    for dp in seed_data.seed_dispatches():
        if dp.id not in existing_disp:
            session.add(mappers.dispatch_to_orm(dp))

    # Demo user (hashed password)
    demo = seed_data.DEMO_USER
    existing_user = session.execute(
        select(UserORM).where(UserORM.id == demo["id"])
    ).scalar_one_or_none()
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

    session.commit()


def reset(session: Session) -> None:
    """Wipe all seeded tables (used by tests for isolation)."""
    for model in (DispatchORM, DonationORM, VolunteerORM, UserORM):
        session.execute(model.__table__.delete())
    session.commit()
