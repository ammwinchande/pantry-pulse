import React, { useState } from 'react';
import {
  HeartHandshake,
  Send,
  ThermometerSnowflake,
  ShieldAlert,
  CheckCircle2,
} from 'lucide-react';
import type { FoodCategory, DonationAlert } from '../types';

interface DonorSurplusViewProps {
  onSimulateCustom: (alert: Partial<DonationAlert>) => void;
  isSubmitting: boolean;
}

export const DonorSurplusView: React.FC<DonorSurplusViewProps> = ({
  onSimulateCustom,
  isSubmitting,
}) => {
  const [donorName, setDonorName] = useState('Pike Place Organic Market');
  const [contactName, setContactName] = useState('Alex Baker');
  const [phone, setPhone] = useState('+1 (206) 555-4921');
  const [address, setAddress] = useState('1500 Pike Pl, Seattle, WA');
  const [neighborhood, setNeighborhood] = useState('Downtown');
  const [category, setCategory] = useState<FoodCategory>('BAKERY_DRY');
  const [description, setDescription] = useState('40 boxes fresh artisan breads, bagels, and breakfast pastries');
  const [weight, setWeight] = useState(80);
  const [boxes, setBoxes] = useState(4);
  const [coldChain, setColdChain] = useState(false);
  const [fragile, setFragile] = useState(false);
  const [minutes, setMinutes] = useState(60);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const now = new Date();
    const deadline = new Date(now.getTime() + minutes * 60000);

    onSimulateCustom({
      donor_name: donorName,
      donor_contact_name: contactName,
      donor_phone: phone,
      donor_address: {
        latitude: 47.609,
        longitude: -122.342,
        address,
        neighborhood,
      },
      food_category: category,
      item_description: description,
      estimated_weight_lbs: weight,
      box_count: boxes,
      requires_cold_chain: coldChain,
      is_fragile: fragile,
      pickup_deadline: deadline.toISOString(),
      status: 'REPORTED',
    });

    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 4000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <HeartHandshake className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white mb-0.5">
              Food Donor Partner Express Portal
            </h3>
            <p className="text-xs text-slate-400">
              Report food surplus in under 30 seconds. The Strands Agent immediately alerts nearby volunteers and provides a 4-digit custody verification code.
            </p>
          </div>
        </div>
      </div>

      {submitted && (
        <div className="bg-emerald-950/40 border border-emerald-500/50 rounded-xl p-4 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            Surplus alert broadcast! Strands Agent is currently matching qualified volunteer drivers.
          </span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h4 className="text-base font-bold text-white mb-2">Emergency Food Rescue Request</h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Donor Organization Name
            </label>
            <input
              type="text"
              required
              value={donorName}
              onChange={(e) => setDonorName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Contact Person & Phone
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                required
                value={contactName}
                onChange={(e) => setContactName(e.target.value)}
                className="w-1/2 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
              <input
                type="text"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-1/2 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2">
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Pickup Address & Instructions
            </label>
            <input
              type="text"
              required
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Neighborhood District
            </label>
            <input
              type="text"
              required
              value={neighborhood}
              onChange={(e) => setNeighborhood(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-1">
            Food Category
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {(['BAKERY_DRY', 'PRODUCE', 'PREPARED_MEALS', 'DAIRY_FROZEN'] as FoodCategory[]).map((cat) => (
              <button
                type="button"
                key={cat}
                onClick={() => {
                  setCategory(cat);
                  if (cat === 'DAIRY_FROZEN') setColdChain(true);
                }}
                className={`text-xs py-2 px-3 rounded-lg border font-medium transition-all ${
                  category === cat
                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-bold'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-1">
            Item Description
          </label>
          <textarea
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Estimated Weight (lbs)
            </label>
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(parseInt(e.target.value, 10) || 0)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Box / Crate Count
            </label>
            <input
              type="number"
              value={boxes}
              onChange={(e) => setBoxes(parseInt(e.target.value, 10) || 0)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Pickup Window (Minutes)
            </label>
            <select
              value={minutes}
              onChange={(e) => setMinutes(parseInt(e.target.value, 10))}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value={45}>45 Minutes (Urgent)</option>
              <option value={60}>60 Minutes (Standard)</option>
              <option value={90}>90 Minutes</option>
              <option value={120}>2 Hours</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-6 pt-2">
          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
            <input
              type="checkbox"
              checked={coldChain}
              onChange={(e) => setColdChain(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-emerald-500 focus:ring-0"
            />
            <span className="flex items-center gap-1">
              <ThermometerSnowflake className="w-3.5 h-3.5 text-cyan-400" />
              Requires Insulated Cold Chain
            </span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
            <input
              type="checkbox"
              checked={fragile}
              onChange={(e) => setFragile(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-emerald-500 focus:ring-0"
            />
            <span className="flex items-center gap-1">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              Fragile (Needs Flat Cargo Bed)
            </span>
          </label>
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 text-slate-950 font-bold text-xs px-6 py-2.5 rounded-lg shadow-md cursor-pointer flex items-center gap-2 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span>Submit Surplus Alert to AI Agent</span>
          </button>
        </div>
      </form>
    </div>
  );
};
