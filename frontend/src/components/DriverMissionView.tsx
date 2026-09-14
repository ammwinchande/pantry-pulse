import React, { useState } from 'react';
import {
  Truck,
  MapPin,
  KeyRound,
  CheckCircle,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react';
import type { Dispatch, Volunteer } from '../types';

interface DriverMissionViewProps {
  dispatches: Dispatch[];
  volunteers: Volunteer[];
  onConfirmPickup: (dispatchId: string, code: string) => void;
  onConfirmDelivery: (dispatchId: string) => void;
}

export const DriverMissionView: React.FC<DriverMissionViewProps> = ({
  dispatches,
  volunteers,
  onConfirmPickup,
  onConfirmDelivery,
}) => {
  const [selectedDriverId, setSelectedDriverId] = useState<string>(
    volunteers[0]?.id || 'vol-01'
  );
  const [inputCode, setInputCode] = useState<string>('');

  const currentDriver = volunteers.find((v) => v.id === selectedDriverId) || volunteers[0];
  const driverDispatches = dispatches.filter(
    (d) => d.volunteer_id === selectedDriverId && d.status !== 'DELIVERED'
  );
  const completedDispatches = dispatches.filter(
    (d) => d.volunteer_id === selectedDriverId && d.status === 'DELIVERED'
  );

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Driver Selector Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <img
            src={
              currentDriver?.avatar_url ||
              `https://api.dicebear.com/7.x/bottts/svg?seed=${currentDriver?.id}`
            }
            alt={currentDriver?.name}
            className="w-12 h-12 rounded-full border border-emerald-500/50"
          />
          <div>
            <h3 className="text-base font-bold text-white">{currentDriver?.name}</h3>
            <p className="text-xs text-slate-400">
              {currentDriver?.vehicle_type.replace('_', ' ')} • {currentDriver?.weekly_shifts_completed} shifts completed this week
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          <label className="text-xs text-slate-400">Switch Persona:</label>
          <select
            value={selectedDriverId}
            onChange={(e) => setSelectedDriverId(e.target.value)}
            className="bg-slate-950 text-white text-xs border border-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            {volunteers.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name} ({v.vehicle_type.replace('_', ' ')})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Active Missions */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Truck className="w-5 h-5 text-emerald-400" />
            <span>Active Assigned Missions ({driverDispatches.length})</span>
          </h3>
          <span className="text-xs text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-800/50">
            Live Turn-by-Turn View
          </span>
        </div>

        {driverDispatches.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center">
            <CheckCircle className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <p className="text-sm text-slate-300 font-semibold">No pending pickups for {currentDriver?.name}</p>
            <p className="text-xs text-slate-500 mt-1">
              When the coordinator approves a rescue dispatch, it will appear here instantly with turn-by-turn routing and the 4-digit pickup code.
            </p>
          </div>
        ) : (
          driverDispatches.map((disp) => (
            <div
              key={disp.id}
              className="bg-slate-900/90 border-2 border-emerald-500/50 rounded-2xl p-6 shadow-xl space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-bold px-2 py-0.5 rounded uppercase">
                    Status: {disp.status}
                  </span>
                  <h4 className="text-xl font-black text-white mt-1">{disp.donor_name}</h4>
                  <p className="text-sm text-slate-300 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{disp.donor_address}</span>
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-black text-emerald-400">
                    {disp.weight_rescued_lbs} <span className="text-xs font-normal text-slate-400">lbs</span>
                  </span>
                  <div className="text-xs text-slate-400">Cargo Weight</div>
                </div>
              </div>

              {/* Secure Pickup Verification Code */}
              <div className="bg-emerald-950/30 border border-emerald-500/40 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-mono text-lg font-bold">
                    <KeyRound className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs text-emerald-300 font-semibold">
                      Donor Pickup Verification Code
                    </div>
                    <div className="text-xs text-slate-400">
                      Present to donor staff upon arrival to verify custody
                    </div>
                  </div>
                </div>
                <div className="text-3xl font-mono font-black text-emerald-400 tracking-widest bg-slate-950 px-4 py-1.5 rounded-lg border border-emerald-500/30">
                  {disp.pickup_verification_code}
                </div>
              </div>

              {/* Delivery destination */}
              <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
                <div>
                  <span className="text-slate-500 block text-[11px]">Final Destination</span>
                  <span className="font-semibold text-white">{disp.pantry_address}</span>
                </div>
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                    disp.donor_address
                  )}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Open Maps
                </a>
              </div>

              {/* Mission Progress Action */}
              <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                {disp.status === 'APPROVED' ? (
                  <div className="flex items-center gap-2 w-full">
                    <input
                      type="text"
                      placeholder="Enter verification code..."
                      value={inputCode}
                      onChange={(e) => setInputCode(e.target.value)}
                      className="bg-slate-950 text-white text-xs border border-slate-700 rounded-lg px-3 py-2.5 flex-1 focus:outline-none focus:border-emerald-500 font-mono text-center tracking-wider"
                    />
                    <button
                      onClick={() => {
                        onConfirmPickup(disp.id, inputCode);
                        setInputCode('');
                      }}
                      disabled={!inputCode.trim()}
                      className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 text-slate-950 font-bold text-xs px-4 py-2.5 rounded-lg shadow-md cursor-pointer whitespace-nowrap"
                    >
                      Confirm Food Picked Up
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => onConfirmDelivery(disp.id)}
                    className="w-full bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 text-slate-950 font-bold text-xs px-4 py-2.5 rounded-lg shadow-md cursor-pointer flex items-center justify-center gap-1.5"
                  >
                    <ShieldCheck className="w-4 h-4" />
                    <span>Confirm Delivery at Food Pantry Dock</span>
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Completed Missions History */}
      {completedDispatches.length > 0 && (
        <div className="pt-4 border-t border-slate-800">
          <h4 className="text-sm font-bold text-slate-400 mb-3">Completed Today by {currentDriver?.name}</h4>
          <div className="space-y-2">
            {completedDispatches.map((cd) => (
              <div
                key={cd.id}
                className="bg-slate-950/40 border border-slate-800 rounded-xl p-3 flex items-center justify-between text-xs"
              >
                <div>
                  <span className="font-semibold text-white">{cd.donor_name}</span>
                  <span className="text-slate-500 ml-2">Code: {cd.pickup_verification_code}</span>
                </div>
                <div className="text-emerald-400 font-bold">
                  +{cd.weight_rescued_lbs} lbs Rescued
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
