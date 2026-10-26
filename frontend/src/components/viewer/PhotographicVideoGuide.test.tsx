import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PhotographicVideoGuide } from './PhotographicVideoGuide';
const api = vi.hoisted(() => ({ generate: vi.fn(), list: vi.fn(), recover: vi.fn() }));
vi.mock('@/services/api', () => ({ direct3DAttempts: api, getApiErrorMessage: (_e: unknown, fallback: string) => fallback }));
const result = { purpose: 'video_appearance' as const, attempt_id: 'image-attempt',
  image_base64: 'cGhvdG8=', source_video_sha256: 'a'.repeat(64), scene_revision_sha256: 'b'.repeat(64),
  output_fingerprint: 'c'.repeat(64), model: 'gpt-image-2.5-sunburst' as const, tokens_spent: 26 };
describe('reviewed photographic video guide', () => {
  beforeEach(() => { vi.clearAllMocks(); api.list.mockResolvedValue([]); });
  it('blocks separate paid guide creation while the video workflow owns generation', async () => {
    render(<PhotographicVideoGuide disabled projectId="project" signature="route" guide={null}
      prepare={vi.fn()} onChange={vi.fn()} onBusyChange={vi.fn()}/>);
    await waitFor(()=>expect(api.list).toHaveBeenCalledOnce());
    const create=screen.getByRole('button',{name:/Create photographic guide/});
    expect(create).toBeDisabled();fireEvent.click(create);expect(api.generate).not.toHaveBeenCalled();
  });
  it('creates one saved image and requires a separate visual review before using it', async () => {
    api.generate.mockResolvedValue(result);
    const change = vi.fn();
    render(<PhotographicVideoGuide projectId="project" signature="route-one" guide={null}
      prepare={async () => ({ project_id: 'project', purpose: 'video_appearance', beauty_image_base64: 'native-source', source_video_sha256: 'a'.repeat(64) })}
      onChange={change} onBusyChange={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Create photographic guide · 26 tokens' }));
    expect(await screen.findByAltText('Photographic video guide to review')).toBeVisible();
    expect(change).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Use this guide' }));
    expect(change).toHaveBeenCalledWith(expect.objectContaining({ ...result, signature: 'route-one' }));
    expect(api.generate).toHaveBeenCalledOnce();
    expect(api.generate).toHaveBeenCalledWith(expect.objectContaining({ beauty_image_base64: 'native-source' }));
  });
  it('retains a completed guide for recovery when the route changes while generating', async () => {
    let resolve!: (value: typeof result) => void;
    api.generate.mockReturnValue(new Promise(r => { resolve = r; }));
    const change = vi.fn();
    const props = { projectId: 'project', guide: null, prepare: async () => ({ project_id: 'project', purpose: 'video_appearance' as const, beauty_image_base64: 'source', source_video_sha256: 'a'.repeat(64) }), onChange: change, onBusyChange: vi.fn() };
    const view = render(<PhotographicVideoGuide {...props} signature="route-one" />);
    fireEvent.click(screen.getByRole('button', { name: /Create photographic guide/ }));
    await waitFor(() => expect(api.generate).toHaveBeenCalledOnce());
    view.rerender(<PhotographicVideoGuide {...props} signature="route-two" />);
    resolve(result);
    expect(await screen.findByText(/route changed.*saved.*Recover/i)).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Use this guide' })).not.toBeInTheDocument();
    expect(change).not.toHaveBeenCalled();
  });
});
