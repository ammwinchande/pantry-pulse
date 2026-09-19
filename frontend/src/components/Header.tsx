import React from 'react';
import {
  HeartHandshake,
  Sparkles,
  Truck,
  Apple,
  Scale,
  Leaf,
  PlusCircle,
  Radio,
  UserCheck,
  LogOut,
} from 'lucide-react';
import type { SystemStats, UserRole, AuthUser } from '../types';

interface HeaderProps {
  stats?: SystemStats;
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  onSimulate: () => void;
  isSimulating: boolean;
  user?: AuthUser | null;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  stats,
  currentRole,
  onRoleChange,
  onSimulate,
  isSimulating,
  user,
  onLogout,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 px-4 py-1.5 text-xs font-medium text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="bg-white/20 px-2 py-0.5 rounded-full text-[11px] font-bold tracking-wide uppercase">
            Good Neighbor Track
          </span>
          <span>Agents for Humans Hackathon • Built with AWS Strands Agents SDK</span>
        </div>
        <div className="flex items-center gap-2 text-emerald-100">
          <Radio className="w-3.5 h-3.5 text-emerald-300 animate-pulse" />
          <span>Strands Agent Active • Background Autonomous Loop Running</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white">
              <HeartHandshake className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-black tracking-tight text-white m-0">PantryPulse</h1>
                <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold px-2 py-0.5 rounded-md">
                  v1.0 Strands AI
                </span>
              </div>
              <p className="text-xs text-slate-400 m-0">
                Autonomous Community Food Rescue & Volunteer Dispatch Agent
              </p>
            </div>
          </div>

          {/* Quick Metrics */}
          {stats && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-left">
              <div className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                  <Scale className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Rescued</span>
                </div>
                <div className="text-base font-bold text-white">
                  {stats.total_rescued_lbs.toLocaleString()} <span className="text-xs font-normal text-slate-400">lbs</span>
                </div>
              </div>

              <div className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                  <Apple className="w-3.5 h-3.5 text-amber-400" />
                  <span>Meals</span>
                </div>
                <div className="text-base font-bold text-white">
                  {stats.meals_provided.toLocaleString()}
                </div>
              </div>

              <div className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                  <Leaf className="w-3.5 h-3.5 text-teal-400" />
                  <span>CO₂ Offset</span>
                </div>
                <div className="text-base font-bold text-white">
                  {stats.carbon_offset_kg.toLocaleString()} <span className="text-xs font-normal text-slate-400">kg</span>
                </div>
              </div>

              <div className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                  <Truck className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Fleet Ready</span>
                </div>
                <div className="text-base font-bold text-white">
                  {stats.active_volunteers} <span className="text-xs font-normal text-slate-400">drivers</span>
                </div>
              </div>
            </div>
          )}

          {/* Action Trigger + Account */}
          <div className="flex items-center gap-2">
            {user && (
              <div className="hidden sm:flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 rounded-lg pl-2.5 pr-1.5 py-1.5">
                <div className="w-7 h-7 rounded-md bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white text-[11px] font-bold">
                  {user.name?.[0]?.toUpperCase() ?? '?'}
                </div>
                <div className="text-left leading-tight">
                  <div className="text-xs font-semibold text-white max-w-[140px] truncate">
                    {user.name}
                  </div>
                  <div className="text-[10px] text-slate-400 max-w-[140px] truncate">
                    {user.role}
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  title="Sign out"
                  className="ml-1 p-1.5 rounded-md text-slate-400 hover:text-rose-400 hover:bg-slate-700/60 transition cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            )}
            <button
              onClick={onSimulate}
              disabled={isSimulating}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-semibold px-3.5 py-2.5 rounded-lg shadow-md shadow-emerald-600/30 transition-all cursor-pointer disabled:opacity-50"
            >
              <PlusCircle className={`w-4 h-4 ${isSimulating ? 'animate-spin' : ''}`} />
              <span>{isSimulating ? 'Analyzing with Strands...' : 'Simulate Surplus Alert'}</span>
            </button>
          </div>
        </div>

        {/* Persona Navigation Tabs */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => onRoleChange('COORDINATOR')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-1.5 ${currentRole === 'COORDINATOR'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Coordinator Mission Control</span>
              {stats && stats.pending_decisions_count > 0 && (
                <span className="bg-amber-400 text-slate-950 font-bold px-1.5 py-0.2 rounded-full text-[10px] ml-1">
                  {stats.pending_decisions_count}
                </span>
              )}
            </button>

            <button
              onClick={() => onRoleChange('VOLUNTEER')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-1.5 ${currentRole === 'VOLUNTEER'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              <Truck className="w-3.5 h-3.5" />
              <span>Volunteer Driver View</span>
            </button>

            <button
              onClick={() => onRoleChange('INTAKE_WORKER')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-1.5 ${currentRole === 'INTAKE_WORKER'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Dock Intake Staff</span>
            </button>

            <button
              onClick={() => onRoleChange('DONOR')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-1.5 ${currentRole === 'DONOR'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              <HeartHandshake className="w-3.5 h-3.5" />
              <span>Food Donor Partner</span>
            </button>
          </div>

          <div className="text-xs text-slate-400 hidden lg:flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Live Sync Active</span>
          </div>
        </div>
      </div>
    </header>
  );
};
