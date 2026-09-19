"""
SQLAlchemy repository adapters — the production datastore.

Each repository implements one of the driven ports and talks to the database
through a short-lived session (``get_session``), so the adapters are stateless
and safe to share across FastAPI's thread pool.

These are the only modules in the codebase that import SQLAlchemy. Swapping
the datastore (SQLite -> Postgres/MySQL) is a ``DATABASE_URL`` change, not a
code change.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.models import (
    Volunteer, VolunteerStatus,
    DonationAlert, DonationStatus,
    DispatchProposal, Dispatch, DispatchStatus,
    User, UserRole,
)
from src.ports.driven.volunteer_repo_port import VolunteerRepositoryPort
from src.ports.driven.donation_repo_port import DonationRepositoryPort
from src.ports.driven.dispatch_repo_port import DispatchRepositoryPort
from src.ports.driven.user_repo_port import UserRepositoryPort
from src.adapters.outbound.persistence.db import get_session
from src.adapters.outbound.persistence import mappers
from src.adapters.outbound.persistence.orm_models import (
    VolunteerORM, DonationORM, DispatchProposalORM, DispatchORM, UserORM,
)


class SQLAlchemyVolunteerRepository(VolunteerRepositoryPort):
    def list_all(self) -> List[Volunteer]:
        with get_session() as session:
            rows = session.execute(select(VolunteerORM)).scalars().all()
            return [mappers.volunteer_from_orm(r) for r in rows]

    def get_by_id(self, volunteer_id: str) -> Optional[Volunteer]:
        with get_session() as session:
            row = session.get(VolunteerORM, volunteer_id)
            return mappers.volunteer_from_orm(row) if row else None

    def list_available(self) -> List[Volunteer]:
        with get_session() as session:
            rows = session.execute(
                select(VolunteerORM).where(
                    VolunteerORM.status == VolunteerStatus.AVAILABLE.value
                )
            ).scalars().all()
            return [mappers.volunteer_from_orm(r) for r in rows]

    def save(self, volunteer: Volunteer) -> Volunteer:
        with get_session() as session:
            row = session.get(VolunteerORM, volunteer.id)
            if row is None:
                row = mappers.volunteer_to_orm(volunteer)
                session.add(row)
            else:
                session.merge(mappers.volunteer_to_orm(volunteer))
            session.commit()
            return volunteer

    def update_status(self, volunteer_id: str, status: VolunteerStatus) -> Optional[Volunteer]:
        with get_session() as session:
            row = session.get(VolunteerORM, volunteer_id)
            if row is None:
                return None
            row.status = status.value
            session.commit()
            return mappers.volunteer_from_orm(row)


class SQLAlchemyDonationRepository(DonationRepositoryPort):
    def list_all(self) -> List[DonationAlert]:
        with get_session() as session:
            rows = session.execute(select(DonationORM)).scalars().all()
            # Newest first (matches the in-memory adapter's ordering).
            return [mappers.donation_from_orm(r) for r in reversed(rows)]

    def get_by_id(self, donation_id: str) -> Optional[DonationAlert]:
        with get_session() as session:
            row = session.get(DonationORM, donation_id)
            return mappers.donation_from_orm(row) if row else None

    def save(self, donation: DonationAlert) -> DonationAlert:
        with get_session() as session:
            row = session.get(DonationORM, donation.id)
            if row is None:
                session.add(mappers.donation_to_orm(donation))
            else:
                session.merge(mappers.donation_to_orm(donation))
            session.commit()
            return donation

    def update_status(self, donation_id: str, status: DonationStatus) -> Optional[DonationAlert]:
        with get_session() as session:
            row = session.get(DonationORM, donation_id)
            if row is None:
                return None
            row.status = status.value
            session.commit()
            return mappers.donation_from_orm(row)


class SQLAlchemyDispatchRepository(DispatchRepositoryPort):
    def save_proposal(self, proposal: DispatchProposal) -> DispatchProposal:
        with get_session() as session:
            row = session.get(DispatchProposalORM, proposal.id)
            if row is None:
                session.add(mappers.proposal_to_orm(proposal))
            else:
                session.merge(mappers.proposal_to_orm(proposal))
            session.commit()
            return proposal

    def get_proposal_by_id(self, proposal_id: str) -> Optional[DispatchProposal]:
        with get_session() as session:
            row = session.get(DispatchProposalORM, proposal_id)
            return mappers.proposal_from_orm(row) if row else None

    def list_pending_proposals(self) -> List[DispatchProposal]:
        with get_session() as session:
            rows = session.execute(
                select(DispatchProposalORM).where(
                    DispatchProposalORM.status == DispatchStatus.PROPOSED.value
                )
            ).scalars().all()
            return [mappers.proposal_from_orm(r) for r in rows]

    def save_dispatch(self, dispatch: Dispatch) -> Dispatch:
        with get_session() as session:
            row = session.get(DispatchORM, dispatch.id)
            if row is None:
                session.add(mappers.dispatch_to_orm(dispatch))
            else:
                session.merge(mappers.dispatch_to_orm(dispatch))
            session.commit()
            return dispatch

    def list_dispatches(self) -> List[Dispatch]:
        with get_session() as session:
            rows = session.execute(select(DispatchORM)).scalars().all()
            # Newest first (matches the in-memory adapter's ordering).
            return [mappers.dispatch_from_orm(r) for r in reversed(rows)]

    def get_dispatch_by_id(self, dispatch_id: str) -> Optional[Dispatch]:
        with get_session() as session:
            row = session.get(DispatchORM, dispatch_id)
            return mappers.dispatch_from_orm(row) if row else None

    def update_dispatch_status(self, dispatch_id: str, status: DispatchStatus) -> Optional[Dispatch]:
        with get_session() as session:
            row = session.get(DispatchORM, dispatch_id)
            if row is None:
                return None
            row.status = status.value
            session.commit()
            return mappers.dispatch_from_orm(row)


class SQLAlchemyUserRepository(UserRepositoryPort):
    def save(self, user: User) -> User:
        with get_session() as session:
            row = session.get(UserORM, user.id)
            if row is None:
                session.add(mappers.user_to_orm(user))
            else:
                session.merge(mappers.user_to_orm(user))
            session.commit()
            return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        with get_session() as session:
            row = session.get(UserORM, user_id)
            return mappers.user_from_orm(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        with get_session() as session:
            row = session.execute(
                select(UserORM).where(UserORM.email == email)
            ).scalar_one_or_none()
            return mappers.user_from_orm(row) if row else None

    def list_all(self) -> List[User]:
        with get_session() as session:
            rows = session.execute(select(UserORM)).scalars().all()
            return [mappers.user_from_orm(r) for r in rows]

    def list_by_role(self, role: UserRole) -> List[User]:
        with get_session() as session:
            rows = session.execute(
                select(UserORM).where(UserORM.role == role.value)
            ).scalars().all()
            return [mappers.user_from_orm(r) for r in rows]
