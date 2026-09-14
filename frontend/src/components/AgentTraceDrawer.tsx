import React, { useState } from 'react';
import { Terminal, Cpu, Clock, ChevronDown, ChevronUp, Check, Activity } from 'lucide-react';
import type { AgentTraceLog } from '../types';

interface AgentTraceDrawerProps {
  traces: AgentTraceLog[];
}

export const AgentTraceDrawer: React.FC<AgentTraceDrawerProps> = ({ traces }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-md">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-3.5 bg-slate-950/80 hover:bg-slate-900 border-b border-slate-800 flex items-center justify-between transition-all cursor-pointer text-left"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-bold text-white">
            Strands Agents SDK • Live Reasoning & Observability Trace
          </span>
          <span className="text-xs bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
            OpenTelemetry & @tool Traces
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">{traces.length} steps logged</span>
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 bg-slate-950/95 font-mono text-xs max-h-72 overflow-y-auto space-y-2">
          {traces.length === 0 ? (
            <div className="text-slate-500 text-center py-6">
              No traces yet. Click "Simulate Surplus Alert" to observe the agent loop.
            </div>
          ) : (
            traces.map((trace, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:border-slate-700 transition-all"
              >
                <div className="flex items-start sm:items-center gap-2">
                  <span className="text-[10px] text-slate-500 shrink-0">
                    {new Date(trace.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })}
                  </span>

                  {trace.event === 'TOOL_CALL' ? (
                    <span className="bg-purple-950/60 text-purple-300 border border-purple-800/50 px-1.5 py-0.5 rounded text-[10px] font-semibold shrink-0 flex items-center gap-1">
                      <Cpu className="w-3 h-3 text-purple-400" />
                      @tool {trace.tool_called}
                    </span>
                  ) : trace.event === 'PROPOSAL_GENERATED' ? (
                    <span className="bg-emerald-950/60 text-emerald-300 border border-emerald-800/50 px-1.5 py-0.5 rounded text-[10px] font-semibold shrink-0 flex items-center gap-1">
                      <Check className="w-3 h-3 text-emerald-400" />
                      PROPOSAL_READY
                    </span>
                  ) : (
                    <span className="bg-blue-950/60 text-blue-300 border border-blue-800/50 px-1.5 py-0.5 rounded text-[10px] font-semibold shrink-0 flex items-center gap-1">
                      <Activity className="w-3 h-3 text-blue-400" />
                      {trace.event}
                    </span>
                  )}

                  <span className="text-slate-300 break-words">{trace.output_summary}</span>
                </div>

                {trace.duration_ms !== undefined && trace.duration_ms !== null && (
                  <div className="text-[11px] text-slate-400 font-semibold shrink-0 flex items-center gap-1 self-end sm:self-auto">
                    <Clock className="w-3 h-3 text-slate-500" />
                    <span>{trace.duration_ms}ms</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
