import { act, renderHook } from '@testing-library/react';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import {
  announceCommunity3DPresentationReady,
  useCleanPresentationAfterCommunity3DCompile,
} from './community3dPresentation';

describe('Community 3D presentation', () => {
  it('switches a successful compile to clean 3D once, then preserves an explicit Plan Overlay choice', () => {
    const { result } = renderHook(() => {
      const [overlaysVisible, setOverlaysVisible] = useState(true);
      useCleanPresentationAfterCommunity3DCompile(setOverlaysVisible);
      return { overlaysVisible, setOverlaysVisible };
    });

    act(() => {
      announceCommunity3DPresentationReady(['building-1', 'park-1', 'street-1']);
    });
    expect(result.current.overlaysVisible).toBe(false);

    act(() => {
      result.current.setOverlaysVisible(true);
    });
    expect(result.current.overlaysVisible).toBe(true);
  });

  it('does not alter overlay state before a successful compile is announced', () => {
    const { result } = renderHook(() => {
      const [overlaysVisible, setOverlaysVisible] = useState(true);
      useCleanPresentationAfterCommunity3DCompile(setOverlaysVisible);
      return overlaysVisible;
    });

    expect(result.current).toBe(true);
  });

  it('opens an already-compiled project in clean 3D without overriding a later Plan Overlay choice', () => {
    const { result, rerender } = renderHook(
      ({ hasCompiledCommunity }) => {
        const [overlaysVisible, setOverlaysVisible] = useState(true);
        useCleanPresentationAfterCommunity3DCompile(
          setOverlaysVisible,
          hasCompiledCommunity,
        );
        return { overlaysVisible, setOverlaysVisible };
      },
      { initialProps: { hasCompiledCommunity: false } },
    );

    rerender({ hasCompiledCommunity: true });
    expect(result.current.overlaysVisible).toBe(false);

    act(() => {
      result.current.setOverlaysVisible(true);
    });
    rerender({ hasCompiledCommunity: true });
    expect(result.current.overlaysVisible).toBe(true);
  });
});
