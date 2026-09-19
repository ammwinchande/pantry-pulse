"""
Shared pytest fixtures for the PantryPulse backend.

Builds a fresh FastAPI app per test backed by an isolated in-memory SQLite
database (via the SQLAlchemy repositories + seeder), so business routes
(now JWT-protected) are exercised end-to-end against the real persistence
path.
"""
import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.adapters.outbound.persistence import db
from src.adapters.outbound.persistence import seeder
from src.adapters.outbound.persistence.orm_models import Base
from src.adapters.outbound.persistence.sqlalchemy_repos import (
    SQLAlchemyVolunteerRepository,
    SQLAlchemyDonationRepository,
    SQLAlchemyDispatchRepository,
    SQLAlchemyUserRepository,
)
from src.adapters.outbound.auth.jwt_credential_adapter import JWTCredentialAdapter
from src.adapters.outbound.auth.mailtrap_email_adapter import MailtrapEmailAdapter
from src.adapters.outbound.agent.strands_agent_adapter import StrandsAgentAdapter
from src.adapters.outbound.notification.mock_notifier import MockNotificationAdapter
from src.core.services import PantryPulseService
from src.core.auth_service import AuthService
from src.adapters.inbound.rest.app import create_app

DEMO_EMAIL = "coordinator@pantrypulse.org"
DEMO_PASSWORD = "Coordinator123!"


@pytest.fixture
def app():
    """A fully wired app backed by a fresh, seeded in-memory SQLite DB."""
    # Isolated in-memory DB shared across the (single) connection.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    # Point the persistence module at the test engine for the duration of the test.
    original_engine, original_session = db.engine, db.SessionLocal
    db.engine = test_engine
    db.SessionLocal = TestSession
    try:
        Base.metadata.create_all(bind=test_engine)
        with TestSession() as session:
            seeder.seed(session, credential_port=JWTCredentialAdapter())

        volunteer_repo = SQLAlchemyVolunteerRepository()
        donation_repo = SQLAlchemyDonationRepository()
        dispatch_repo = SQLAlchemyDispatchRepository()
        agent_adapter = StrandsAgentAdapter()
        notifier_adapter = MockNotificationAdapter()

        service = PantryPulseService(
            volunteer_repo=volunteer_repo,
            donation_repo=donation_repo,
            dispatch_repo=dispatch_repo,
            agent=agent_adapter,
            notifier=notifier_adapter,
        )

        credential_port = JWTCredentialAdapter()
        email_adapter = MailtrapEmailAdapter()
        user_repo = SQLAlchemyUserRepository()

        auth_service = AuthService(
            user_repo=user_repo,
            credentials=credential_port,
            email=email_adapter,
        )

        yield create_app(
            service=service,
            agent_adapter=agent_adapter,
            notifier_adapter=notifier_adapter,
            auth_service=auth_service,
            credential_port=credential_port,
            email_adapter=email_adapter,
            user_repo=user_repo,
        )
    finally:
        db.engine = original_engine
        db.SessionLocal = original_session
        test_engine.dispose()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Authorization headers for the seeded demo coordinator."""
    res = client.post(
        "/api/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
