/**
 * useGlobeDragRef.ts — Shared mutable drag state for globe zone editing.
 *
 * During drag, coordinates are written to this ref (no React state updates).
 * GlobeZoneLayer reads the ref via useFrame to update BufferGeometry directly.
 * On drag end, final coords are committed to React state (one re-render).
 *
 * This avoids re-rendering the entire R3F scene (including millions of Google
 * 3D tile polygons) on every pointer move during drag.
 */

import { createContext, useContext, useRef } from 'react';

export interface GlobeDragState {
  /** ID of the zone currently being dragged, or null */
  zoneId: string | null;
  /** Type of drag operation */
  type: 'vertex' | 'body' | null;
  /** Index of the vertex being dragged (for vertex drag) */
  vertexIndex: number;
  /** Current polygon coordinates during drag */
  coords: [number, number][];
  /** Incremented on each update — lets useFrame skip redundant buffer writes */
  version: number;
}

export type GlobeDragRef = React.MutableRefObject<GlobeDragState>;

const GlobeDragContext = createContext<GlobeDragRef | null>(null);

export const GlobeDragProvider = GlobeDragContext.Provider;

export function useGlobeDragRef(): GlobeDragRef {
  const ref = useContext(GlobeDragContext);
  if (!ref) throw new Error('useGlobeDragRef must be used within GlobeDragProvider');
  return ref;
}

export function useCreateGlobeDragRef(): GlobeDragRef {
  return useRef<GlobeDragState>({
    zoneId: null,
    type: null,
    vertexIndex: -1,
    coords: [],
    version: 0,
  });
}
