import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useViewerStore } from '@/store';
import type { ReferenceLayer } from './api';

export interface StudyMapDrawing {
  begin: (accept: (points: number[][]) => boolean, cancel: () => void) => void;
  cancel: () => void;
  preview: (layer: ReferenceLayer | null) => void;
}

/** Reuse the globe's polygon picking, touch controls and vertex undo. Complete
 * into a cartographic study, never into a building/development-area API write. */
export function useStudyMapDrawing(projectId: string | undefined) {
  const tool = useViewerStore(state => state.activeSitePlannerTool);
  const studyTool = useViewerStore(state => state.activeToolProperties?.cartography_study === true);
  const setTool = useViewerStore(state => state.setActiveSitePlannerTool);
  const pending = useRef<{ accept: (points: number[][]) => boolean; cancel: () => void } | null>(null);
  const [layer, preview] = useState<ReferenceLayer | null>(null);
  const cancel = useCallback(() => {
    const previous = pending.current;
    pending.current = null;
    if (previous) { setTool(null); previous.cancel(); }
  }, [setTool]);
  const begin = useCallback((accept: (points: number[][]) => boolean, cancelled: () => void) => {
    pending.current?.cancel();
    pending.current = { accept, cancel: cancelled };
    useViewerStore.getState().selectZone(null);
    setTool('development_area', { cartography_study: true });
  }, [setTool]);
  const complete = useCallback((points: number[][]) => {
    const current = pending.current;
    if (!current || !current.accept(points)) return false;
    pending.current = null;
    setTool(null);
    return true;
  }, [setTool]);
  useEffect(() => {
    if (tool === 'development_area' && studyTool) return;
    const previous = pending.current;
    pending.current = null;
    previous?.cancel();
  }, [tool, studyTool]);
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && pending.current) { event.preventDefault(); cancel(); }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [cancel]);
  useEffect(() => () => { pending.current = null; setTool(null); }, [projectId, setTool]);
  const controls = useMemo(() => ({ begin, cancel, preview }), [begin, cancel]);
  return { controls, complete, layer, editing: layer !== null };
}
