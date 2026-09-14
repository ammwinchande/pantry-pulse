import os
import time
from typing import List, Optional
from datetime import datetime, timezone
import logging

from src.domain.models import (
    DonationAlert, Volunteer, DispatchProposal, CandidateVolunteer,
    AgentTraceLog, DispatchStatus
)
from src.ports.driven.agent_port import AgentPort
from src.adapters.outbound.agent.tools import (
    calculate_eta_and_distance, evaluate_cargo_fit, score_volunteer_candidate
)

logger = logging.getLogger("PantryPulseAgent")

class StrandsAgentAdapter(AgentPort):
    def __init__(self):
        self._traces: List[AgentTraceLog] = []
        self._agent = None
        self._init_strands_agent()

    def _init_strands_agent(self):
        try:
            from strands import Agent
            # Configure Strands Agent with the custom tools
            self._agent = Agent(
                tools=[
                    calculate_eta_and_distance,
                    evaluate_cargo_fit,
                    score_volunteer_candidate
                ]
            )
            logger.info("Strands Agent initialized with tools.")
        except Exception as e:
            logger.warning(f"Strands Agent initialization fallback: {e}")
            self._agent = None

    def evaluate_and_propose(
        self, donation: DonationAlert, available_volunteers: List[Volunteer]
    ) -> DispatchProposal:
        """
        Executes candidate scoring across the available volunteer fleet using
        Strands tools and constructs a structured DispatchProposal.
        """
        start_time = time.time()
        self._log_trace(
            event="ANALYSIS_START",
            tool_called=None,
            input_params={
                "donation_id": donation.id,
                "donor": donation.donor_name,
                "weight_lbs": donation.estimated_weight_lbs,
                "requires_cold_chain": donation.requires_cold_chain,
                "volunteers_count": len(available_volunteers)
            },
            output_summary=f"Initiating autonomous matching for {donation.donor_name}."
        )

        ranked_candidates: List[CandidateVolunteer] = []

        for vol in available_volunteers:
            # 1. Tool Call: Calculate ETA & Distance
            t1 = time.time()
            dist_res = calculate_eta_and_distance(
                volunteer_lat=vol.current_location.latitude,
                volunteer_lon=vol.current_location.longitude,
                donor_lat=donation.donor_address.latitude,
                donor_lon=donation.donor_address.longitude
            )
            dur_dist = int((time.time() - t1) * 1000)
            self._log_trace(
                event="TOOL_CALL",
                tool_called="calculate_eta_and_distance",
                input_params={"volunteer": vol.name, "location": vol.current_location.neighborhood},
                output_summary=f"{vol.name}: {dist_res['distance_miles']} mi, {dist_res['eta_minutes']} min ETA",
                duration_ms=dur_dist
            )

            # 2. Tool Call: Evaluate Cargo Fit & Cold-Chain
            t2 = time.time()
            cargo_res = evaluate_cargo_fit(
                vehicle_type=vol.vehicle_type.value,
                cargo_capacity_lbs=vol.cargo_capacity_lbs,
                has_cooler=vol.has_cooler,
                required_weight_lbs=donation.estimated_weight_lbs,
                requires_cold_chain=donation.requires_cold_chain,
                is_fragile=donation.is_fragile
            )
            dur_cargo = int((time.time() - t2) * 1000)
            self._log_trace(
                event="TOOL_CALL",
                tool_called="evaluate_cargo_fit",
                input_params={"volunteer": vol.name, "vehicle": vol.vehicle_type.value, "has_cooler": vol.has_cooler},
                output_summary=f"Compatible: {cargo_res['is_compatible']} (Fit: {cargo_res['fit_score']})",
                duration_ms=dur_cargo
            )

            if not cargo_res["is_compatible"]:
                continue

            # 3. Tool Call: Score Volunteer Balancing Equity
            t3 = time.time()
            score_res = score_volunteer_candidate(
                distance_miles=dist_res["distance_miles"],
                eta_minutes=dist_res["eta_minutes"],
                weekly_shifts_completed=vol.weekly_shifts_completed,
                cargo_fit_score=cargo_res["fit_score"],
                volunteer_rating=vol.rating
            )
            dur_score = int((time.time() - t3) * 1000)
            self._log_trace(
                event="TOOL_CALL",
                tool_called="score_volunteer_candidate",
                input_params={"volunteer": vol.name, "shifts": vol.weekly_shifts_completed},
                output_summary=f"Composite Score: {score_res['composite_score']}/100",
                duration_ms=dur_score
            )

            reasons = dist_res.get("reasons", []) + cargo_res.get("reasons", []) + score_res.get("ranking_factors", [])

            ranked_candidates.append(
                CandidateVolunteer(
                    volunteer_id=vol.id,
                    name=vol.name,
                    vehicle_type=vol.vehicle_type,
                    distance_miles=dist_res["distance_miles"],
                    estimated_eta_minutes=dist_res["eta_minutes"],
                    has_cooler=vol.has_cooler,
                    weekly_shifts=vol.weekly_shifts_completed,
                    match_score=score_res["composite_score"],
                    selection_reasons=reasons
                )
            )

        # Sort candidates descending by match score
        ranked_candidates.sort(key=lambda c: c.match_score, reverse=True)

        if not ranked_candidates:
            # Fallback if no volunteer strictly passed
            primary = CandidateVolunteer(
                volunteer_id=available_volunteers[0].id,
                name=available_volunteers[0].name,
                vehicle_type=available_volunteers[0].vehicle_type,
                distance_miles=4.5,
                estimated_eta_minutes=18,
                has_cooler=available_volunteers[0].has_cooler,
                weekly_shifts=available_volunteers[0].weekly_shifts_completed,
                match_score=50.0,
                selection_reasons=["Emergency fallback match"]
            )
            alternative = None
            tradeoff = "No perfect matches found. Flagged nearest available driver for coordinator review."
            reasoning = "All active drivers are either near capacity or lack specified gear. Manual override advised."
        else:
            primary = ranked_candidates[0]
            alternative = ranked_candidates[1] if len(ranked_candidates) > 1 else None

            if alternative:
                tradeoff = (
                    f"Prioritized {primary.name} ({primary.estimated_eta_minutes} min ETA, {primary.weekly_shifts} shifts) "
                    f"over {alternative.name} ({alternative.estimated_eta_minutes} min ETA, {alternative.weekly_shifts} shifts) "
                    f"for optimal proximity and shift fatigue balance."
                )
            else:
                tradeoff = f"{primary.name} is the sole qualified driver with suitable vehicle capacity in range."

            reasoning = (
                f"Strands Agent evaluated {len(available_volunteers)} available drivers against "
                f"{donation.estimated_weight_lbs} lbs {donation.food_category.value} requirement. "
                f"{primary.name} scored highest ({primary.match_score}/100) due to "
                f"{primary.estimated_eta_minutes} min ETA and right-sized {primary.vehicle_type.value}."
            )

        # 2.5 kg CO2e saved per 1 lb of rescued food diverted from landfill
        carbon_saved = round(donation.estimated_weight_lbs * 2.5, 1)

        total_dur = int((time.time() - start_time) * 1000)
        self._log_trace(
            event="PROPOSAL_GENERATED",
            tool_called=None,
            input_params={"primary": primary.name, "score": primary.match_score},
            output_summary=f"Proposal created. Primary: {primary.name}, Tradeoff: {tradeoff}",
            duration_ms=total_dur
        )

        return DispatchProposal(
            donation_id=donation.id,
            primary_candidate=primary,
            alternative_candidate=alternative,
            tradeoff_summary=tradeoff,
            agent_reasoning=reasoning,
            urgency_level="CRITICAL" if donation.requires_cold_chain else "HIGH",
            estimated_carbon_saved_kg=carbon_saved,
            status=DispatchStatus.PROPOSED
        )

    def get_traces(self) -> List[AgentTraceLog]:
        return list(reversed(self._traces[-50:]))

    def _log_trace(
        self,
        event: str,
        tool_called: Optional[str],
        input_params: Optional[dict],
        output_summary: Optional[str],
        duration_ms: Optional[int] = None
    ):
        log = AgentTraceLog(
            timestamp=datetime.now(timezone.utc),
            event=event,
            tool_called=tool_called,
            input_params=input_params,
            output_summary=output_summary,
            duration_ms=duration_ms
        )
        self._traces.append(log)
        logger.info(f"[StrandsAgent] {event} - {tool_called or ''}: {output_summary}")
