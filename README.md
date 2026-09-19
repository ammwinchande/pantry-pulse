# 🥗 PantryPulse

> **Autonomous Food Rescue & Volunteer Dispatch Agent**
> Built for the **Agents for Humans Hackathon** (Good Neighbor Track) using the **AWS Strands Agents SDK**.

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](./LICENSE)
[![Strands Agents SDK](https://img.shields.io/badge/Strands_Agents_SDK-AWS_Bedrock-orange.svg)](https://strandsagents.com)
[![Python 3.14](https://img.shields.io/badge/Python-3.14_%7C_uv-blue.svg)](https://docs.astral.sh/uv/)
[![React + TypeScript](https://img.shields.io/badge/Frontend-React_19_%2B_TypeScript_%2B_TanStack_Query-61dafb.svg)](https://tanstack.com/query)
[![Architecture: Hexagonal](https://img.shields.io/badge/Architecture-Ports_%26_Adapters-purple.svg)](./docs/platform_flow.md)

---

## 🎯 The Problem
Local food banks, community pantries, and shelters operate with small, volunteer-driven teams. Every day, grocery stores, bakeries, and catered corporate events call with sudden 60–90 minute windows to pick up surplus fresh food before it is discarded.

Coordinators lose **10–15 hours every week** to frantic, repetitive logistics:
- Checking who has a car or van available right now
- Verifying who has insulated coolers for perishable or cold-chain items
- Calling, texting, and juggling driver fatigue to avoid burning out the same volunteers
- Ensuring food safety chain of custody

## 💡 The Solution: An Agent That Works in the Background
Instead of giving coordinators another app to babysit, **PantryPulse** runs quietly in the background:
1. **Autonomous Ingestion & Cargo Analysis**: Evaluates weight, crates, fragility, and cold-chain refrigeration needs.
2. **Strands Agent Matching & Scoring**: Executes custom Strands `@tool` functions to calculate driving distance, vehicle cargo suitability, and volunteer shift equity.
3. **The Human-in-the-Loop Decision Gate**: The agent pauses and surfaces a high-clarity recommendation card to the coordinator with primary and alternative candidates.
4. **Autonomous Execution**: On 1-click coordinator approval, the agent automatically dispatches the driver via SMS, issues a secure 4-digit pickup code to the donor, tracks delivery, and updates pantry inventory.

---

## 🏗️ Architecture: Ports & Adapters (Hexagonal)

```mermaid
graph TD
    subgraph Driving / Inbound Adapters
        WebAPI[FastAPI REST API]
        Sim[Surplus Alert Simulator]
    end

    subgraph Driving Ports
        DonationPort[Donation Ingestion Port]
        DispatchPort[Dispatch Management Port]
        VolunteerPort[Volunteer Fleet Port]
    end

    subgraph Core Domain
        PantryEngine[PantryPulse Application Service]
        Models[Domain Models: Donation, Volunteer, Proposal, Dispatch]
    end

    subgraph Driven Ports
        AgentPort[Strands Agent Reasoning Port]
        VolunteerRepoPort[Volunteer Repository Port]
        DonationRepoPort[Donation Repository Port]
        NotifierPort[Notification & Dispatch Port]
    end

    subgraph Driven / Outbound Adapters
        StrandsAdapter[Strands Agents SDK Adapter with Custom @tool Functions]
        MemRepo[SQLAlchemy Repository<br/>SQLite default · Postgres/MySQL via DATABASE_URL]
        SMSAdapter[Mock SMS & Webhook Dispatch Notifier]
    end

    WebAPI --> DispatchPort
    WebAPI --> VolunteerPort
    Sim --> DonationPort
    DispatchPort --> PantryEngine
    DonationPort --> PantryEngine
    VolunteerPort --> PantryEngine
    PantryEngine --> Models
    PantryEngine --> AgentPort
    PantryEngine --> VolunteerRepoPort
    PantryEngine --> DonationRepoPort
    PantryEngine --> NotifierPort
    AgentPort --> StrandsAdapter
    VolunteerRepoPort --> MemRepo
    DonationRepoPort --> MemRepo
    NotifierPort --> SMSAdapter
```

---

## 📁 Project Structure

```
pantry-pulse/
├── backend/
│   ├── .venv/                         # Python 3.14 virtual environment (managed via uv)
│   ├── pyproject.toml / requirements.txt
│   ├── src/
│   │   ├── domain/                    # Pure domain models (zero framework dependencies)
│   │   │   ├── models.py              # Volunteer, DonationAlert, DispatchProposal, Dispatch
│   │   │   └── exceptions.py
│   │   ├── ports/                     # Abstract interfaces (Contracts)
│   │   │   ├── driving/               # Inbound use cases (Donation, Dispatch, Volunteer)
│   │   │   └── driven/                # Outbound SPIs (Repos, Agent, Notifier, Auth)
│   │   ├── core/                      # Application service orchestrator
│   │   │   ├── services.py
│   │   │   └── auth_service.py        # Login / token verification / password reset
│   │   ├── adapters/                  # Concrete implementations
│   │   │   ├── inbound/rest/          # FastAPI routes, auth routes & app factory
│   │   │   └── outbound/
│   │   │       ├── agent/             # Strands Agents SDK adapter & custom @tool functions
│   │   │       ├── persistence/       # SQLAlchemy repos, ORM models, seeder & seed data
│   │   │       ├── notification/      # SMS / webhook mock delivery engine
│   │   │       └── auth/              # JWT credential adapter & Mailtrap email adapter
│   │   └── main.py                    # Composition root & server startup
│   └── tests/                         # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── api/                       # TanStack Query client & hooks
│   │   ├── components/
│   │   │   ├── Header.tsx             # Live metrics, persona tabs & simulator button
│   │   │   ├── DecisionGate.tsx       # The Human-in-the-Loop decision checkpoint card
│   │   │   ├── LiveSurplusFeed.tsx    # Live food rescue alerts feed
│   │   │   ├── VolunteerFleetView.tsx # Driver fleet cards & on/off duty toggling
│   │   │   ├── AgentTraceDrawer.tsx   # Live Strands Agent tool execution traces
│   │   │   ├── DriverMissionView.tsx  # Volunteer driver mobile-first turn-by-turn view
│   │   │   ├── DockIntakeView.tsx     # Loading dock weight inspection view
│   │   │   └── DonorSurplusView.tsx   # 30-second donor surplus intake form
│   │   ├── types/                     # TypeScript domain definitions
│   │   └── App.tsx                    # Root dashboard application
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   └── platform_flow.md               # In-depth architectural & lifecycle specification
├── LICENSE                            # MIT Open Source License
└── README.md
```

---

## ⚡ Quickstart Guide

### Prerequisites
- **Python 3.10+** (Python 3.14 supported)
- **Node.js 18+** & **npm**

---

### 1. Backend Setup (Python 3.14 via `uv`)

```bash
cd pantry-pulse/backend

# Activate the existing virtual environment or create a new one:
source .venv/bin/activate

# Install dependencies using uv:
.venv/bin/uv pip install -r requirements.txt

# Run unit tests:
PYTHONPATH=. .venv/bin/pytest tests/

# Start the FastAPI backend:
PYTHONPATH=. .venv/bin/python src/main.py
```
The backend starts at `http://localhost:8000`.
API Docs (Swagger UI): `http://localhost:8000/docs`

On first boot the app creates its datastore (SQLite file `pantrypulse.db` by default) and seeds the demo fleet, one completed donation, one delivered dispatch, and the demo coordinator account. Seeding is idempotent — restarting the app never duplicates data.

### Datastore & Seeding

Persistence is driven entirely by the `DATABASE_URL` environment variable (see `backend/.env.example`):

| Target                       | `DATABASE_URL`                                         |
| ---------------------------- | ------------------------------------------------------ |
| SQLite (default, zero-setup) | `sqlite:///pantrypulse.db`                             |
| PostgreSQL                   | `postgresql+psycopg://user:pass@host:5432/pantrypulse` |
| MySQL                        | `mysql+pymysql://user:pass@host:3306/pantrypulse`      |

Switching from SQLite to Postgres or MySQL in production is a one-line environment change — no application code changes. Set `SEED_ON_STARTUP=false` to skip seeding (e.g., when the database is already populated).

### Authentication

The app is protected by JWT authentication. Log in with the seeded demo coordinator:

- **Email:** `coordinator@pantrypulse.org`
- **Password:** `Coordinator123!`

`POST /api/auth/login` returns a JWT that the frontend stores and sends as a `Bearer` token on every API call. Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes (never plaintext), and password-reset emails are delivered via Mailtrap SMTP.

---

### 2. Frontend Setup (React + TypeScript + TanStack Query)

In a separate terminal:
```bash
cd pantry-pulse/frontend

# Install dependencies:
npm install

# Start development server:
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Demo Scenarios & Walkthrough for Judges

1. **Autonomous Background Triage**: Click **"Simulate Surplus Alert"** in the top navigation bar.
2. **Observe Strands Tool Execution**: Open the **"Strands Agents SDK • Live Reasoning Trace"** drawer to see tools executing in real time (`calculate_eta_and_distance`, `evaluate_cargo_fit`, `score_volunteer_candidate`).
3. **Review the Human-in-the-Loop Decision Gate**:
   - The coordinator sees the **Primary Recommendation** with a match score (e.g., Sarah Lin with 94/100, 6 min ETA, cooler equipped).
   - An **Alternative Candidate** is shown with a transparent trade-off rationale explaining why Primary was chosen (proximity vs. shift fatigue).
4. **Approve Dispatch**: Click **"Approve Dispatch: Sarah Lin"**.
   - Watch the automated SMS notification fire.
   - Switch to **"Volunteer Driver View"** to inspect the turn-by-turn routing and 4-digit pickup code (`3914`).
   - Click **"Confirm Food Picked Up"**.
5. **Receive at Dock**: Switch to **"Dock Intake Staff"** tab to verify the shipment weight on the scale and click **"Confirm & Receive into Pantry Inventory"**.
6. **Community Impact**: Notice the live counters immediately update (Total Rescued lbs, Meals Provided, and Carbon Offset in kg CO₂e).

---

## 📄 License
This project is open-source under the [MIT License](./LICENSE).
