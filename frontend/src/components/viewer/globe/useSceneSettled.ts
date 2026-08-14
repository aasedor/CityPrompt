/**
 * useSceneSettled.ts — Detects when Google 3D Tiles have finished loading.
 *
 * Monitors the TilesRenderer loading state and applies a debounce:
 * isSettled = true only after isLoading stays false for 500ms.
 *
 * Usage: Place <SceneSettledMonitor> inside <TilesRenderer> tree,
 * pass a callback to receive settlement state changes.
 */

import { useEffect, useRef } from 'react';
import { useContext } from 'react';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import {
  type SceneTileRenderer,
  waitForTileDisplayReady,
} from './tileLoadReadiness';

interface SceneSettledMonitorProps {
  onSettledChange: (settled: boolean) => void;
  onDisplayReadyChange?: (ready: boolean) => void;
  debounceMs?: number;
}

/**
 * R3F component that monitors TilesRenderer loading state.
 * Must be placed inside <TilesRenderer> tree to access context.
 */
export function SceneSettledMonitor({
  onSettledChange,
  onDisplayReadyChange,
  debounceMs = 500,
}: SceneSettledMonitorProps) {
  const tiles = useContext(TilesRendererContext);
  const settledTimerRef = useRef<number | null>(null);
  const lastSettledRef = useRef(false);

  useEffect(() => {
    if (!tiles) return;

    const notify = (settled: boolean) => {
      if (settled !== lastSettledRef.current) {
        lastSettledRef.current = settled;
        onSettledChange(settled);
      }
    };

    const handleLoadEnd = () => {
      // Debounce: wait for stability before declaring settled
      if (settledTimerRef.current) clearTimeout(settledTimerRef.current);
      settledTimerRef.current = window.setTimeout(() => {
        notify(true);
      }, debounceMs);
    };

    const handleLoadStart = () => {
      if (settledTimerRef.current) {
        clearTimeout(settledTimerRef.current);
        settledTimerRef.current = null;
      }
      notify(false);
    };

    tiles.addEventListener('tiles-load-end', handleLoadEnd);
    tiles.addEventListener('tiles-load-start', handleLoadStart);

    // Check initial state. isLoading exists at runtime (TilesRendererBase.js)
    // but is missing from the package's type declarations.
    if (!(tiles as unknown as { isLoading?: boolean }).isLoading) {
      handleLoadEnd();
    }

    return () => {
      tiles.removeEventListener('tiles-load-end', handleLoadEnd);
      tiles.removeEventListener('tiles-load-start', handleLoadStart);
      if (settledTimerRef.current) clearTimeout(settledTimerRef.current);
    };
  }, [tiles, onSettledChange, debounceMs]);

  useEffect(() => {
    if (!onDisplayReadyChange) return;
    onDisplayReadyChange(false);
    if (!tiles) return;

    const sceneTiles = tiles as unknown as SceneTileRenderer;
    let cancelled = false;
    let retryTimer: number | null = null;

    const checkVisibleCoverage = () => {
      void waitForTileDisplayReady(sceneTiles).then((ready) => {
        if (cancelled) return;
        if (ready) {
          onDisplayReadyChange(true);
          return;
        }
        // An empty renderer must not falsely settle, but it may simply be on a
        // slow connection. Keep checking at a low cadence until content arrives.
        retryTimer = window.setTimeout(checkVisibleCoverage, 500);
      });
    };

    checkVisibleCoverage();
    return () => {
      cancelled = true;
      if (retryTimer !== null) window.clearTimeout(retryTimer);
    };
  }, [onDisplayReadyChange, tiles]);

  // This component renders nothing — it's just a monitor
  return null;
}
