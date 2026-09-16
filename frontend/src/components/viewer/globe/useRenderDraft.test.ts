import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useRenderDraft } from './useRenderDraft';

const styles = ['photorealistic', 'watercolour'];
beforeEach(() => { sessionStorage.clear(); vi.restoreAllMocks(); });

describe('render panel drafts', () => {
  it('defaults old drafts to no entourage and remembers only explicit selections per project', () => {
    sessionStorage.setItem('cityprompt:render-draft:a', JSON.stringify({selectedStyle:'photorealistic', customPrompt:'Add crowds', addVehicles:'true'}));
    const hook = renderHook(({id}) => useRenderDraft(id, styles), {initialProps:{id:'a'}});
    expect(hook.result.current.addPeople).toBe(false); expect(hook.result.current.addVehicles).toBe(false);
    act(() => hook.result.current.setAddPeople(true));
    hook.rerender({id:'b'}); expect(hook.result.current.addPeople).toBe(false);
    hook.unmount();
    const reopened = renderHook(() => useRenderDraft('a', styles));
    expect(reopened.result.current.addPeople).toBe(true); expect(reopened.result.current.addVehicles).toBe(false);
  });
  it('retains directions and style after closing and reopening', () => {
    const first = renderHook(() => useRenderDraft('site-a', styles));
    act(() => { first.result.current.setSelectedStyle('watercolour'); first.result.current.setCustomPrompt('Two people on the existing path'); });
    first.unmount();
    const reopened = renderHook(() => useRenderDraft('site-a', styles));
    expect(reopened.result.current.selectedStyle).toBe('watercolour');
    expect(reopened.result.current.customPrompt).toBe('Two people on the existing path');
  });
  it('does not leak directions into another project, including in-place navigation', () => {
    const hook = renderHook(({ id }) => useRenderDraft(id, styles), { initialProps: { id: 'a' } });
    act(() => hook.result.current.setCustomPrompt('Site A only'));
    hook.rerender({ id: 'b' });
    expect(hook.result.current.customPrompt).toBe('');
    act(() => hook.result.current.setCustomPrompt('Site B only'));
    hook.rerender({ id: 'a' });
    expect(hook.result.current.customPrompt).toBe('Site A only');
    expect(JSON.parse(sessionStorage.getItem('cityprompt:render-draft:b')!).customPrompt).toBe('Site B only');
  });
  it('allows editing with corrupt or unavailable storage', () => {
    sessionStorage.setItem('cityprompt:render-draft:a', '{broken');
    const hook = renderHook(() => useRenderDraft('a', styles));
    expect(hook.result.current.selectedStyle).toBe('photorealistic');
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('full'); });
    act(() => hook.result.current.setCustomPrompt('Still editable'));
    expect(hook.result.current.customPrompt).toBe('Still editable');
  });
  it('ignores obsolete styles and non-text prompts', () => {
    sessionStorage.setItem('cityprompt:render-draft:a', JSON.stringify({ selectedStyle: 'removed', customPrompt: 42 }));
    const hook = renderHook(() => useRenderDraft('a', styles));
    expect(hook.result.current.selectedStyle).toBe('photorealistic');
    expect(hook.result.current.customPrompt).toBe('');
  });
});
