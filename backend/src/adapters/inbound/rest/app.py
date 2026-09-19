import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from src.config import settings
from src.core.services import PantryPulseService
from src.core.auth_service import AuthService
from src.ports.driven.agent_port import AgentPort
from src.ports.driven.notification_port import NotificationPort
from src.ports.driven.credential_port import CredentialPort
from src.ports.driven.email_port import EmailPort
from src.ports.driven.user_repo_port import UserRepositoryPort
from src.adapters.inbound.rest.routes import create_router
from src.adapters.inbound.rest.auth_routes import create_auth_router
from src.domain.exceptions import (
    DomainException,
    DonationNotFoundError,
    VolunteerNotFoundError,
    ProposalNotFoundError,
    DispatchNotFoundError,
    UserNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidStateTransitionError,
    IncompatibleVolunteerError,
)


def _register_domain_exception_handlers(app: FastAPI) -> None:
    """Map domain exceptions to appropriate HTTP status codes.

    Keeping this in the inbound REST adapter preserves the hexagonal boundary:
    the domain layer raises pure domain errors, and only the adapter decides
    how they surface over HTTP.
    """
    not_found = [
        DonationNotFoundError,
        VolunteerNotFoundError,
        ProposalNotFoundError,
        DispatchNotFoundError,
        UserNotFoundError,
    ]

    async def _not_found_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    async def _conflict_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    async def _domain_handler(request: Request, exc: DomainException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    for exc_class in not_found:
        app.add_exception_handler(exc_class, _not_found_handler)

    app.add_exception_handler(EmailAlreadyRegisteredError, _conflict_handler)
    app.add_exception_handler(InvalidStateTransitionError, _conflict_handler)
    app.add_exception_handler(IncompatibleVolunteerError, _conflict_handler)
    app.add_exception_handler(DomainException, _domain_handler)

def create_app(
    service: PantryPulseService,
    agent_adapter: AgentPort,
    notifier_adapter: NotificationPort,
    auth_service: AuthService,
    credential_port: CredentialPort,
    email_adapter: EmailPort,
    user_repo: UserRepositoryPort,
) -> FastAPI:
    app = FastAPI(
        title="PantryPulse API",
        description="Autonomous Food Rescue & Volunteer Dispatch Agent using AWS Strands Agents SDK",
        version="1.0.0"
    )

    # Expose ports on app.state for the auth dependency (get_current_user).
    app.state.auth_service = auth_service
    app.state.credential_port = credential_port
    app.state.email_adapter = email_adapter
    app.state.user_repo = user_repo

    # Map domain exceptions to HTTP status codes (inbound adapter concern).
    _register_domain_exception_handlers(app)

    # Enable CORS for the configured frontend origins (credentials required
    # for the Bearer-token flow). Wildcard is disallowed when credentials are
    # enabled, so we use an explicit origin list from settings.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    router = create_router(service, agent_adapter, notifier_adapter)
    app.include_router(router)

    auth_router = create_auth_router(auth_service, credential_port, email_adapter)
    app.include_router(auth_router, prefix="/api")

    @app.get("/api/health")
    def api_health():
        return {
            "status": "healthy",
            "service": "PantryPulse Backend",
            "architecture": "Ports and Adapters (Hexagonal)",
            "agent_sdk": "AWS Strands Agents SDK",
            "hackathon_track": "Good Neighbor Agents"
        }

    # Mount static frontend if available (for single-container production deployment).
    # We serve the built SPA with a catch-all fallback so client-side routes such as
    # /activate and /reset-password (used by the Mailtrap email links) resolve to
    # index.html instead of a 404.
    candidate_paths = [
        os.environ.get("STATIC_DIR"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../frontend/dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../frontend/dist")),
        "/app/frontend/dist",
        "/app/static"
    ]
    static_path = next((p for p in candidate_paths if p and os.path.isdir(p)), None)

    if static_path:
        index_file = os.path.join(static_path, "index.html")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str):
            # Never shadow the API namespace — undefined /api/* should 404 as JSON.
            if full_path == "api" or full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not found")
            # Serve a real static file if it exists (assets, favicon, etc.).
            if full_path:
                candidate = os.path.join(static_path, full_path)
                if os.path.isfile(candidate):
                    return FileResponse(candidate)
            # Otherwise fall back to the SPA entry point.
            if os.path.isfile(index_file):
                return FileResponse(index_file)
            raise HTTPException(status_code=404, detail="Not found")
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
