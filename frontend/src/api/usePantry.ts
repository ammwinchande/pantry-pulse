import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from './client';
import { useAuth } from './useAuth';
import type {
  SystemStats,
  DonationAlert,
  DispatchProposal,
  Dispatch,
  Volunteer,
  AgentTraceLog,
  NotificationMessage,
} from '../types';

/** Resolve the acting coordinator's display name from the auth session. */
function useApproverName(): string {
  const { user } = useAuth();
  return user?.name ?? 'Coordinator';
}

export function useStats() {
  return useQuery<SystemStats>({
    queryKey: ['stats'],
    queryFn: () => fetchApi<SystemStats>('/stats'),
    refetchInterval: 3000,
  });
}

export function useDonations() {
  return useQuery<DonationAlert[]>({
    queryKey: ['donations'],
    queryFn: () => fetchApi<DonationAlert[]>('/donations'),
    refetchInterval: 3000,
  });
}

export function usePendingDecisions() {
  return useQuery<DispatchProposal[]>({
    queryKey: ['pendingDecisions'],
    queryFn: () => fetchApi<DispatchProposal[]>('/decisions/pending'),
    refetchInterval: 2500,
  });
}

export function useDispatches() {
  return useQuery<Dispatch[]>({
    queryKey: ['dispatches'],
    queryFn: () => fetchApi<Dispatch[]>('/dispatches'),
    refetchInterval: 3000,
  });
}

export function useVolunteers() {
  return useQuery<Volunteer[]>({
    queryKey: ['volunteers'],
    queryFn: () => fetchApi<Volunteer[]>('/volunteers'),
    refetchInterval: 4000,
  });
}

export function useAgentTraces() {
  return useQuery<AgentTraceLog[]>({
    queryKey: ['agentTraces'],
    queryFn: () => fetchApi<AgentTraceLog[]>('/agent/traces'),
    refetchInterval: 2500,
  });
}

export function useNotifications() {
  return useQuery<NotificationMessage[]>({
    queryKey: ['notifications'],
    queryFn: () => fetchApi<NotificationMessage[]>('/notifications'),
    refetchInterval: 3000,
  });
}

export function useSimulateAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => fetchApi<DispatchProposal>('/donations/simulate', { method: 'POST' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingDecisions'] });
      queryClient.invalidateQueries({ queryKey: ['donations'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      queryClient.invalidateQueries({ queryKey: ['agentTraces'] });
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useApproveDecision() {
  const queryClient = useQueryClient();
  const approver = useApproverName();
  return useMutation({
    mutationFn: (proposalId: string) =>
      fetchApi<Dispatch>(`/decisions/${proposalId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ approved_by: approver }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingDecisions'] });
      queryClient.invalidateQueries({ queryKey: ['dispatches'] });
      queryClient.invalidateQueries({ queryKey: ['volunteers'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      queryClient.invalidateQueries({ queryKey: ['agentTraces'] });
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useOverrideAlternative() {
  const queryClient = useQueryClient();
  const approver = useApproverName();
  return useMutation({
    mutationFn: (proposalId: string) =>
      fetchApi<Dispatch>(`/decisions/${proposalId}/override-alternative`, {
        method: 'POST',
        body: JSON.stringify({ approved_by: approver }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingDecisions'] });
      queryClient.invalidateQueries({ queryKey: ['dispatches'] });
      queryClient.invalidateQueries({ queryKey: ['volunteers'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function useRejectDecision() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ proposalId, reason }: { proposalId: string; reason: string }) =>
      fetchApi(`/decisions/${proposalId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingDecisions'] });
      queryClient.invalidateQueries({ queryKey: ['donations'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function useConfirmPickup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ dispatchId, code }: { dispatchId: string; code: string }) =>
      fetchApi<Dispatch>(`/dispatches/${dispatchId}/pickup`, {
        method: 'POST',
        body: JSON.stringify({ verification_code: code }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dispatches'] });
      queryClient.invalidateQueries({ queryKey: ['volunteers'] });
      queryClient.invalidateQueries({ queryKey: ['donations'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function useConfirmDelivery() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ dispatchId, weight }: { dispatchId: string; weight?: number }) =>
      fetchApi<Dispatch>(`/dispatches/${dispatchId}/deliver`, {
        method: 'POST',
        body: JSON.stringify({ final_weight_lbs: weight }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dispatches'] });
      queryClient.invalidateQueries({ queryKey: ['volunteers'] });
      queryClient.invalidateQueries({ queryKey: ['donations'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}

export function useToggleAvailability() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ volunteerId, isAvailable }: { volunteerId: string; isAvailable: boolean }) =>
      fetchApi<Volunteer>(`/volunteers/${volunteerId}/toggle-availability`, {
        method: 'POST',
        body: JSON.stringify({ is_available: isAvailable }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['volunteers'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}
