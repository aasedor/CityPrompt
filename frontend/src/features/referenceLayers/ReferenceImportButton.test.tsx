import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ReferenceImportButton } from './ReferenceImportButton';
import { referenceLayersApi } from './api';
import { siteZonesApi } from '@/services/api';

vi.mock('@/services/api', () => ({ api: {}, getApiErrorMessage: (_: unknown, fallback: string) => fallback, siteZonesApi: { create: vi.fn() } }));
vi.mock('./api', () => ({ referenceLayerQueryKey: (id: string) => ['reference-layers', id], referenceLayersApi: { import: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));

function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  render(<QueryClientProvider client={client}><ReferenceImportButton projectId="project-a" /></QueryClientProvider>);
  const file = new File(['{"type":"FeatureCollection","features":[]}'], 'zoning.geojson', { type: 'application/geo+json' });
  fireEvent.change(screen.getByLabelText('Choose reference dataset'), { target: { files: [file] } });
  return file;
}

describe('Reference import', () => {
  beforeEach(() => vi.clearAllMocks());
  it('defaults to reference persistence and never calls design-zone creation', async () => {
    vi.mocked(referenceLayersApi.import).mockResolvedValue({ name: 'Zoning', feature_count: 1, bounds: [0, 0, 1, 1] } as never);
    const file = setup();
    expect(screen.getByLabelText('Reference type')).toHaveValue('reference');
    fireEvent.click(screen.getAllByRole('button', { name: 'Import reference' }).slice(-1)[0]);
    await waitFor(() => expect(referenceLayersApi.import).toHaveBeenCalledWith('project-a', file, expect.objectContaining({ kind: 'reference' })));
    expect(siteZonesApi.create).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
  it('preserves a failed upload and metadata for a deliberate retry', async () => {
    vi.mocked(referenceLayersApi.import).mockRejectedValueOnce(new Error('Network failed'));
    const file = setup();
    fireEvent.change(screen.getByLabelText('Reference type'), { target: { value: 'zoning' } });
    fireEvent.click(screen.getAllByRole('button', { name: 'Import reference' }).slice(-1)[0]);
    await screen.findByRole('alert');
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByLabelText('Reference type')).toHaveValue('zoning');
    vi.mocked(referenceLayersApi.import).mockResolvedValueOnce({ name: 'Zoning', feature_count: 1, bounds: [0, 0, 1, 1] } as never);
    fireEvent.click(screen.getAllByRole('button', { name: 'Import reference' }).slice(-1)[0]);
    await waitFor(() => expect(referenceLayersApi.import).toHaveBeenLastCalledWith('project-a', file, expect.objectContaining({ kind: 'zoning' })));
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});
