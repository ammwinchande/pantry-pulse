import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Navigation,
  ShieldCheck,
  Flame,
  ArrowRightLeft,
  XCircle,
  ThermometerSnowflake,
  Cpu,
} from 'lucide-react';
import type { DispatchProposal, DonationAlert } from '../types';

interface DecisionGateProps {
  proposals: DispatchProposal[];
  donations: DonationAlert[];
  onApprove: (proposalId: string) => void;
  onOverrideAlternative: (proposalId: string) => void;
  onReject: (proposalId: string, reason: string) => void;
  isApproving: boolean;
}

export const DecisionGate: React.FC<DecisionGateProps> = ({
  proposals,
  donations,
  onApprove,
  onOverrideAlternative,
  onReject,
  isApproving,
}) => {
  if (!proposals || proposals.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center backdrop-blur-sm">
        <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto mb-3">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-white mb-1">Autonomous Agent Idle</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          No pending human decisions. The Strands Agent is quietly monitoring donation channels in
          the background and will only surface when candidate driver triage requires authorization.
        </p>
        <p className="text-xs text-slate-500 mt-4">
          Tip: Click <span className="text-emerald-400 font-semibold">"Simulate Surplus Alert"</span> above to test the autonomous triage loop.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-400 animate-ping" />
          <h2 className="text-xl font-black text-white m-0 tracking-tight">
            Human-in-the-Loop Decision Gates ({proposals.length})
          </h2>
        </div>
        <span className="text-xs bg-amber-500/10 text-amber-300 border border-amber-500/30 font-medium px-2.5 py-1 rounded-full">
          Autonomous Action Paused • Awaiting Coordinator Authorization
        </span>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {proposals.map((proposal) => {
          const donation = donations.find((d) => d.id === proposal.donation_id);
          const primary = proposal.primary_candidate;
          const alt = proposal.alternative_candidate;

          return (
            <div
              key={proposal.id}
              className="bg-gradient-to-b from-slate-900 via-slate-900/95 to-slate-950 border-2 border-amber-500/40 rounded-2xl p-6 shadow-2xl shadow-amber-500/5 relative overflow-hidden"
            >
              {/* Top Accent Stripe */}
              <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-amber-500 via-emerald-500 to-teal-500" />

              {/* Header Info */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="bg-red-500/10 text-red-400 border border-red-500/30 text-[11px] font-bold px-2 py-0.5 rounded uppercase flex items-center gap-1">
                      <Flame className="w-3 h-3" />
                      {proposal.urgency_level} URGENCY RESCUE
                    </span>
                    {donation?.requires_cold_chain && (
                      <span className="bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
                        <ThermometerSnowflake className="w-3 h-3" />
                        Cold Chain Required
                      </span>
                    )}
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      Deadline in ~60m
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">
                    {donation ? donation.donor_name : 'Emergency Food Donor'}
                  </h3>
                  <p className="text-sm text-slate-300">
                    <span className="font-semibold text-emerald-400">
                      {donation?.estimated_weight_lbs} lbs
                    </span>{' '}
                    • {donation?.item_description} ({donation?.box_count} boxes)
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    📍 {donation?.donor_address.address}, {donation?.donor_address.neighborhood}
                  </p>
                </div>

                <div className="flex flex-col items-end text-right bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
                  <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold mb-1">
                    <Cpu className="w-4 h-4" />
                    <span>Strands Agent Triage</span>
                  </div>
                  <div className="text-xs text-slate-400">
                    Estimated Carbon Offset:{' '}
                    <span className="font-bold text-white">
                      {proposal.estimated_carbon_saved_kg} kg CO₂e
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Tools Executed: distance, cargo_fit, equity_balance
                  </div>
                </div>
              </div>

              {/* Rationale & Candidates Grid */}
              <div className="py-5 grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Primary Pick (Recommended) */}
                <div className="lg:col-span-7 bg-emerald-950/20 border-2 border-emerald-500/50 rounded-xl p-5 relative">
                  <div className="absolute -top-3 left-4 bg-emerald-500 text-slate-950 text-[11px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full shadow-md">
                    ★ Primary AI Recommendation
                  </div>

                  <div className="flex items-start justify-between mt-1">
                    <div>
                      <h4 className="text-lg font-bold text-white flex items-center gap-2">
                        {primary.name}
                        <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-normal">
                          {primary.vehicle_type.replace('_', ' ')}
                        </span>
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {primary.has_cooler
                          ? '✓ Cooler equipped for cold-chain'
                          : 'No cooler equipment'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-black text-emerald-400">
                        {primary.match_score}
                        <span className="text-xs font-normal text-slate-400">/100</span>
                      </div>
                      <span className="text-[10px] uppercase font-bold text-emerald-300">
                        Match Score
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 my-3 text-xs">
                    <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[11px]">Proximity / ETA</div>
                      <div className="font-bold text-white flex items-center gap-1 mt-0.5">
                        <Navigation className="w-3 h-3 text-emerald-400" />
                        {primary.estimated_eta_minutes} min ({primary.distance_miles} mi)
                      </div>
                    </div>
                    <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[11px]">Weekly Shifts</div>
                      <div className="font-bold text-white mt-0.5">
                        {primary.weekly_shifts} shifts (fatigue low)
                      </div>
                    </div>
                    <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800 col-span-2 sm:col-span-1">
                      <div className="text-slate-400 text-[11px]">Suitability</div>
                      <div className="font-bold text-emerald-400 flex items-center gap-1 mt-0.5">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Safe & Verified
                      </div>
                    </div>
                  </div>

                  <div className="text-xs text-slate-300 bg-slate-950/70 p-3 rounded-lg border border-slate-800/80">
                    <span className="font-semibold text-emerald-300">Why Primary Pick: </span>
                    {proposal.agent_reasoning}
                  </div>
                </div>

                {/* Alternative Pick */}
                <div className="lg:col-span-5 bg-slate-950/40 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                      <ArrowRightLeft className="w-3.5 h-3.5" />
                      Alternative Candidate
                    </div>

                    {alt ? (
                      <div>
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="text-base font-bold text-slate-200">
                              {alt.name}
                            </h4>
                            <span className="text-[11px] text-slate-400">
                              {alt.vehicle_type.replace('_', ' ')} • {alt.estimated_eta_minutes} min ETA ({alt.distance_miles} mi)
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-base font-bold text-slate-300">
                              {alt.match_score}
                            </span>
                            <span className="text-xs text-slate-500">/100</span>
                          </div>
                        </div>

                        <div className="mt-3 text-xs text-slate-400 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                          {alt.weekly_shifts >= 2 ? (
                            <span className="text-amber-300">
                              Notice: Has already completed {alt.weekly_shifts} shifts this week.
                            </span>
                          ) : (
                            <span>Viable backup candidate available for immediate dispatch.</span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs text-slate-500 py-6 text-center">
                        No secondary driver meets distance & cargo thresholds.
                      </div>
                    )}
                  </div>

                  {/* Trade-off summary */}
                  <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 italic">
                    <span className="font-semibold text-slate-300 not-italic">Trade-off: </span>
                    {proposal.tradeoff_summary}
                  </div>
                </div>
              </div>

              {/* Human-in-the-Loop Action Bar */}
              <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                <div className="text-xs text-slate-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>
                    Coordinator authorization confirms automated SMS notification to driver with pickup code.
                  </span>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto flex-wrap">
                  <button
                    onClick={() => onReject(proposal.id, 'No volunteers ready')}
                    className="px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-red-400 hover:bg-red-500/10 border border-slate-800 transition-all cursor-pointer flex items-center gap-1"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Decline</span>
                  </button>

                  {alt && (
                    <button
                      onClick={() => onOverrideAlternative(proposal.id)}
                      disabled={isApproving}
                      className="px-3.5 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all cursor-pointer flex items-center gap-1 disabled:opacity-50"
                    >
                      <ArrowRightLeft className="w-3.5 h-3.5 text-amber-400" />
                      <span>Switch to {alt.name.split(' ')[0]}</span>
                    </button>
                  )}

                  <button
                    onClick={() => onApprove(proposal.id)}
                    disabled={isApproving}
                    className="px-5 py-2.5 rounded-lg text-xs font-bold text-slate-950 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 shadow-lg shadow-emerald-500/20 transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve Dispatch: {primary.name}</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
