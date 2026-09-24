import { api } from '@/services/api';
import type { ParkAccessSnapshot } from '@/components/viewer/globe/parkAccessConnections';

export type StudentChoice = 'implement' | 'adapt' | 'decline';
export interface ReportSource {
  title: string;
  url?: string | null;
  page?: number;
  section?: string | null;
  excerpt?: string;
  context_created_at?: string;
}
export interface StudentFinding {
  id: string;
  kind: 'design_suggestion' | 'unresolved_question' | 'source_context';
  title: string;
  observation: string;
  recommendation: string;
  basis: string;
  uncertainty: string;
  location: { label: string; zone_ids: string[] };
  sources: ReportSource[];
}
export interface StudentDecision {
  choice: StudentChoice;
  rationale: string;
  follow_through: string;
  author_id: string;
  author_name: string;
  updated_at: string;
}
export interface StudentReport {
  id: string;
  project_id: string;
  project_name: string;
  plan_version: string;
  is_stale: boolean;
  created_at: string;
  requested_by_name: string;
  response_revision: number;
  scope_zone_ids: string[] | null;
  decisions: Record<string, StudentDecision>;
  analysis: {
    method_version: string;
    scope_zone_count: number;
    boundary_name: string | null;
    metrics: { key: string; label: string; value: number | null; unit: string; derivation: string; confidence: number }[];
    findings: StudentFinding[];
    limitations: string[];
  };
}
export type ReportSummary = Pick<StudentReport, 'id' | 'created_at' | 'plan_version' | 'requested_by_name'>;

const base = '/api/v1/student-reports';
export const studentReportsApi = {
  latest: async (projectId: string) => (await api.get<StudentReport | null>(`${base}/project/${projectId}`)).data,
  history: async (projectId: string) => (await api.get<ReportSummary[]>(`${base}/project/${projectId}/history`)).data,
  get: async (reportId: string) => (await api.get<StudentReport>(`${base}/${reportId}`)).data,
  create: async (projectId: string, zoneIds?: string[], parkAccess?: ParkAccessSnapshot) => (
    await api.post<StudentReport>(`${base}/project/${projectId}`, {
      zone_ids: zoneIds ?? null, ...(parkAccess ? { park_access_snapshot: parkAccess } : {}),
    })
  ).data,
  respond: async (reportId: string, findingId: string, decision: {
    choice: StudentChoice; rationale: string; follow_through: string; expected_revision: number;
  }) => (await api.patch<StudentReport>(`${base}/${reportId}/findings/${encodeURIComponent(findingId)}`, decision)).data,
  export: async (reportId: string) => (await api.get<Blob>(`${base}/${reportId}/export`, { responseType: 'blob' })).data,
};

export function reportError(error: unknown): string {
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  return typeof detail === 'string' ? detail : 'The report could not be saved or loaded. Your design is still available. Please try again.';
}

export function safeSourceUrl(value?: string | null): string | undefined {
  if (!value) return undefined;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : undefined;
  } catch { return undefined; }
}
