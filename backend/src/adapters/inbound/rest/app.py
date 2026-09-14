import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.services import PantryPulseService
from src.ports.driven.agent_port import AgentPort
from src.ports.driven.notification_port import NotificationPort
from src.adapters.inbound.rest.routes import create_router

def create_app(
    service: PantryPulseService,
    agent_adapter: AgentPort,
    notifier_adapter: NotificationPort
) -> FastAPI:
    app = FastAPI(
        title="PantryPulse API",
        description="Autonomous Food Rescue & Volunteer Dispatch Agent using AWS Strands Agents SDK",
        version="1.0.0"
    )

    # Enable CORS for React frontend development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    router = create_router(service, agent_adapter, notifier_adapter)
    app.include_router(router)

    @app.get("/api/health")
    def api_health():
        return {
            "status": "healthy",
            "service": "PantryPulse Backend",
            "architecture": "Ports and Adapters (Hexagonal)",
            "agent_sdk": "AWS Strands Agents SDK",
            "hackathon_track": "Good Neighbor Agents"
        }

    # Mount static frontend if available (for single-container production deployment)
    candidate_paths = [
        os.environ.get("STATIC_DIR"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../frontend/dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../frontend/dist")),
        "/app/frontend/dist",
        "/app/static"
    ]
    static_path = next((p for p in candidate_paths if p and os.path.isdir(p)), None)

    if static_path:
        app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
    else:
        @app.get("/")
        def health_check():
            return {
                "status": "healthy",
                "service": "PantryPulse Backend",
                "architecture": "Ports and Adapters (Hexagonal)",
                "agent_sdk": "AWS Strands Agents SDK",
                "hackathon_track": "Good Neighbor Agents"
            }

    return app
