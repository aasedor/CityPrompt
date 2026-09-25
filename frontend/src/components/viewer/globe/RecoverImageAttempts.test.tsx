import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { RecoverImageAttempts } from './RecoverImageAttempts';

const mocks = vi.hoisted(() => ({ list: vi.fn(), recover: vi.fn(), acknowledge: vi.fn() }));
vi.mock('@/services/api', () => ({ direct3DAttempts: { ...mocks,
  capabilities: async () => ({ enabled: true, images_enabled: true }) }, rendersApi: {} }));
vi.mock('@/store', () => ({ useAuthStore: (select: (state: unknown) => unknown) => select({ user: { id: 'student' } }) }));

describe('image recovery panel', () => {
  it('opens the saved image alongside its original and keeps unverified fidelity visible', async () => {
    mocks.list.mockResolvedValue([{ id: 'image-1', project_id: 'project', status: 'completed', style: 'watercolour', created_at: '2026-09-23T12:00:00Z' }]);
    mocks.recover.mockResolvedValue({ attempt: { id: 'image-1' }, style: 'watercolour', source_image_base64: 'b3JpZ2luYWw=',
      response: { image_base64: 'cmVzdWx0', warnings: ['Check street junctions'], diagnostics: { processing_mode: 'scene' } } });
    render(<RecoverImageAttempts projectId="project" />);
    await waitFor(() => expect(mocks.list).toHaveBeenCalledWith('project'));
    fireEvent.click(screen.getByText('Recover recent images'));
    fireEvent.click(await screen.findByText('Open saved image'));
    expect(await screen.findByText('Compare with your original design')).toBeTruthy();
    expect(screen.getByAltText('Original 3D design used for this saved image').getAttribute('src')).toContain('b3JpZ2luYWw=');
    expect(screen.getByAltText('Recovered image result for comparison with its original design').getAttribute('src')).toContain('cmVzdWx0');
    expect(screen.getByText('Check street junctions')).toBeTruthy();
    expect(mocks.recover).toHaveBeenCalledTimes(1);
  });
});
