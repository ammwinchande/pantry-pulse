import math
from typing import Dict, Any, List
from strands import tool
from src.domain.models import VehicleType

@tool
def calculate_eta_and_distance(
    volunteer_lat: float,
    volunteer_lon: float,
    donor_lat: float,
    donor_lon: float
) -> Dict[str, Any]:
    """
    Calculates estimated driving distance in miles and ETA in minutes
    between a volunteer driver and food donor coordinates using Haversine formula
    and urban traffic multipliers.

    Args:
        volunteer_lat: Latitude of volunteer
        volunteer_lon: Longitude of volunteer
        donor_lat: Latitude of food donor
        donor_lon: Longitude of food donor

    Returns:
        Dictionary with 'distance_miles' (float) and 'eta_minutes' (int).
    """
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(donor_lat - volunteer_lat)
    dlon = math.radians(donor_lon - volunteer_lon)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(volunteer_lat))
        * math.cos(math.radians(donor_lat))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    # In city traffic: ~20 mph average + 2 min dispatch buffer
    distance_miles = round(max(distance * 1.25, 0.4), 1)
    eta_minutes = int(max(round((distance_miles / 20.0) * 60) + 2, 4))

    return {
        "distance_miles": distance_miles,
        "eta_minutes": eta_minutes
    }

@tool
def evaluate_cargo_fit(
    vehicle_type: str,
    cargo_capacity_lbs: int,
    has_cooler: bool,
    required_weight_lbs: int,
    requires_cold_chain: bool,
    is_fragile: bool
) -> Dict[str, Any]:
    """
    Evaluates whether a volunteer's vehicle, capacity, and equipment meet
    the food safety and volume requirements of the donation.

    Args:
        vehicle_type: BICYCLE_CARGO, SEDAN, HATCHBACK_SUV, VAN_TRUCK
        cargo_capacity_lbs: Maximum weight vehicle can hold
        has_cooler: Whether vehicle has thermal cooler for perishables
        required_weight_lbs: Estimated weight of donation
        requires_cold_chain: True if frozen/dairy/meat requires refrigeration
        is_fragile: True if items like cakes/berries require flat cargo floor

    Returns:
        Dictionary with 'is_compatible' (bool), 'fit_score' (float 0.0-1.0), and 'reasons' (list of str).
    """
    reasons: List[str] = []
    is_compatible = True
    fit_score = 1.0

    if requires_cold_chain and not has_cooler:
        is_compatible = False
        reasons.append("Fails cold-chain requirement: vehicle lacks thermal cooler.")

    if cargo_capacity_lbs < required_weight_lbs:
        is_compatible = False
        reasons.append(f"Insufficient capacity ({cargo_capacity_lbs} lbs < {required_weight_lbs} lbs required).")

    if is_fragile and vehicle_type == VehicleType.BICYCLE_CARGO.value:
        fit_score -= 0.3
        reasons.append("Bicycle transit risks damaging fragile food trays.")

    # Right-sizing bonus: avoid sending a huge truck for a 15 lb box
    capacity_ratio = required_weight_lbs / max(cargo_capacity_lbs, 1)
    if capacity_ratio < 0.1 and vehicle_type == VehicleType.VAN_TRUCK.value:
        fit_score -= 0.2
        reasons.append("Vehicle oversized for small cargo (fuel inefficiency).")
    elif 0.3 <= capacity_ratio <= 0.85:
        fit_score += 0.1
        reasons.append("Optimal cargo space utilization.")

    return {
        "is_compatible": is_compatible,
        "fit_score": round(max(min(fit_score, 1.0), 0.0), 2),
        "reasons": reasons
    }

@tool
def score_volunteer_candidate(
    distance_miles: float,
    eta_minutes: int,
    weekly_shifts_completed: int,
    cargo_fit_score: float,
    volunteer_rating: float
) -> Dict[str, Any]:
    """
    Computes a composite heuristic score (0 to 100) balancing proximity,
    volunteer shift equity to prevent burnout, and vehicle suitability.

    Args:
        distance_miles: Distance in miles
        eta_minutes: ETA in minutes
        weekly_shifts_completed: Shifts already done this week
        cargo_fit_score: 0.0 to 1.0 score from evaluate_cargo_fit
        volunteer_rating: Reliability rating (1.0 to 5.0)

    Returns:
        Dictionary with 'composite_score' (float) and 'ranking_factors' (list of str).
    """
    # Proximity component (40 pts max, decaying with distance)
    proximity_pts = max(40.0 - (distance_miles * 4.0), 5.0)

    # Equity component (30 pts max, penalizing high shifts to rotate drivers)
    # 0 shifts: 30 pts; 1 shift: 24 pts; 2 shifts: 18 pts; 3+ shifts: 10 pts
    equity_pts = max(30.0 - (weekly_shifts_completed * 6.0), 8.0)

    # Cargo fit component (20 pts max)
    cargo_pts = cargo_fit_score * 20.0

    # Rating component (10 pts max)
    rating_pts = (volunteer_rating / 5.0) * 10.0

    total_score = round(proximity_pts + equity_pts + cargo_pts + rating_pts, 1)

    factors = [
        f"ETA: {eta_minutes} min ({distance_miles} mi)",
        f"Weekly shifts: {weekly_shifts_completed} (fatigue-balanced)",
        f"Cargo fit: {int(cargo_fit_score * 100)}%",
        f"Rating: {volunteer_rating}★"
    ]

    return {
        "composite_score": total_score,
        "ranking_factors": factors
    }
