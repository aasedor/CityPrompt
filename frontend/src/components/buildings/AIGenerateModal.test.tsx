// @vitest-environment jsdom
import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { AIGenerateModal } from './AIGenerateModal';

const mock = vi.hoisted(() => ({
  getPhotoReferences: vi.fn(),
  createPhotoReferences: vi.fn(),
  generatePhotoModel: vi.fn(),
  getTemplates: vi.fn(),
  getEngines: vi.fn(),
  getRenderPreviews: vi.fn(),
  me: vi.fn(),
}));

vi.mock('@/services/api', () => ({
  buildingsApi: mock,
  authApi: { me: mock.me },
  resolveApiFileUrl: (url: string) => url,
  subscribeAssetTicketChanges: () => () => {},
  getAssetTicketRevision: () => 0,
}));
vi.mock('./StyleSelector', () => ({ StyleSelector: () => null }));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('student reviews generated views before starting the paid model stage', async () => {
  mock.getTemplates.mockResolvedValue([]);
  mock.getEngines.mockResolvedValue([{ id: 'meshy', name: 'Meshy', available: true }]);
  mock.getRenderPreviews.mockResolvedValue([]);
  mock.me.mockResolvedValue({ id: 'student-1', role: 'editor', render_credits: 950 });
  const idle = { status: 'idle', brief: '', reference_urls: [], source_count: 0, error: null,
    reference_token_cost: 50, model_token_cost: 150 };
  const ready = { ...idle, status: 'references_ready', reference_urls: ['/api/v1/files/a', '/api/v1/files/b', '/api/v1/files/c'] };
  mock.getPhotoReferences.mockResolvedValueOnce(idle).mockResolvedValue(ready);
  mock.createPhotoReferences.mockResolvedValue(undefined);
  mock.generatePhotoModel.mockResolvedValue({ status: 'generating', progress: 0 });

  const view = render(<AIGenerateModal buildingId="building-1" onClose={() => {}} onComplete={() => {}} />);
  fireEvent.click(screen.getByRole('button', { name: /Photos to 3D/i }));
  expect(screen.getByText(/private 3D model preview/i)).toBeTruthy();
  expect(screen.getByText(/Costs 50 City Prompt tokens/i)).toBeTruthy();
  const upload = view.container.querySelector('input[multiple]') as HTMLInputElement;
  const photo = new File(['image'], 'home.jpg', { type: 'image/jpeg' });
  fireEvent.change(upload, { target: { files: [photo] } });
  fireEvent.change(screen.getByLabelText(/Describe anything the photos do not show/i), {
    target: { value: 'two mirrored homes' },
  });
  fireEvent.click(screen.getByRole('button', { name: /Step 1 · Prepare reference views/i }));

  await waitFor(() => expect(mock.createPhotoReferences).toHaveBeenCalledWith(
    'building-1', [photo], 'two mirrored homes',
  ));
  await waitFor(() => expect(screen.getAllByAltText(/Generated building reference/)).toHaveLength(3));
  expect(mock.generatePhotoModel).not.toHaveBeenCalled();
  expect(screen.getByText(/Costs 150 City Prompt tokens/i)).toBeTruthy();
  fireEvent.click(screen.getByLabelText('Use view 1'));
  fireEvent.click(screen.getByLabelText('Use view 3'));
  fireEvent.click(screen.getByRole('button', { name: /Step 2 · Generate 3D model preview/i }));
  await waitFor(() => expect(mock.generatePhotoModel).toHaveBeenCalledWith('building-1', [1]));
});
