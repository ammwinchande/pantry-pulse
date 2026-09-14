import React from 'react';
import {
  Clock,
  CheckCircle,
  Truck,
  Flame,
  ThermometerSnowflake,
} from 'lucide-react';
import type { DonationAlert, FoodCategory } from '../types';

interface LiveSurplusFeedProps {
  donations: DonationAlert[];
}

export const LiveSurplusFeed: React.FC<LiveSurplusFeedProps> = ({ donations }) => {
  const getCategoryBadge = (cat: FoodCategory) => {
    switch (cat) {
      case 'BAKERY_DRY':
        return <span className="bg-amber-950/40 text-amber-300 border border-amber-800/40 px-2 py-0.5 rounded text-[11px] font-medium">Bakery & Dry</span>;
      case 'PRODUCE':
        return <span className="bg-emerald-950/40 text-emerald-300 border border-emerald-800/40 px-2 py-0.5 rounded text-[11px] font-medium">Fresh Produce</span>;
      case 'PREPARED_MEALS':
        return <span className="bg-purple-950/40 text-purple-300 border border-purple-800/40 px-2 py-0.5 rounded text-[11px] font-medium">Prepared Meals</span>;
      case 'DAIRY_FROZEN':
        return <span className="bg-cyan-950/40 text-cyan-300 border border-cyan-800/40 px-2 py-0.5 rounded text-[11px] font-medium">Dairy & Frozen</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold px-2 py-0.5 rounded flex items-center gap-1">
            <CheckCircle className="w-3 h-3" /> Rescued
          </span>
        );
      case 'IN_TRANSIT':
        return (
          <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-[11px] font-semibold px-2 py-0.5 rounded flex items-center gap-1">
            <Truck className="w-3 h-3" /> In Transit
          </span>
        );
      case 'DISPATCHED':
        return (
          <span className="bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[11px] font-semibold px-2 py-0.5 rounded flex items-center gap-1">
            <Clock className="w-3 h-3" /> Driver Dispatched
          </span>
        );
      case 'PENDING_DECISION':
        return (
          <span className="bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px] font-semibold px-2 py-0.5 rounded flex items-center gap-1">
            <Flame className="w-3 h-3" /> Decision Gate
          </span>
        );
      case 'ANALYZING':
        return (
          <span className="bg-purple-500/10 text-purple-300 border border-purple-500/30 text-[11px] font-semibold px-2 py-0.5 rounded animate-pulse">
            Strands Triage...
          </span>
        );
      default:
        return (
          <span className="bg-slate-800 text-slate-400 text-[11px] px-2 py-0.5 rounded">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white mb-0.5">Live Food Rescue Alerts</h3>
          <p className="text-xs text-slate-400">
            Emergency surplus alerts received from supermarkets, bakeries, and catered venues.
          </p>
        </div>
        <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
          {donations.length} Tracked
        </span>
      </div>

      <div className="space-y-3">
        {donations.map((don) => (
          <div
            key={don.id}
            className="bg-slate-950/70 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-bold text-white">{don.donor_name}</span>
                {getCategoryBadge(don.food_category)}
                {don.requires_cold_chain && (
                  <span className="bg-cyan-950/60 text-cyan-300 border border-cyan-800 text-[10px] font-bold px-1.5 py-0.5 rounded flex items-center gap-0.5">
                    <ThermometerSnowflake className="w-3 h-3" /> Cold Chain
                  </span>
                )}
                {getStatusBadge(don.status)}
              </div>

              <p className="text-xs text-slate-300">
                <span className="font-semibold text-emerald-400">{don.estimated_weight_lbs} lbs</span>{' '}
                • {don.item_description} ({don.box_count} crates)
              </p>

              <div className="text-[11px] text-slate-500 flex items-center gap-4 flex-wrap">
                <span>📍 {don.donor_address.address}, {don.donor_address.neighborhood}</span>
                <span>Contact: {don.donor_contact_name} ({don.donor_phone})</span>
              </div>
            </div>

            <div className="text-right md:min-w-[120px] shrink-0 border-t md:border-t-0 pt-2 md:pt-0 border-slate-900">
              <div className="text-xs font-semibold text-slate-300">Pickup Deadline</div>
              <div className="text-xs text-amber-400 font-mono flex items-center md:justify-end gap-1 mt-0.5">
                <Clock className="w-3 h-3" />
                <span>
                  {new Date(don.pickup_deadline).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
