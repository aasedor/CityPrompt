import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { geocodingApi } from '@/services/geocoding';
import { projectsApi } from '@/services/api';
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

function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={['/projects/new']}>
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
    fireEvent.change(screen.getByPlaceholderText('e.g., Riverside Development Phase 1'), { target: { value: 'Currie exercise' } });
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
