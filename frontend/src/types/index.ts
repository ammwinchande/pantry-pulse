export type VehicleType = 'BICYCLE_CARGO' | 'SEDAN' | 'HATCHBACK_SUV' | 'VAN_TRUCK';

export type VolunteerStatus = 'AVAILABLE' | 'DISPATCHED' | 'EN_ROUTE' | 'OFF_DUTY';

export type FoodCategory = 'BAKERY_DRY' | 'PRODUCE' | 'PREPARED_MEALS' | 'DAIRY_FROZEN';

export type DonationStatus =
  | 'REPORTED'
  | 'ANALYZING'
  | 'PENDING_DECISION'
  | 'DISPATCHED'
  | 'IN_TRANSIT'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'EXPIRED';

export type DispatchStatus =
  | 'PROPOSED'
  | 'APPROVED'
  | 'PICKED_UP'
  | 'DELIVERED'
  | 'OVERRIDDEN'
  | 'REJECTED';

export type UserRole = 'COORDINATOR' | 'INTAKE_WORKER' | 'VOLUNTEER' | 'DONOR';

export interface GeoLocation {
  latitude: float;
  longitude: float;
  address: string;
  neighborhood?: string;
}

type float = number;

export interface Volunteer {
  id: string;
  name: string;
  phone: string;
  email: string;
  current_location: GeoLocation;
  vehicle_type: VehicleType;
  cargo_capacity_lbs: number;
  has_cooler: boolean;
  can_lift_heavy: boolean;
  status: VolunteerStatus;
  weekly_shifts_completed: number;
  rating: number;
  avatar_url?: string;
}

export interface DonationAlert {
  id: string;
  donor_name: string;
  donor_contact_name: string;
  donor_phone: string;
  donor_address: GeoLocation;
  food_category: FoodCategory;
  item_description: string;
  estimated_weight_lbs: number;
  box_count: number;
  requires_cold_chain: boolean;
  is_fragile: boolean;
  reported_at: string;
  pickup_deadline: string;
  status: DonationStatus;
  special_instructions?: string;
}

export interface CandidateVolunteer {
  volunteer_id: string;
  name: string;
  vehicle_type: VehicleType;
  distance_miles: number;
  estimated_eta_minutes: number;
  has_cooler: boolean;
  weekly_shifts: number;
  match_score: number;
  selection_reasons: string[];
}

export interface DispatchProposal {
  id: string;
  donation_id: string;
  created_at: string;
  primary_candidate: CandidateVolunteer;
  alternative_candidate?: CandidateVolunteer;
  tradeoff_summary: string;
  agent_reasoning: string;
  urgency_level: string;
  estimated_carbon_saved_kg: number;
  status: DispatchStatus;
}

export interface Dispatch {
  id: string;
  proposal_id: string;
  donation_id: string;
  volunteer_id: string;
  volunteer_name: string;
  donor_name: string;
  donor_address: string;
  pantry_address: string;
  pickup_verification_code: string;
  status: DispatchStatus;
  approved_by: string;
  approved_at: string;
  picked_up_at?: string;
  delivered_at?: string;
  weight_rescued_lbs: number;
  notes?: string;
}

export interface SystemStats {
  total_rescued_lbs: number;
  meals_provided: number;
  active_volunteers: number;
  pending_decisions_count: number;
  active_dispatches_count: number;
  carbon_offset_kg: number;
}

export interface AgentTraceLog {
  timestamp: string;
  event: string;
  tool_called?: string;
  input_params?: Record<string, any>;
  output_summary?: string;
  duration_ms?: number;
}

export interface NotificationMessage {
  id: string;
  recipient_type: string;
  recipient_name: string;
  recipient_phone: string;
  channel: string;
  timestamp: string;
  content: string;
  status: string;
}
