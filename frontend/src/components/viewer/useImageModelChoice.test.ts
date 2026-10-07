import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import { rendersApi } from '@/services/api';
import { useImageModelChoice } from './useImageModelChoice';
import { useRenderDraft } from './globe/useRenderDraft';
import { comfyTrialsApi } from '@/services/comfyTrials';
vi.mock('@/services/api', () => ({rendersApi:{imageModels:vi.fn()}}));
vi.mock('@/services/comfyTrials', () => ({comfyTrialsApi:{presets:vi.fn().mockResolvedValue({presets:[]})}}));
beforeEach(() => sessionStorage.clear());
it('adds local images beside GPT, remembers the selection, and excludes local video', async () => {
  vi.mocked(rendersApi.imageModels).mockResolvedValue({ default_model: 'gpt-image-2', models: [{ id: 'gpt-image-2', available: true }] });
  vi.mocked(comfyTrialsApi.presets).mockResolvedValue({ credit_cost: 0, presets: [
    { id: 'flux-klein', kind: 'image', available: true }, { id: 'qwen-image', kind: 'image', available: false }, { id: 'wan-video', kind: 'video', available: true },
  ] as never });
  const first = renderHook(() => useImageModelChoice({projectId:'local'}));
  await waitFor(() => expect(first.result.current.availability?.models).toHaveLength(3));
  act(() => first.result.current.setImageModel('flux-klein'));
  first.unmount();
  const reopened = renderHook(() => useImageModelChoice({projectId:'local'}));
  expect(reopened.result.current.imageModel).toBe('flux-klein');
  const masked = renderHook(() => useImageModelChoice({projectId:'local',allowLocal:false,compareByDefault:false}));
  expect(masked.result.current.imageModel).toBe('gpt-image-2');
});
it('requests one discovered default engine unless the user explicitly selects comparison', async () => {
  vi.mocked(rendersApi.imageModels).mockResolvedValue({default_model:'gpt-image-2.5-flare',models:['gpt-image-2','gpt-image-2.5-flare','gpt-image-2.5-sunburst'].map(id=>({id,available:true}))} as Awaited<ReturnType<typeof rendersApi.imageModels>>);
  const hook=renderHook(()=>useImageModelChoice({compareByDefault:false}));
  await waitFor(()=>expect(hook.result.current.availability).not.toBeNull());
  expect(hook.result.current.imageModel).toBe('gpt-image-2.5-flare');
  act(()=>hook.result.current.setImageModel('compare-all-three'));
  expect(hook.result.current.imageModel).toBe('compare-all-three');
});
it('retains the engine through panel remount and prompt edits without leaking across projects', async () => {
  const styles = ['photorealistic', 'watercolour'];
  const first = renderHook(() => ({ engine: useImageModelChoice({ projectId: 'a', compareByDefault: false }), draft: useRenderDraft('a', styles) }));
  await waitFor(() => expect(first.result.current.engine.availability).not.toBeNull());
  act(() => first.result.current.engine.setImageModel('gpt-image-2.5-sunburst'));
  act(() => first.result.current.draft.setCustomPrompt('Keep the original canal'));
  first.unmount();
  const reopened = renderHook(({ id }) => useImageModelChoice({ projectId: id, compareByDefault: false }), { initialProps: { id: 'a' } });
  expect(reopened.result.current.imageModel).toBe('gpt-image-2.5-sunburst');
  expect(JSON.parse(sessionStorage.getItem('cityprompt:render-draft:a')!).customPrompt).toBe('Keep the original canal');
  reopened.rerender({ id: 'b' });
  await waitFor(() => expect(reopened.result.current.availability).not.toBeNull());
  expect(reopened.result.current.imageModel).toBe('gpt-image-2.5-flare');
  reopened.rerender({ id: 'a' });
  expect(reopened.result.current.imageModel).toBe('gpt-image-2.5-sunburst');
});
it('preserves an explicit engine when availability changes or storage is corrupt', async () => {
  sessionStorage.setItem('cityprompt:render-draft:a', '{broken');
  vi.mocked(rendersApi.imageModels).mockResolvedValue({ default_model: 'gpt-image-2.5-flare', models: [{ id: 'gpt-image-2.5-sunburst', available: false }] });
  const first = renderHook(() => useImageModelChoice({ projectId: 'a', compareByDefault: false }));
  act(() => first.result.current.setImageModel('gpt-image-2.5-sunburst'));
  await waitFor(() => expect(first.result.current.availability).not.toBeNull());
  expect(first.result.current.imageModel).toBe('gpt-image-2.5-sunburst');
  first.unmount();
  const reopened = renderHook(() => useImageModelChoice({ projectId: 'a', compareByDefault: false }));
  expect(reopened.result.current.imageModel).toBe('gpt-image-2.5-sunburst');
});
