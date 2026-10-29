import { render, screen, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { beforeEach, expect, it, vi } from 'vitest';
import { StudentPlanningReport } from './StudentPlanningReport';
import { studentReportsApi, type StudentReport } from './studentReportsApi';
import { reportDraftKey, writeReportDraft, readReportDraft } from './reportDrafts';

vi.mock('./studentReportsApi', async original => ({ ...await original<typeof import('./studentReportsApi')>(),
  studentReportsApi: { latest: vi.fn(), history: vi.fn(), get: vi.fn(), create: vi.fn(), respond: vi.fn(), export: vi.fn() } }));
const report: StudentReport = { id: 'report', project_id: 'project', project_name: 'Site', plan_version: '123',
  created_at: '2026-10-29', requested_by_name: 'Student', response_revision: 0, is_stale: false, scope_zone_ids: null, decisions: {},
  analysis: { method_version: 'student-review-v2-placement-plots', scope_zone_count: 2, boundary_name: 'Site', limitations: ['Counts are concept estimates.'],
    metrics: [ { key: 'building_count', label: 'Buildings', value: 2, unit: 'objects', derivation: 'Distinct saved building records.', confidence: 1 },
      { key: 'retail_units', label: 'Retail units', value: null, unit: 'units', derivation: 'Unknown: no recorded unit counts.', confidence: .8 } ],
    findings: [{ id: 'question', title: 'Explain park access', kind: 'unresolved_question', observation: 'Missing park.', recommendation: 'Write why.',
      basis: 'Saved geometry', uncertainty: '', location: { label: 'Site', zone_ids: [] }, sources: [{ title: 'City plan', url: 'https://city.example/plan' }] }] } };
beforeEach(() => { sessionStorage.clear(); vi.clearAllMocks(); vi.mocked(studentReportsApi.latest).mockResolvedValue(report); vi.mocked(studentReportsApi.history).mockResolvedValue([]); });
it('shows quantities and sources without student response prompts, preserving old browser drafts', async () => {
  const key = reportDraftKey('anonymous', 'project', 'report', 'question');
  writeReportDraft(key, { choice: 'adapt', rationale: 'Keep this earlier draft.', followThrough: '' });
  const view = render(<StudentPlanningReport projectId="project" />);
  expect(await screen.findByRole('table')).toHaveTextContent('Buildings');
  expect(screen.getByRole('table')).toHaveTextContent('Unknown');
  expect(screen.getByRole('link', { name: 'City plan' })).toHaveAttribute('href', 'https://city.example/plan');
  expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  expect(screen.queryByText('Explain park access')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Save response' })).not.toBeInTheDocument();
  view.unmount();
  expect(readReportDraft(key)?.rationale).toBe('Keep this earlier draft.');
  expect(studentReportsApi.respond).not.toHaveBeenCalled();
});
it('clears the previous project quantities immediately while the next project is loading', async () => {
  const view = render(<StudentPlanningReport projectId="project" />);
  await screen.findByRole('table');
  vi.mocked(studentReportsApi.latest).mockReturnValue(new Promise(() => {}));
  view.rerender(<StudentPlanningReport projectId="other" />);
  await waitFor(() => expect(screen.queryByRole('table')).not.toBeInTheDocument());
  expect(screen.getByRole('status')).toHaveTextContent('Checking saved report');
});
it('keeps derivations available in a disclosure while the main table shows compact quantity statuses', async () => {
  render(<StudentPlanningReport projectId="project" />);
  const table = await screen.findByRole('table');
  expect(within(table).getByRole('columnheader', {name: 'Status'})).toBeInTheDocument();
  expect(table).not.toHaveTextContent('Distinct saved building records.');
  expect(screen.getByText('How totals are calculated')).toBeInTheDocument();
  expect(screen.getByText('Distinct saved building records.').closest('details')).not.toHaveAttribute('open');
});
