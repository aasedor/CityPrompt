import type { StudentChoice } from './studentReportsApi';

export interface ReportDraft {
  choice: StudentChoice | '';
  rationale: string;
  followThrough: string;
}

// Tab-scoped, account/project/report/finding-specific drafts survive panel
// navigation and reload without submitting an unfinished response to the server.
const fallback = new Map<string, string>();
export const reportDraftKey = (account: string, project: string, report: string, finding: string) =>
  `cityprompt:report-draft:${JSON.stringify([account, project, report, finding])}`;

export function readReportDraft(key: string): ReportDraft | null {
  try {
    let raw: string | null;
    try { raw = fallback.get(key) ?? sessionStorage.getItem(key); } catch { raw = fallback.get(key) ?? null; }
    if (!raw) return null;
    const draft = JSON.parse(raw) as ReportDraft;
    return ['', 'implement', 'adapt', 'decline'].includes(draft.choice)
      && typeof draft.rationale === 'string' && typeof draft.followThrough === 'string' ? draft : null;
  } catch { return null; }
}

export function writeReportDraft(key: string, draft: ReportDraft) {
  const raw = JSON.stringify(draft);
  try { sessionStorage.setItem(key, raw); fallback.delete(key); }
  catch { fallback.set(key, raw); }
}

export function clearSavedReportDraft(key: string, saved: ReportDraft) {
  // A completed request must not erase text typed while it was in flight.
  if (JSON.stringify(readReportDraft(key)) !== JSON.stringify(saved)) return;
  try { sessionStorage.removeItem(key); } catch { /* Memory fallback below. */ }
  fallback.delete(key);
}
