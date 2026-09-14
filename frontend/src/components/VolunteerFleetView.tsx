import React from 'react';
import {
  Truck,
  Car,
  Bike,
  Snowflake,
  Star,
  Clock,
  Power,
} from 'lucide-react';
import type { Volunteer, VehicleType } from '../types';

interface VolunteerFleetViewProps {
  volunteers: Volunteer[];
  onToggleAvailability: (volunteerId: string, isAvailable: boolean) => void;
}

export const VolunteerFleetView: React.FC<VolunteerFleetViewProps> = ({
  volunteers,
  onToggleAvailability,
}) => {
  const getVehicleIcon = (type: VehicleType) => {
    switch (type) {
      case 'VAN_TRUCK':
        return <Truck className="w-4 h-4 text-amber-400" />;
      case 'BICYCLE_CARGO':
        return <Bike className="w-4 h-4 text-emerald-400" />;
      default:
        return <Car className="w-4 h-4 text-cyan-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return (
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Available
          </span>
        );
      case 'DISPATCHED':
        return (
          <span className="bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Dispatched
          </span>
        );
      case 'EN_ROUTE':
        return (
          <span className="bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
            <Truck className="w-3 h-3" />
            En Route
          </span>
        );
      default:
        return (
          <span className="bg-slate-800 text-slate-400 text-[11px] font-semibold px-2 py-0.5 rounded-full">
            Off Duty
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white mb-0.5">Volunteer Driver Fleet</h3>
          <p className="text-xs text-slate-400">
            Real-time tracking of community volunteers, cargo capacities, and weekly shift balancing.
          </p>
        </div>
        <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
          {volunteers.filter((v) => v.status === 'AVAILABLE').length} of {volunteers.length} Ready
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {volunteers.map((vol) => (
          <div
            key={vol.id}
            className="bg-slate-950/70 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-3">
                <img
                  src={
                    vol.avatar_url ||
                    `https://api.dicebear.com/7.x/bottts/svg?seed=${vol.id}`
                  }
                  alt={vol.name}
                  className="w-10 h-10 rounded-full object-cover border border-slate-700"
                />
                <div>
                  <h4 className="text-sm font-bold text-white">{vol.name}</h4>
                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    {getVehicleIcon(vol.vehicle_type)}
                    <span>{vol.vehicle_type.replace('_', ' ')}</span>
                  </div>
                </div>
              </div>
              {getStatusBadge(vol.status)}
            </div>

            <div className="mt-3 pt-3 border-t border-slate-900 grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-[11px] text-slate-500">Location</span>
                <p className="font-medium text-slate-300 truncate">
                  {vol.current_location.neighborhood || 'Central Seattle'}
                </p>
              </div>
              <div>
                <span className="text-[11px] text-slate-500">Capacity</span>
                <p className="font-medium text-slate-300">{vol.cargo_capacity_lbs} lbs max</p>
              </div>
            </div>

            <div className="mt-2.5 flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-2">
                {vol.has_cooler && (
                  <span className="inline-flex items-center gap-1 text-[11px] text-cyan-400 bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                    <Snowflake className="w-3 h-3" />
                    Cooler
                  </span>
                )}
                <span className="text-[11px] text-slate-400">
                  {vol.weekly_shifts_completed} shifts this wk
                </span>
              </div>
              <div className="flex items-center gap-1 text-amber-400 text-xs font-semibold">
                <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                <span>{vol.rating}</span>
              </div>
            </div>

            {/* Availability Toggle */}
            <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">Shift Availability</span>
              <button
                onClick={() => onToggleAvailability(vol.id, vol.status !== 'AVAILABLE')}
                className={`text-[11px] font-semibold px-2 py-1 rounded transition-all cursor-pointer flex items-center gap-1 ${
                  vol.status === 'AVAILABLE'
                    ? 'text-red-400 bg-red-950/20 hover:bg-red-900/30'
                    : 'text-emerald-400 bg-emerald-950/20 hover:bg-emerald-900/30'
                }`}
              >
                <Power className="w-3 h-3" />
                <span>{vol.status === 'AVAILABLE' ? 'Set Off Duty' : 'Set Available'}</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
