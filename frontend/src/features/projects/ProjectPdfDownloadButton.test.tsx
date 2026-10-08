import '@testing-library/jest-dom/vitest';
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { ProjectPdfDownloadButton } from './ProjectPdfDownloadButton';
import { api } from '@/services/api';
import toast from 'react-hot-toast';

vi.mock('@/services/api', () => ({ api: { get: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { error: vi.fn() } }));
afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); vi.clearAllMocks(); });

it('downloads the PDF through the authenticated API client', async () => {
  const blob = new Blob(['pdf'], { type: 'application/pdf' });
  vi.mocked(api.get).mockResolvedValue({ data: blob });
  const create = vi.fn(() => 'blob:report');
  vi.stubGlobal('URL', { createObjectURL: create, revokeObjectURL: vi.fn() });
  const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
  render(<ProjectPdfDownloadButton projectId="project-a" />);
  fireEvent.click(screen.getByRole('button', { name: 'Download project PDF' }));
  await waitFor(() => expect(click).toHaveBeenCalledOnce());
  expect(api.get).toHaveBeenCalledWith('/api/v1/reports/projects/project-a/report', { responseType: 'blob' });
  expect(create).toHaveBeenCalledWith(blob);
});

it('shows download failure and allows a retry', async () => {
  vi.mocked(api.get).mockRejectedValue(new Error('offline'));
  render(<ProjectPdfDownloadButton projectId="project-a" />);
  fireEvent.click(screen.getByRole('button', { name: 'Download project PDF' }));
  await waitFor(() => expect(toast.error).toHaveBeenCalled());
  expect(screen.getByRole('button', { name: 'Download project PDF' })).toBeEnabled();
});
