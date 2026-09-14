import os
import uvicorn
from src.adapters.outbound.persistence.in_memory_repo import (
    SharedInMemoryStore,
    InMemoryVolunteerRepository,
    InMemoryDonationRepository,
    InMemoryDispatchRepository
)
from src.adapters.outbound.agent.strands_agent_adapter import StrandsAgentAdapter
from src.adapters.outbound.notification.mock_notifier import MockNotificationAdapter
from src.core.services import PantryPulseService
from src.adapters.inbound.rest.app import create_app

# --- Hexagonal Composition Root ---
store = SharedInMemoryStore()
volunteer_repo = InMemoryVolunteerRepository(store)
donation_repo = InMemoryDonationRepository(store)
dispatch_repo = InMemoryDispatchRepository(store)
agent_adapter = StrandsAgentAdapter()
notifier_adapter = MockNotificationAdapter()

service = PantryPulseService(
    volunteer_repo=volunteer_repo,
    donation_repo=donation_repo,
    dispatch_repo=dispatch_repo,
    agent=agent_adapter,
    notifier=notifier_adapter
)

app = create_app(service, agent_adapter, notifier_adapter)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting PantryPulse Backend on port {port}...")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
