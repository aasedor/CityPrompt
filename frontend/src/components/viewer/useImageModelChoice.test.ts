import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import { rendersApi } from '@/services/api';
import { useImageModelChoice } from './useImageModelChoice';
import { useRenderDraft } from './globe/useRenderDraft';
vi.mock('@/services/api', () => ({rendersApi:{imageModels:vi.fn()}}));
beforeEach(() => {
  sessionStorage.clear();
  vi.mocked(rendersApi.imageModels).mockReset().mockResolvedValue({ default_model: 'gpt-image-2', models: [] });
});
it('clears stale account credit metadata immediately and ignores an earlier account response', async () => {
  let resolveFirst!: (value: Awaited<ReturnType<typeof rendersApi.imageModels>>) => void;
  let resolveSecond!: (value: Awaited<ReturnType<typeof rendersApi.imageModels>>) => void;
  vi.mocked(rendersApi.imageModels)
    .mockResolvedValue({ default_model: 'gpt-image-2', credit_balance: 100, credit_exempt: false, models: [] })
    .mockImplementationOnce(() => new Promise(resolve => { resolveFirst = resolve; }))
    .mockImplementationOnce(() => new Promise(resolve => { resolveSecond = resolve; }));
  const hook = renderHook(({ revision }) => useImageModelChoice({ compareByDefault: false, accountRevision: revision }), { initialProps: { revision: 'first:100:editor' } });
  hook.rerender({ revision: 'second:0:editor' });
  expect(hook.result.current.availability).toBeNull();
  await act(async () => resolveFirst({ default_model: 'gpt-image-2', credit_balance: 100, credit_exempt: false, models: [{ id: 'gpt-image-2', available: true, minimum_credit_cost: 33 }] }));
  expect(hook.result.current.availability).toBeNull();
  await act(async () => resolveSecond({ default_model: 'gpt-image-2', credit_balance: 0, credit_exempt: false, models: [{ id: 'gpt-image-2', available: true, minimum_credit_cost: 33 }] }));
  expect(hook.result.current.availability?.credit_balance).toBe(0);
  hook.rerender({ revision: 'second:100:editor' });
  expect(hook.result.current.availability).toBeNull();
});
it('remembers an explicitly selected Google engine without changing the default engine',async()=>{
  vi.mocked(rendersApi.imageModels).mockResolvedValue({default_model:'gpt-image-2',models:[{id:'gemini-nano-banana-2.1',available:true}]});
  const first=renderHook(()=>useImageModelChoice({projectId:'google',compareByDefault:false}));
  await waitFor(()=>expect(first.result.current.availability).not.toBeNull());
  expect(first.result.current.imageModel).toBe('gpt-image-2');
  act(()=>first.result.current.setImageModel('gemini-nano-banana-2.1'));
  first.unmount();
  const next=renderHook(()=>useImageModelChoice({projectId:'google',compareByDefault:false}));
  expect(next.result.current.imageModel).toBe('gemini-nano-banana-2.1');
  await waitFor(()=>expect(next.result.current.availability).not.toBeNull());
});
it.each(['flux-klein', 'qwen-image'])('replaces a retired %s draft with the discovered default without submitting a render', async model => {
  sessionStorage.setItem('cityprompt:render-draft:retired', JSON.stringify({ imageModel: model, customPrompt: 'Keep the brick facade' }));
  vi.mocked(rendersApi.imageModels).mockResolvedValue({ default_model: 'gpt-image-2.5-sunburst', models: [{ id: 'gpt-image-2.5-sunburst', available: true }] });
  const hook = renderHook(() => useImageModelChoice({ projectId: 'retired', compareByDefault: false }));
  expect(hook.result.current.imageModel).toBe('gpt-image-2');
  await waitFor(() => expect(hook.result.current.imageModel).toBe('gpt-image-2.5-sunburst'));
  expect(rendersApi.imageModels).toHaveBeenCalledOnce();
  expect(JSON.parse(sessionStorage.getItem('cityprompt:render-draft:retired')!).customPrompt).toBe('Keep the brick facade');
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
  vi.mocked(rendersApi.imageModels).mockResolvedValue({ default_model: 'gpt-image-2.5-flare', models: [{ id: 'gpt-image-2.5-flare', available: true }] });
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
it('does not invent a balance when discovery fails', async () => {
  vi.mocked(rendersApi.imageModels).mockRejectedValue(new Error('server unavailable'));
  const hook = renderHook(() => useImageModelChoice({ compareByDefault: false, accountRevision: 'editor:0:editor' }));
  await waitFor(() => expect(hook.result.current.availability).not.toBeNull());
  expect(hook.result.current.availability?.credit_balance).toBeUndefined();
  expect(hook.result.current.availability?.credit_exempt).toBeUndefined();
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

it.each([null, [], {}, {default_model:'gpt-image-2',models:null},
  {default_model:'gpt-image-2',models:[null]},
  {default_model:'unknown-engine',models:[],credit_balance:999,credit_exempt:true}])(
  'keeps the project usable when discovery returns malformed metadata %j', async response => {
    vi.mocked(rendersApi.imageModels).mockResolvedValue(response as unknown as Awaited<ReturnType<typeof rendersApi.imageModels>>);
    const hook=renderHook(()=>useImageModelChoice({compareByDefault:false}));
    await waitFor(()=>expect(hook.result.current.availability).toEqual({default_model:'gpt-image-2',models:[]}));
    expect(hook.result.current.imageModel).toBe('gpt-image-2');
    expect(hook.result.current.availability?.credit_balance).toBeUndefined();
    expect(hook.result.current.availability?.credit_exempt).toBeUndefined();
  },
);
