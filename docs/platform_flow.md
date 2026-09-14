# PantryPulse: Platform Flow & Architecture Specification

## 1. Executive Summary
**PantryPulse** is an autonomous, background AI agent platform designed for community food rescue organizations, food banks, and shelters. Built for the **Agents for Humans Hackathon** (Good Neighbor Track), it uses the **AWS Strands Agents SDK** to handle the frantic, repetitive logistics of matching short-notice surplus food donations with volunteer drivers—surfacing only when a human coordinator decision is required.

---

## 2. Core Subsystems

### 2.1 Volunteers Management
Volunteers represent the delivery fleet. Because volunteers are unpaid community members, the system balances operational efficacy with volunteer equity to prevent burnout.

#### Attributes:
- `id`: Unique identifier (UUID).
- `name`: Full name.
- `phone`: Mobile contact for urgent SMS dispatches.
- `current_location`: Latitude and longitude (or neighborhood district).
- `vehicle_type`: `BICYCLE_CARGO`, `SEDAN`, `HATCHBACK_SUV`, `VAN_TRUCK`.
- `cargo_capacity_lbs`: Maximum weight limit of the vehicle.
- `has_cooler`: Whether insulated thermal cooler bags/boxes are available for cold-chain items.
- `can_lift_heavy`: Capable of lifting 40+ lb crates or heavy cargo.
- `status`:
  - `AVAILABLE`: Ready for new dispatches.
  - `DISPATCHED`: Proposed or assigned to an active mission.
  - `EN_ROUTE`: En route to donor or pantry.
  - `OFF_DUTY`: Unavailable for dispatches.
- `weekly_shifts_completed`: Counter used for equity/fatigue balancing.
- `rating`: Reliability and punctuality score (1.0 to 5.0).

---

### 2.2 Donations Management
Food surplus comes from grocery stores, bakeries, campus dining halls, and catered corporate events. These donations typically have narrow 60–120 minute pickup windows before food safety regulations require disposal.

#### Attributes:
- `id`: Unique identifier.
- `donor_name`: Organization name (e.g., "Whole Foods Market - Downtown").
- `donor_address`: Exact pickup address with contact person and phone.
- `food_category`:
  - `BAKERY_DRY`: Bread, pastries, packaged shelf-stable goods.
  - `PRODUCE`: Fresh vegetables, fruits.
  - `PREPARED_MEALS`: Cooked trays from caterers/cafeterias.
  - `DAIRY_FROZEN`: Milk, yogurt, meats requiring strict cold chain.
- `estimated_weight_lbs`: Estimated total weight in pounds.
- `box_count`: Estimated number of standard banana boxes / crates.
- `requires_cold_chain`: Boolean flag enforcing cooler equipment.
- `is_fragile`: Boolean flag (e.g., stacked sheet cakes, ripe berries).
- `pickup_deadline`: UTC ISO timestamp indicating strict cutoff.
- `status`:
  - `REPORTED`: Alert newly created by donor.
  - `ANALYZING`: Strands Agent is evaluating cargo and querying volunteer pool.
  - `PENDING_DECISION`: Strands Agent generated candidate proposal; awaiting coordinator approval.
  - `DISPATCHED`: Coordinator approved dispatch; driver notified.
  - `IN_TRANSIT`: Driver verified pickup and is en route to pantry.
  - `COMPLETED`: Safe delivery confirmed at pantry loading bay; inventory updated.
  - `CANCELLED` / `EXPIRED`: Missed deadline or donor cancellation.

---

### 2.3 Dispatches & Human-in-the-Loop Gate
This is the central innovation of PantryPulse: **the agent does not send arbitrary autonomous dispatches without human oversight; instead, it presents a pre-analyzed, low-cognitive-load decision to the pantry coordinator.**

#### Autonomous Matching Logic:
1. **Hard Filtering:**
   - Filters out volunteers who are `OFF_DUTY` or already `EN_ROUTE`.
   - Filters out volunteers whose vehicle capacity < donation estimated weight.
   - If `requires_cold_chain` is true, filters out volunteers without coolers.
2. **Scoring & Ranking Factors:**
   - **Proximity / ETA (40%)**: Driving distance from volunteer to donor.
   - **Shift Equity (30%)**: Prefers volunteers with lower `weekly_shifts_completed` to balance volunteer engagement.
   - **Vehicle Fit (20%)**: Prefers right-sized vehicles (avoids sending a 15-passenger van for 2 boxes of bread).
   - **Reliability (10%)**: Historical completion rating.
3. **Structured Proposal Output:**
   - **Primary Recommendation**: Best overall match with explicit rationale.
   - **Alternative Candidate**: Next-best driver (e.g., closer but already did 3 shifts, or larger vehicle).
   - **Trade-off Summary**: 1–2 sentence human-readable explanation of why Primary was prioritized.

#### Coordinator Decision Options:
- **Approve Primary**: 1-click execution.
- **Select Alternative**: Overrides with the backup candidate.
- **Decline / Custom**: Reject or manually select another volunteer from the full roster.

#### Custody Verification:
- When approved, a 4-digit numeric verification code is generated (e.g., `5812`).
- Upon arrival at the donor, the driver presents the code, ensuring proof of pickup and preventing food theft or miscommunication.

---

### 2.4 Notifications System
The notification adapter sends targeted, low-friction communications:
1. **Volunteer SMS:** Contains pickup deadline, donor address, cargo summary, and an instant mobile link (`pantrypulse.org/mission/{dispatch_id}`).
2. **Donor Confirmation:** Informs donor of the assigned driver name, vehicle description, ETA, and verification code.
3. **Coordinator Audio/Visual Dashboard Cue:** High-priority toast and chime in the web UI when a donation deadline is within 60 minutes.

---

### 2.5 User Roles & Personas
- **Pantry Coordinator (Administrator):** Operates the desktop Mission Control dashboard. Manages live operations, approves/overrides AI dispatch proposals, edits volunteer fleet, configures pantry inventory thresholds.
- **Volunteer Driver:** Uses the responsive mobile web interface to set availability, receive mission briefs, launch Google/Apple Maps routing, and confirm pickup/drop-off.
- **Pantry Intake Worker:** Uses a tablet at the pantry loading dock to inspect food condition, log the confirmed weight, and route items to refrigerated storage or dry pantry shelves.
- **Food Donor Partner:** Uses a 30-second express form to report food surplus, with zero login friction.

---

## 3. Architecture Pattern: Ports & Adapters (Hexagonal Architecture)

The codebase strictly adheres to the Ports & Adapters design pattern:
- **Core Domain (`domain/`):** Pure Python entities and dataclasses with zero external framework dependencies.
- **Driving Ports (`ports/driving/`):** Abstract use-case interfaces defining inbound operations (`DonationUseCase`, `DispatchUseCase`, `VolunteerUseCase`).
- **Driven Ports (`ports/driven/`):** Abstract interfaces defining secondary dependencies (`AgentPort`, `VolunteerRepoPort`, `DonationRepoPort`, `NotificationPort`).
- **Application Services (`core/`):** Implements driving ports by orchestrating domain models, calling repositories, and invoking the Strands Agent.
- **Adapters (`adapters/`):**
  - **Inbound:** FastAPI REST endpoints and event simulator.
  - **Outbound:** Strands Agent SDK integration with custom `@tool` functions, In-memory/SQLite persistence, Mock SMS/Webhook notification engine.
