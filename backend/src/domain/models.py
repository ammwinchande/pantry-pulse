from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

class VehicleType(str, Enum):
    BICYCLE_CARGO = "BICYCLE_CARGO"
    SEDAN = "SEDAN"
    HATCHBACK_SUV = "HATCHBACK_SUV"
    VAN_TRUCK = "VAN_TRUCK"

class VolunteerStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    OFF_DUTY = "OFF_DUTY"

class FoodCategory(str, Enum):
    BAKERY_DRY = "BAKERY_DRY"
    PRODUCE = "PRODUCE"
    PREPARED_MEALS = "PREPARED_MEALS"
    DAIRY_FROZEN = "DAIRY_FROZEN"

class DonationStatus(str, Enum):
    REPORTED = "REPORTED"
    ANALYZING = "ANALYZING"
    PENDING_DECISION = "PENDING_DECISION"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class DispatchStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    OVERRIDDEN = "OVERRIDDEN"
    REJECTED = "REJECTED"

class UserRole(str, Enum):
    COORDINATOR = "COORDINATOR"      # Mission control supervisor / decision approver
    INTAKE_WORKER = "INTAKE_WORKER"  # Pantry loading dock intake
    VOLUNTEER = "VOLUNTEER"          # Driver receiving dispatches
    DONOR = "DONOR"                  # Supermarket/bakery surplus reporter

class GeoLocation(BaseModel):
    latitude: float
    longitude: float
    address: str
    neighborhood: Optional[str] = None

class Volunteer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: str
    current_location: GeoLocation
    vehicle_type: VehicleType
    cargo_capacity_lbs: int
    has_cooler: bool = False
    can_lift_heavy: bool = True
    status: VolunteerStatus = VolunteerStatus.AVAILABLE
    weekly_shifts_completed: int = 0
    rating: float = 4.9
    avatar_url: Optional[str] = None

class DonationAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    donor_name: str
    donor_contact_name: str
    donor_phone: str
    donor_address: GeoLocation
    food_category: FoodCategory
    item_description: str
    estimated_weight_lbs: int
    box_count: int
    requires_cold_chain: bool = False
    is_fragile: bool = False
    reported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pickup_deadline: datetime
    status: DonationStatus = DonationStatus.REPORTED
    special_instructions: Optional[str] = None

class CandidateVolunteer(BaseModel):
    volunteer_id: str
    name: str
    vehicle_type: VehicleType
    distance_miles: float
    estimated_eta_minutes: int
    has_cooler: bool
    weekly_shifts: int
    match_score: float
    selection_reasons: List[str]

class DispatchProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    donation_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    primary_candidate: CandidateVolunteer
    alternative_candidate: Optional[CandidateVolunteer] = None
    tradeoff_summary: str
    agent_reasoning: str
    urgency_level: str = "HIGH" # CRITICAL, HIGH, MEDIUM
    estimated_carbon_saved_kg: float = 0.0
    status: DispatchStatus = DispatchStatus.PROPOSED

class Dispatch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    donation_id: str
    volunteer_id: str
    volunteer_name: str
    donor_name: str
    donor_address: str
    pantry_address: str = "Community Food Pantry, 1420 Hope St, Seattle, WA"
    pickup_verification_code: str
    status: DispatchStatus = DispatchStatus.APPROVED
    approved_by: str = "Coordinator Sarah L."
    approved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    weight_rescued_lbs: int
    notes: Optional[str] = None

class User(BaseModel):
    """Application user (coordinator, intake worker, volunteer, donor)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    role: UserRole
    organization: str = "Downtown Community Pantry"
    is_active: bool = False
    email_verified_at: Optional[datetime] = None
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthToken(BaseModel):
    """JWT access token issued after login / registration activation."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: User

class SystemStats(BaseModel):
    total_rescued_lbs: int
    meals_provided: int
    active_volunteers: int
    pending_decisions_count: int
    active_dispatches_count: int
    carbon_offset_kg: float

class AgentTraceLog(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event: str
    tool_called: Optional[str] = None
    input_params: Optional[Dict[str, Any]] = None
    output_summary: Optional[str] = None
    duration_ms: Optional[int] = None
