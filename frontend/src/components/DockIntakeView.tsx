import React, { useState } from 'react';
import {
  Scale,
  CheckCircle2,
  Truck,
  ClipboardCheck,
  ShieldCheck,
} from 'lucide-react';
import type { Dispatch } from '../types';

interface DockIntakeViewProps {
  dispatches: Dispatch[];
  onConfirmDelivery: (dispatchId: string, weight?: number) => void;
}

export const DockIntakeView: React.FC<DockIntakeViewProps> = ({
  dispatches,
  onConfirmDelivery,
}) => {
  const [scaleWeights, setScaleWeights] = useState<Record<string, number>>({});

  const incomingDeliveries = dispatches.filter((d) => d.status === 'PICKED_UP');
  const pastDeliveries = dispatches.filter((d) => d.status === 'DELIVERED');

  const handleWeightChange = (dispatchId: string, value: string) => {
    const num = parseInt(value, 10);
    setScaleWeights((prev) => ({
      ...prev,
      [dispatchId]: isNaN(num) ? 0 : num,
    }));
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-0.5">
                Pantry Loading Dock Intake
              </h3>
              <p className="text-xs text-slate-400">
                Inspect arriving food donations, verify weights on scale, and record into community inventory.
              </p>
            </div>
          </div>
          <span className="text-xs font-bold px-3 py-1 bg-teal-500/10 text-teal-300 border border-teal-500/30 rounded-full">
            Dock Station #1 Active
          </span>
        </div>
      </div>

      {/* Arriving Shipments */}
      <div className="space-y-4">
        <h4 className="text-base font-bold text-white flex items-center gap-2">
          <Truck className="w-4 h-4 text-cyan-400" />
          <span>Arriving Vehicles / In Transit ({incomingDeliveries.length})</span>
        </h4>

        {incomingDeliveries.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="text-sm text-slate-300 font-semibold">No vehicles currently en route to dock</p>
            <p className="text-xs text-slate-500 mt-1">
              When drivers confirm food pickup from donors, their arrival manifest will appear here for dock verification.
            </p>
          </div>
        ) : (
          incomingDeliveries.map((disp) => {
            const currentWeight = scaleWeights[disp.id] ?? disp.weight_rescued_lbs;

            return (
              <div
                key={disp.id}
                className="bg-slate-900/90 border-2 border-teal-500/50 rounded-2xl p-6 shadow-lg space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
                  <div>
                    <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-[11px] font-bold px-2 py-0.5 rounded uppercase">
                      Driver: {disp.volunteer_name}
                    </span>
                    <h5 className="text-lg font-bold text-white mt-1">{disp.donor_name}</h5>
                    <p className="text-xs text-slate-400">
                      Donor Location: {disp.donor_address}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono text-slate-400">
                      Code: <span className="text-emerald-400 font-bold">{disp.pickup_verification_code}</span>
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-500 block text-[11px]">Donor Manifest Weight</span>
                    <span className="text-base font-bold text-white">{disp.weight_rescued_lbs} lbs</span>
                  </div>

                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-500 block text-[11px]">Scale Verified Weight</span>
                    <div className="flex items-center gap-1.5 mt-1">
                      <input
                        type="number"
                        value={currentWeight}
                        onChange={(e) => handleWeightChange(disp.id, e.target.value)}
                        className="w-20 bg-slate-900 text-white border border-slate-700 rounded px-2 py-1 text-sm font-bold text-center focus:outline-none focus:border-teal-500"
                      />
                      <span className="text-slate-400 font-medium">lbs</span>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex flex-col justify-center">
                    <span className="text-slate-500 block text-[11px]">Food Safety Status</span>
                    <span className="text-emerald-400 font-bold flex items-center gap-1 mt-0.5">
                      <ShieldCheck className="w-4 h-4" /> Passed Inspection
                    </span>
                  </div>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    onClick={() => onConfirmDelivery(disp.id, currentWeight)}
                    className="bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 text-slate-950 font-bold text-xs px-5 py-2.5 rounded-lg shadow-md cursor-pointer flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Confirm & Receive into Pantry Inventory</span>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Dock History */}
      {pastDeliveries.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
          <h4 className="text-base font-bold text-white mb-3 flex items-center gap-2">
            <ClipboardCheck className="w-4 h-4 text-emerald-400" />
            <span>Recent Dock Receiving Log</span>
          </h4>
          <div className="divide-y divide-slate-800">
            {pastDeliveries.map((pd) => (
              <div key={pd.id} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-white">{pd.donor_name}</span>
                  <span className="text-slate-400 ml-2">Delivered by {pd.volunteer_name}</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-emerald-400">+{pd.weight_rescued_lbs} lbs</span>
                  <div className="text-[11px] text-slate-500">
                    {pd.delivered_at
                      ? new Date(pd.delivered_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })
                      : 'Received'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
