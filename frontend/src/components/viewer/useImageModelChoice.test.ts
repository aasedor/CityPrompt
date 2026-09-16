import { act, renderHook, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { rendersApi } from '@/services/api';
import { useImageModelChoice } from './useImageModelChoice';
vi.mock('@/services/api', () => ({rendersApi:{imageModels:vi.fn()}}));
it('requests one discovered default engine unless the user explicitly selects comparison', async () => {
  vi.mocked(rendersApi.imageModels).mockResolvedValue({default_model:'gpt-image-2.5-flare',models:['gpt-image-2','gpt-image-2.5-flare','gpt-image-2.5-sunburst'].map(id=>({id,available:true}))} as Awaited<ReturnType<typeof rendersApi.imageModels>>);
  const hook=renderHook(()=>useImageModelChoice({compareByDefault:false}));
  await waitFor(()=>expect(hook.result.current.availability).not.toBeNull());
  expect(hook.result.current.imageModel).toBe('gpt-image-2.5-flare');
  act(()=>hook.result.current.setImageModel('compare-all-three'));
  expect(hook.result.current.imageModel).toBe('compare-all-three');
});
