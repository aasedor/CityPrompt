import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { StudentPlanningReport } from './StudentPlanningReport';
import { safeSourceUrl, studentReportsApi, type StudentReport } from './studentReportsApi';

vi.mock('./studentReportsApi', async (original) => ({
  ...await original<typeof import('./studentReportsApi')>(),
  studentReportsApi: { latest: vi.fn(), history: vi.fn(), get: vi.fn(), create: vi.fn(), respond: vi.fn(), export: vi.fn() },
}));

const report: StudentReport = {
  id: 'report-1', project_id: 'project-1', project_name: 'Community', plan_version: 'abcdef123456',
  is_stale: false, created_at: '2026-09-04T12:00:00Z', requested_by_name: 'Student', response_revision: 0,
  scope_zone_ids: null, decisions: {}, analysis: {
    method_version: 'student-review-v1', scope_zone_count: 3, boundary_name: 'Boundary', limitations: ['Advisory.'],
    metrics: [{ key: 'units', label: 'Recorded units', value: null, unit: 'units', derivation: 'No recorded count.', confidence: 0.8 }],
    findings: [{ id: 'access', title: 'Check park access', kind: 'design_suggestion', observation: 'There is a gap.',
      recommendation: 'Show a walking connection.', basis: 'Saved geometry', uncertainty: 'Existing paths not assessed.',
      location: { label: 'Park', zone_ids: ['park-1'] }, sources: [] }],
  },
};

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

const otherReport: StudentReport = {
  ...report, id: 'report-2', project_id: 'project-2', project_name: 'Other community',
  analysis: { ...report.analysis, findings: [{ ...report.analysis.findings[0], title: 'Review the second community' }] },
};

function writeResponse() {
  fireEvent.change(screen.getByLabelText('Your response'), { target: { value: 'adapt' } });
  fireEvent.change(screen.getByLabelText('Your reasoning'), { target: { value: 'Preserve our own project reasoning.' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save response' }));
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(studentReportsApi.latest).mockResolvedValue(null);
  vi.mocked(studentReportsApi.history).mockResolvedValue([]);
  vi.mocked(studentReportsApi.create).mockResolvedValue(report);
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe('StudentPlanningReport', () => {
  it('does not replace project B with a late saved response from project A', async () => {
    const pending = deferred<StudentReport>();
    vi.mocked(studentReportsApi.latest).mockImplementation(async (id) => id === 'project-1' ? report : otherReport);
    vi.mocked(studentReportsApi.respond).mockReturnValue(pending.promise);
    const view = render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText('Check park access');
    writeResponse();
    view.rerender(<StudentPlanningReport projectId="project-2" />);
    await screen.findByText('Review the second community');
    await act(async () => pending.resolve({ ...report, response_revision: 1 }));
    expect(screen.getByText('Review the second community')).toBeInTheDocument();
    expect(screen.queryByText('Check park access')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Save response' })).toBeEnabled();
  });

  it.each(['resolve', 'reject'] as const)('keeps B saving while the previous A response %s completes', async (outcome) => {
    const first = deferred<StudentReport>();
    const second = deferred<StudentReport>();
    vi.mocked(studentReportsApi.latest).mockImplementation(async (id) => id === 'project-1' ? report : otherReport);
    vi.mocked(studentReportsApi.respond).mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const view = render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText('Check park access');
    writeResponse();
    view.rerender(<StudentPlanningReport projectId="project-2" />);
    await screen.findByText('Review the second community');
    expect(screen.getByRole('button', { name: 'Save response' })).toBeEnabled();
    writeResponse();
    await act(async () => {
      if (outcome === 'resolve') first.resolve({ ...report, response_revision: 1 });
      else first.reject({ response: { data: { detail: 'Old project save failed' } } });
    });
    expect(screen.getByRole('button', { name: 'Save response' })).toBeDisabled();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.queryByText('Response saved')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Your reasoning')).toHaveValue('Preserve our own project reasoning.');
    await act(async () => second.resolve({ ...otherReport, response_revision: 1 }));
    expect(screen.getByRole('button', { name: 'Save response' })).toBeEnabled();
    expect(screen.getByText('Response saved')).toBeInTheDocument();
    expect(studentReportsApi.respond).toHaveBeenLastCalledWith('report-2', 'access', expect.objectContaining({ expected_revision: 0 }));
  });

  it.each(['resolve', 'reject'] as const)('keeps B report creation pending when old A creation %s completes', async (outcome) => {
    const first = deferred<StudentReport>();
    const second = deferred<StudentReport>();
    vi.mocked(studentReportsApi.create).mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const view = render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText(/Your first report will capture/);
    fireEvent.click(screen.getByRole('button', { name: 'Request report' }));
    view.rerender(<StudentPlanningReport projectId="project-2" />);
    await screen.findByText(/Your first report will capture/);
    expect(screen.getByRole('button', { name: 'Request report' })).toBeEnabled();
    fireEvent.click(screen.getByRole('button', { name: 'Request report' }));
    await act(async () => {
      if (outcome === 'resolve') first.resolve(report);
      else first.reject({ response: { data: { detail: 'Old project creation failed' } } });
    });
    expect(screen.getByRole('button', { name: 'Preparing…' })).toBeDisabled();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.queryByText('Check park access')).not.toBeInTheDocument();
    await act(async () => second.resolve(otherReport));
    expect(screen.getByText('Review the second community')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Request a new report' })).toBeEnabled();
  });

  it.each(['resolve', 'reject'] as const)('does not download A or clear B export state when old A export %s completes', async (outcome) => {
    const first = deferred<Blob>();
    const second = deferred<Blob>();
    const createUrl = vi.fn(() => 'blob:local-report');
    const revokeUrl = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createUrl, revokeObjectURL: revokeUrl });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    vi.mocked(studentReportsApi.latest).mockImplementation(async (id) => id === 'project-1' ? report : otherReport);
    vi.mocked(studentReportsApi.export).mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const view = render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText('Check park access');
    fireEvent.click(screen.getByRole('button', { name: 'Download printable report' }));
    view.rerender(<StudentPlanningReport projectId="project-2" />);
    await screen.findByText('Review the second community');
    expect(screen.getByRole('button', { name: 'Download printable report' })).toBeEnabled();
    fireEvent.click(screen.getByRole('button', { name: 'Download printable report' }));
    await act(async () => {
      if (outcome === 'resolve') first.resolve(new Blob(['private A']));
      else first.reject({ response: { data: { detail: 'Old project export failed' } } });
    });
    expect(createUrl).not.toHaveBeenCalled();
    expect(click).not.toHaveBeenCalled();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Download printable report' })).toBeDisabled();
    const secondBlob = new Blob(['current B']);
    vi.useFakeTimers();
    await act(async () => second.resolve(secondBlob));
    expect(createUrl).toHaveBeenCalledExactlyOnceWith(secondBlob);
    expect(click).toHaveBeenCalledOnce();
    const downloadedAnchor = click.mock.instances[0];
    expect(downloadedAnchor).toBeInstanceOf(HTMLAnchorElement);
    expect((downloadedAnchor as HTMLAnchorElement).download).toBe('planning-report-report-2.html');
    expect(screen.getByRole('button', { name: 'Download printable report' })).toBeEnabled();
    act(() => vi.runAllTimers());
    expect(revokeUrl).toHaveBeenCalledWith('blob:local-report');
  });

  it('does not start a download after the report panel unmounts', async () => {
    const pending = deferred<Blob>();
    const createUrl = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createUrl });
    vi.mocked(studentReportsApi.latest).mockResolvedValue(report);
    vi.mocked(studentReportsApi.export).mockReturnValue(pending.promise);
    const view = render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText('Check park access');
    fireEvent.click(screen.getByRole('button', { name: 'Download printable report' }));
    view.unmount();
    await act(async () => pending.resolve(new Blob(['private A'])));
    expect(createUrl).not.toHaveBeenCalled();
  });

  it('does not clear a newer automatic refresh loading state when report creation finishes', async () => {
    const creation = deferred<StudentReport>();
    const refresh = deferred<StudentReport>();
    vi.mocked(studentReportsApi.latest).mockResolvedValue(report);
    vi.mocked(studentReportsApi.create).mockReturnValue(creation.promise);
    vi.mocked(studentReportsApi.get).mockReturnValue(refresh.promise);
    const view = render(<StudentPlanningReport projectId="project-1" planChangeToken={1} />);
    await screen.findByText('Check park access');
    fireEvent.click(screen.getByRole('button', { name: 'Request a new report' }));
    view.rerender(<StudentPlanningReport projectId="project-1" planChangeToken={2} />);
    await act(async () => creation.resolve({ ...report, id: 'new-report' }));
    expect(screen.getByText('Checking saved report…')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Request a new report' })).toBeDisabled();
    await act(async () => refresh.resolve({ ...report, is_stale: true }));
    expect(screen.getByText('The proposal has changed.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Request a new report' })).toBeEnabled();
  });

  it('waits for the student to request a report and sends the intended zone scope', async () => {
    render(<StudentPlanningReport projectId="project-1" zoneIds={['building-1', 'park-1']} />);
    await screen.findByText(/Your first report will capture/);
    expect(studentReportsApi.create).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Request report' }));
    expect(await screen.findByText('Check park access')).toBeInTheDocument();
    expect(studentReportsApi.create).toHaveBeenCalledWith('project-1', ['building-1', 'park-1']);
  });

  it('saves a declined recommendation with the student’s own reason and leaves design freedom explicit', async () => {
    vi.mocked(studentReportsApi.latest).mockResolvedValue(report);
    vi.mocked(studentReportsApi.respond).mockResolvedValue({ ...report, response_revision: 1 });
    render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText('Check park access');
    fireEvent.change(screen.getByLabelText('Your response'), { target: { value: 'decline' } });
    fireEvent.change(screen.getByLabelText('Your reasoning'), { target: { value: 'We use the existing park entrance.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save response' }));
    await screen.findByText('Response saved');
    expect(studentReportsApi.respond).toHaveBeenCalledWith('report-1', 'access', {
      choice: 'decline', rationale: 'We use the existing park entrance.', follow_through: '', expected_revision: 0,
    });
    expect(screen.getByText(/keep designing and rendering/)).toBeInTheDocument();
  });

  it('retains a written rationale after a teammate conflict, and refreshes staleness on plan changes', async () => {
    vi.mocked(studentReportsApi.latest).mockResolvedValue(report);
    vi.mocked(studentReportsApi.respond).mockRejectedValue({ response: { data: { detail: 'A teammate updated this report. Refresh it.' } } });
    vi.mocked(studentReportsApi.get).mockResolvedValue({ ...report, is_stale: true, response_revision: 1 });
    const view = render(<StudentPlanningReport projectId="project-1" planChangeToken={1} />);
    await screen.findByText('Check park access');
    fireEvent.change(screen.getByLabelText('Your response'), { target: { value: 'adapt' } });
    fireEvent.change(screen.getByLabelText('Your reasoning'), { target: { value: 'Our route protects mature trees.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save response' }));
    await screen.findByText(/A teammate updated this report/);
    expect(screen.getByLabelText('Your reasoning')).toHaveValue('Our route protects mature trees.');
    view.rerender(<StudentPlanningReport projectId="project-1" planChangeToken={2} />);
    await screen.findByText('The proposal has changed.');
    expect(screen.getByLabelText('Your reasoning')).toHaveValue('Our route protects mature trees.');
  });

  it('requires a reason, exposes read-only reports to viewers, and rejects unsafe citation links', async () => {
    vi.mocked(studentReportsApi.latest).mockResolvedValue(report);
    const view = render(<StudentPlanningReport projectId="project-1" />);
    await screen.findByText('Check park access');
    fireEvent.click(screen.getByRole('button', { name: 'Save response' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('explain your reasoning');
    expect(studentReportsApi.respond).not.toHaveBeenCalled();
    view.rerender(<StudentPlanningReport projectId="project-1" canEdit={false} />);
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Save response' })).not.toBeInTheDocument());
    expect(screen.queryByRole('button', { name: 'Request a new report' })).not.toBeInTheDocument();
    expect(safeSourceUrl('javascript:alert(1)')).toBeUndefined();
    expect(safeSourceUrl('https://city.example/plan.pdf')).toBe('https://city.example/plan.pdf');
  });
});
