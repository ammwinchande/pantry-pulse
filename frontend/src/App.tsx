import React, { useState } from 'react';
import { QueryClient, QueryClientProvider, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  useStats,
  useDonations,
  usePendingDecisions,
  useDispatches,
  useVolunteers,
  useAgentTraces,
  useSimulateAlert,
  useApproveDecision,
  useOverrideAlternative,
  useRejectDecision,
  useConfirmPickup,
  useConfirmDelivery,
  useToggleAvailability,
} from './api/usePantry';
import { AuthProvider, useAuth } from './api/useAuth';
import { fetchApi } from './api/client';
import type { UserRole, DonationAlert } from './types';
import { Header } from './components/Header';
import { AuthView } from './components/AuthView';
import { DecisionGate } from './components/DecisionGate';
import { LiveSurplusFeed } from './components/LiveSurplusFeed';
import { VolunteerFleetView } from './components/VolunteerFleetView';
import { AgentTraceDrawer } from './components/AgentTraceDrawer';
import { DriverMissionView } from './components/DriverMissionView';
import { DockIntakeView } from './components/DockIntakeView';
import { DonorSurplusView } from './components/DonorSurplusView';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000,
      retry: 2,
    },
  },
});

const DashboardContent: React.FC = () => {
  const [role, setRole] = useState<UserRole>('COORDINATOR');
  const { user, logout } = useAuth();

  // TanStack Queries
  const { data: stats } = useStats();
  const { data: donations = [] } = useDonations();
  const { data: pendingDecisions = [] } = usePendingDecisions();
  const { data: dispatches = [] } = useDispatches();
  const { data: volunteers = [] } = useVolunteers();
  const { data: traces = [] } = useAgentTraces();

  // Mutations
  const simulateMutation = useSimulateAlert();
  const approveMutation = useApproveDecision();
  const overrideAltMutation = useOverrideAlternative();
  const rejectMutation = useRejectDecision();
  const pickupMutation = useConfirmPickup();
  const deliveryMutation = useConfirmDelivery();
  const toggleAvailMutation = useToggleAvailability();

  const qc = useQueryClient();
  const customDonationMutation = useMutation({
    mutationFn: (alert: Partial<DonationAlert>) =>
      fetchApi('/donations', {
        method: 'POST',
        body: JSON.stringify(alert),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pendingDecisions'] });
      qc.invalidateQueries({ queryKey: ['donations'] });
      qc.invalidateQueries({ queryKey: ['stats'] });
      qc.invalidateQueries({ queryKey: ['agentTraces'] });
    },
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header
        stats={stats}
        currentRole={role}
        onRoleChange={setRole}
        onSimulate={() => simulateMutation.mutate()}
        isSimulating={simulateMutation.isPending}
        user={user}
        onLogout={logout}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {role === 'COORDINATOR' && (
          <div className="space-y-8">
            {/* The Core Magic: Human-in-the-Loop Decision Gate */}
            <DecisionGate
              proposals={pendingDecisions}
              donations={donations}
              onApprove={(id) => approveMutation.mutate(id)}
              onOverrideAlternative={(id) => overrideAltMutation.mutate(id)}
              onReject={(id, reason) => rejectMutation.mutate({ proposalId: id, reason })}
              isApproving={approveMutation.isPending || overrideAltMutation.isPending}
            />

            {/* Real-time Observability: Strands Agent Trace */}
            <AgentTraceDrawer traces={traces} />

            {/* Fleet & Active Live Surplus Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-7">
                <LiveSurplusFeed donations={donations} />
              </div>
              <div className="lg:col-span-5">
                <VolunteerFleetView
                  volunteers={volunteers}
                  onToggleAvailability={(id, avail) =>
                    toggleAvailMutation.mutate({ volunteerId: id, isAvailable: avail })
                  }
                />
              </div>
            </div>
          </div>
        )}

        {role === 'VOLUNTEER' && (
          <DriverMissionView
            dispatches={dispatches}
            volunteers={volunteers}
            onConfirmPickup={(id, code) => pickupMutation.mutate({ dispatchId: id, code })}
            onConfirmDelivery={(id) => deliveryMutation.mutate({ dispatchId: id })}
          />
        )}

        {role === 'INTAKE_WORKER' && (
          <DockIntakeView
            dispatches={dispatches}
            onConfirmDelivery={(id, weight) => deliveryMutation.mutate({ dispatchId: id, weight })}
          />
        )}

        {role === 'DONOR' && (
          <DonorSurplusView
            onSimulateCustom={(alert) => customDonationMutation.mutate(alert)}
            isSubmitting={customDonationMutation.isPending}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/50 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            PantryPulse • Autonomous Food Rescue & Volunteer Dispatch Agent
          </span>
          <span>
            Agents for Humans Hackathon • Powered by AWS Strands Agents SDK
          </span>
        </div>
      </footer>
    </div>
  );
};

const AuthGate: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="text-sm text-slate-400">Loading PantryPulse…</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthView />;
  }

  return <DashboardContent />;
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AuthGate />
      </AuthProvider>
    </QueryClientProvider>
  );
}
