import os
import uvicorn
from src.config import settings
from src.adapters.outbound.persistence.db import init_db, get_session
from src.adapters.outbound.persistence import seeder
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

# --- Hexagonal Composition Root ---
# Datastore: SQLite by default; set DATABASE_URL to switch to Postgres/MySQL.
init_db()

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
    notifier=notifier_adapter
)

# --- Auth composition ---
credential_port = JWTCredentialAdapter()
email_adapter = MailtrapEmailAdapter()
user_repo = SQLAlchemyUserRepository()

# Seed demo data idempotently (safe on every boot).
if settings.seed_on_startup:
    with get_session() as session:
        seeder.seed(session, credential_port=credential_port)

auth_service = AuthService(
    user_repo=user_repo,
    credentials=credential_port,
    email=email_adapter,
)

app = create_app(
    service=service,
    agent_adapter=agent_adapter,
    notifier_adapter=notifier_adapter,
    auth_service=auth_service,
    credential_port=credential_port,
    email_adapter=email_adapter,
    user_repo=user_repo,
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting PantryPulse Backend on port {port}...")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
