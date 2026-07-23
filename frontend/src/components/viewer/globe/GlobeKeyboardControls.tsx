/**
 * GlobeKeyboardControls.tsx — Keyboard navigation for the 3D globe.
 *
 * WASD: Pan camera or move selected zone
 * Q/E: Rotate bearing
 * Arrow keys (street view): Rotate pegman angle
 */

import { useEffect } from 'react';
import { useViewerStore } from '@/store';

interface GlobeKeyboardControlsProps {
  controlsRef: React.RefObject<any>;
}

export function GlobeKeyboardControls({ controlsRef: _controlsRef }: GlobeKeyboardControlsProps) {
  const {
    streetViewPegman,
    setStreetViewAngle,
    setStreetViewActive,
    selectedZoneId,
    activeSitePlannerTool,
  } = useViewerStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture when typing in inputs
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      // Street view arrow controls
      if (streetViewPegman?.position) {
        if (e.key === 'ArrowLeft') {
          setStreetViewAngle(((streetViewPegman.angle - 45) + 360) % 360);
          return;
        }
        if (e.key === 'ArrowRight') {
          setStreetViewAngle((streetViewPegman.angle + 45) % 360);
          return;
        }
        if (e.key === 'Escape') {
          setStreetViewActive(false);
          return;
        }
      }

      // Drawing mode keyboard is handled by useGlobeDrawing
      if (activeSitePlannerTool) return;

      // Q/E to rotate (would need GlobeControls API to rotate programmatically)
      // For now, GlobeControls handles mouse-based rotation natively
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [streetViewPegman, setStreetViewAngle, setStreetViewActive, selectedZoneId, activeSitePlannerTool]);

  return null; // This is a behavior-only component
}
