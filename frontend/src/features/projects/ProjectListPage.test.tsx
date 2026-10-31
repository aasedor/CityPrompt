import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { geocodingApi } from '@/services/geocoding';
import { projectsApi, rendersApi } from '@/services/api';
import { ProjectListPage } from './ProjectListPage';

vi.mock('@/store', () => ({ useAuthStore: () => ({ user: { id: 'student', role: 'user' } }) }));
vi.mock('@/services/api', () => ({
  projectsApi: { list: vi.fn(), create: vi.fn() },
  rendersApi: { list: vi.fn() },
  getApiErrorMessage: (_: unknown, fallback: string) => fallback,
  resolveApiFileUrl: (url: string) => url,
}));
vi.mock('@/services/geocoding', () => ({
  geocodingApi: { autocomplete: vi.fn(), resolve: vi.fn() },
}));
vi.mock('@/components/viewer/AnimateRenderButton', () => ({ AnimateRenderButton: () => null }));

function setup(path = '/projects/new') {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <ProjectListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('new project location', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(projectsApi.list).mockResolvedValue([]);
    vi.mocked(projectsApi.create).mockResolvedValue({ id: 'created', name: 'Currie exercise' } as never);
  });

  it('resolves a typed address before creating, even when no suggestion was clicked', async () => {
    vi.mocked(geocodingApi.autocomplete).mockResolvedValue([{ id: 'currie', place_name: 'Currie, Calgary' }] as never);
    vi.mocked(geocodingApi.resolve).mockResolvedValue({ latitude: 51.01848, longitude: -114.12376, address: 'Currie, Calgary' });
    setup();
    await screen.findByRole('heading', { name: 'Create New Project' });
    fireEvent.change(screen.getByRole('textbox', { name: /^Project Name/ }), { target: { value: 'Currie exercise' } });
    fireEvent.change(screen.getByPlaceholderText('Search for an address...'), { target: { value: 'Currie, Calgary' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create Project' }));
    await waitFor(() => expect(projectsApi.create).toHaveBeenCalledWith({
      name: 'Currie exercise',
      description: undefined,
      location: { latitude: 51.01848, longitude: -114.12376, address: 'Currie, Calgary' },
    }));
  });

  it('blocks creation when typed location cannot be resolved', async () => {
    vi.mocked(geocodingApi.autocomplete).mockResolvedValue([]);
    setup();
    await screen.findByRole('heading', { name: 'Create New Project' });
    fireEvent.change(screen.getByPlaceholderText('e.g., Riverside Development Phase 1'), { target: { value: 'Currie exercise' } });
    fireEvent.change(screen.getByPlaceholderText('Search for an address...'), { target: { value: 'Unknown field' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create Project' }));
    expect(await screen.findByText('Could not locate that address. Choose a suggestion or clear the location.')).toBeInTheDocument();
    expect(projectsApi.create).not.toHaveBeenCalled();
  });
});

describe('project render preview pressure', () => {
  const projects = Array.from({ length: 100 }, (_, index) => ({
    id: `project-${index}`, name: `Project ${index}`, updated_at: '2026-10-31T00:00:00Z',
  }));
  let pending: Array<{ resolve: (value: never[]) => void; reject: (reason: Error) => void; signal?: AbortSignal }>;
  let active: number;
  let peak: number;

  beforeEach(() => {
    vi.clearAllMocks();
    pending = [];
    active = 0;
    peak = 0;
    vi.mocked(projectsApi.list).mockResolvedValue(projects as never);
    vi.mocked(projectsApi.create).mockResolvedValue({ id: 'created', name: 'New study' } as never);
    vi.mocked(rendersApi.list).mockImplementation((...args: unknown[]) => {
      const signal = args[1] as AbortSignal | undefined;
      active += 1;
      peak = Math.max(peak, active);
      return new Promise<never[]>((resolve, reject) => {
        pending.push({ resolve, reject, signal });
        signal?.addEventListener('abort', () => reject(new DOMException('Cancelled', 'AbortError')), { once: true });
      }).finally(() => { active -= 1; });
    });
  });

  it('loads all 100 projects with at most three complete preview operations, isolating a failure', async () => {
    const view = setup('/projects');
    await waitFor(() => expect(rendersApi.list).toHaveBeenCalledTimes(3));
    await act(async () => { pending[0].reject(new Error('One preview unavailable')); });
    await waitFor(() => expect(rendersApi.list).toHaveBeenCalledTimes(4));
    let settled = 1;
    while (settled < projects.length) {
      const next = pending.slice(settled);
      await act(async () => { next.forEach(item => item.resolve([])); });
      settled += next.length;
    }
    expect(rendersApi.list).toHaveBeenCalledTimes(100);
    expect(peak).toBe(3);
    expect(active).toBe(0);
    expect(screen.getByText('Project 99')).toBeInTheDocument();
    view.unmount();
  });

  it('cancels active requests and never starts the queued 97 after leaving Projects', async () => {
    const view = setup('/projects');
    await waitFor(() => expect(rendersApi.list).toHaveBeenCalledTimes(3));
    await act(async () => { view.unmount(); });
    expect(pending.every(item => item.signal?.aborted)).toBe(true);
    expect(rendersApi.list).toHaveBeenCalledTimes(3);
    expect(active).toBe(0);
  });

  it('pauses and cancels previews for New Project, then resumes when the form closes', async () => {
    // The separate 100-project case covers scale; this case exercises form transitions.
    vi.mocked(projectsApi.list).mockResolvedValue(projects.slice(0, 5) as never);
    const view = setup('/projects');
    await waitFor(() => expect(rendersApi.list).toHaveBeenCalledTimes(3));
    fireEvent.click(screen.getByRole('button', { name: 'New Project' }));
    await waitFor(() => expect(pending.every(item => item.signal?.aborted)).toBe(true));
    expect(rendersApi.list).toHaveBeenCalledTimes(3);
    fireEvent.click(screen.getByRole('button', { name: 'Close new project form' }));
    await waitFor(() => expect(rendersApi.list).toHaveBeenCalledTimes(6));
    await act(async () => { view.unmount(); });
  });

  it('starts no preview requests when opening /projects/new and can create immediately', async () => {
    const view = setup();
    await screen.findByText('Project 99');
    expect(rendersApi.list).not.toHaveBeenCalled();
    fireEvent.change(screen.getByRole('textbox', { name: /^Project Name/ }), { target: { value: 'New study' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create Project' }));
    await waitFor(() => expect(projectsApi.create).toHaveBeenCalledWith({ name: 'New study', description: undefined, location: undefined }));
    view.unmount();
  });

  it('can create without waiting for the active preview batch', async () => {
    vi.mocked(projectsApi.list).mockResolvedValue(projects.slice(0, 5) as never);
    const view = setup('/projects');
    await waitFor(() => expect(rendersApi.list).toHaveBeenCalledTimes(3));
    fireEvent.click(screen.getByRole('button', { name: 'New Project' }));
    fireEvent.change(screen.getByRole('textbox', { name: /^Project Name/ }), { target: { value: 'New study' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create Project' }));
    await waitFor(() => expect(projectsApi.create).toHaveBeenCalledWith({ name: 'New study', description: undefined, location: undefined }));
    await act(async () => { view.unmount(); });
    expect(pending.slice(0, 3).every(item => item.signal?.aborted)).toBe(true);
  });

  it('uses lazy, small previews but opens and downloads the scoped original', async () => {
    const image = '/api/v1/files/projects/project-0/renders/scene.png?asset_ticket=scoped';
    vi.mocked(projectsApi.list).mockResolvedValue([projects[0]] as never);
    vi.mocked(rendersApi.list).mockResolvedValue([{ id: 'render-0', image_url: image, prompt: 'Bridge view', created_at: '2026-10-31T00:00:00Z' }] as never);
    setup('/projects');
    const preview = await screen.findByAltText('Bridge view');
    expect(preview).toHaveAttribute('loading', 'lazy');
    expect(preview).toHaveAttribute('decoding', 'async');
    expect(new URL(preview.getAttribute('src')!, window.location.origin).searchParams.get('thumbnail')).toBe('true');
    expect(preview.getAttribute('src')).toContain('asset_ticket=scoped');
    fireEvent.click(preview);
    const dialog = screen.getByRole('dialog', { name: 'Saved project render' });
    expect(within(dialog).getByAltText('Bridge view')).toHaveAttribute('src', image);
    expect(within(dialog).getByTitle('Download')).toHaveAttribute('href', image);
  });
});
