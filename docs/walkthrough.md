# PantryPulse: Build & Verification Walkthrough

**PantryPulse** is an autonomous, background AI agent platform built for the **Agents for Humans Hackathon** (Good Neighbor Track). It uses the **AWS Strands Agents SDK** to handle the chaotic, time-sensitive logistics of matching community food rescues with volunteer drivers, surfacing only when a human coordinator decision is required.

---

## 🚀 What Was Built

### 1. Backend (Python 3.14 + `uv` + Ports and Adapters)
- **Directory**: `pantry-pulse/backend/`
- **Architecture**: Strict **Hexagonal Architecture (Ports and Adapters)**:
  - **Core Domain (`src/domain/`)**: Pure typed models (`DonationAlert`, `Volunteer`, `DispatchProposal`, `Dispatch`, `GeoLocation`, `SystemStats`, `AgentTraceLog`).
  - **Driving Ports (`src/ports/driving/`)**: Inbound use cases (`DonationUseCase`, `DispatchUseCase`, `VolunteerUseCase`).
  - **Driven Ports (`src/ports/driven/`)**: Outbound SPIs (`AgentPort`, `VolunteerRepositoryPort`, `DonationRepositoryPort`, `DispatchRepositoryPort`, `NotificationPort`, `UserRepositoryPort`, `CredentialPort`, `EmailPort`).
  - **Application Service (`src/core/services.py`)**: Coordinates domain logic, calculates real-time community impact (meals rescued, carbon offset), and handles state transitions.
  - **Auth Service (`src/core/auth_service.py`)**: Handles login (verifies credentials, issues JWTs), token verification, and password-reset email dispatch — all behind the driven auth ports.
  - **Strands Agent Adapter (`src/adapters/outbound/agent/`)**:
    - Wrapped Strands `Agent` using `@tool` decorated functions:
      - `calculate_eta_and_distance`: Computes proximity and driving time with urban traffic multipliers.
      - `evaluate_cargo_fit`: Enforces cold-chain refrigeration, weight limits, and right-sized vehicles.
      - `score_volunteer_candidate`: Evaluates composite scores while factoring in weekly shift fatigue to prevent driver burnout.
    - Records OpenTelemetry-style in-memory execution traces with millisecond latencies.
  - **Inbound REST Adapter (`src/adapters/inbound/rest/`)**: FastAPI server with CORS, health check, and endpoints for proposals, 1-click approvals, pickup confirmations, live trace inspection, plus `auth_routes.py` for login / token verification / password reset.
  - **Persistence Adapter (`src/adapters/outbound/persistence/`)**: SQLAlchemy-backed repositories (`sqlalchemy_repos.py`) over ORM models (`orm_models.py`), with an engine/session factory (`db.py`), domain↔ORM `mappers.py`, a single-source-of-truth `seed_data.py`, and an idempotent `seeder.py`. The datastore is selected by `DATABASE_URL` — SQLite by default, Postgres/MySQL in production. `in_memory_repo.py` remains for fast unit tests.
  - **Auth Adapters (`src/adapters/outbound/auth/`)**: `jwt_credential_adapter.py` (salted PBKDF2-HMAC-SHA256 password hashing + JWT issue/verify) and `mailtrap_email_adapter.py` (SMTP delivery of password-reset emails via Mailtrap).

### 2. Frontend (React 19 + TypeScript + TanStack Query + Tailwind CSS)
- **Directory**: `pantry-pulse/frontend/`
- **Stack**: Vite + React + TypeScript + TanStack Query (`@tanstack/react-query`) + Lucide React + Tailwind CSS.
- **Key UI Components**:
  - `Header.tsx`: Live rescue counters (Total Rescued lbs, Meals Provided, CO₂ Offset, Fleet Ready), one-click **"Simulate Surplus Alert"** button, and persona tabs.
  - `DecisionGate.tsx`: **The Core Hackathon Innovation** — An autonomous decision gate that surfaces primary & alternative driver recommendations, match score (e.g. 96/100), transparent trade-off rationale, and 1-click approval.
  - `LiveSurplusFeed.tsx`: Live stream of food rescue alerts with cold-chain badges, category tags, and countdown timers.
  - `VolunteerFleetView.tsx`: Live fleet cards with vehicle specs, cooler availability, shift counts, and availability toggling.
  - `AgentTraceDrawer.tsx`: Observability drawer displaying live Strands Agent tool executions and latencies for hackathon judges.
  - `DriverMissionView.tsx`: Mobile-first view for the volunteer driver showing turn-by-turn route and 4-digit pickup code.
  - `DockIntakeView.tsx`: Loading dock tablet view for pantry intake staff to inspect incoming food and log verified scale weights.
  - `DonorSurplusView.tsx`: Express 30-second surplus alert submission form for supermarkets and bakeries.

### 3. Documentation & Open Source Compliance
- `pantry-pulse/docs/platform_flow.md`: In-depth platform flow and lifecycle specification.
- `pantry-pulse/README.md`: Comprehensive guide with problem description, architecture diagrams, setup instructions, and demo guide.
- `pantry-pulse/LICENSE`: MIT Open Source License (required by hackathon rules).

---

## 🧪 Verification & Test Results

### 1. Backend Automated Tests
Ran `PYTHONPATH=. .venv/bin/pytest tests/` covering domain models, agent scoring, dispatch lifecycle, and FastAPI endpoints:

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/ammwinchande/Developer/Hackathons/build-ai-agents/pantry-pulse/backend
collected 25 items

tests/test_api_endpoints.py ........                                     [ 32%]
tests/test_auth.py ............                                          [ 76%]
tests/test_domain_and_service.py ......                                  [100%]

======================== 25 passed, 1 warning in 13.08s ========================
```

The suite covers domain models, agent scoring, dispatch lifecycle, FastAPI endpoints, and the full authentication flow (login, JWT verification, password hashing, and reset). The API tests run against an isolated in-memory SQLite database seeded by the same `seeder.py` used in production, so persistence behavior is exercised end-to-end.

### 2. End-to-End Simulation Test
Executed end-to-end Python integration runner:
- Initial state: 85 lbs rescued, 70 meals provided.
- Simulated surplus alert (110 lbs produce).
- Strands Agent evaluated candidates and generated proposal.
- Coordinator 1-click approved primary candidate.
- Generated pickup verification code: `7114`.
- Driver confirmed pickup; loading dock verified delivery.
- Updated state: 195 lbs rescued, 162 meals provided, 487.5 kg CO₂ offset.

### 3. Frontend Production Build
Ran `npm run build` with TypeScript type-checking:

```text
✓ 1919 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-D-G-R64l.css   46.68 kB │ gzip:  7.83 kB
dist/assets/index-BSdmPVrq.js   323.37 kB │ gzip: 94.15 kB
✓ built in 1.07s
```

---

## 🖥️ How to Run Locally

### Terminal 1: Backend
```bash
cd pantry-pulse/backend
source .venv/bin/activate
PYTHONPATH=. .venv/bin/python src/main.py
```
Backend runs at `http://localhost:8000` (API Docs at `http://localhost:8000/docs`).

On first boot the app creates the SQLite datastore (`pantrypulse.db`) and seeds the demo fleet, one completed donation, one delivered dispatch, and the demo coordinator account. Seeding is idempotent. To use PostgreSQL or MySQL instead, set `DATABASE_URL` (see `backend/.env.example`) — no code changes required.

Log in with the seeded demo coordinator: `coordinator@pantrypulse.org` / `Coordinator123!`.

### Terminal 2: Frontend
```bash
cd pantry-pulse/frontend
npm run dev
```
Open `http://localhost:5173` in your browser.
