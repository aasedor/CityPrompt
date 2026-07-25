export interface CameraElevationBadge {
  label: string;
  color: string;
  mutedColor: string;
  textClass: string;
}

function clampDegrees(value: number, min = 0, max = 90): number {
  if (!Number.isFinite(value)) return min;
  return Math.min(max, Math.max(min, value));
}

/**
 * Convert Mapbox-style pitch / angle-from-nadir to architectural camera
 * elevation: 0deg = ground-level horizon, 90deg = straight-down overhead.
 */
export function pitchFromNadirToCameraElevation(pitchFromNadirDeg: number): number {
  return Math.round(90 - clampDegrees(pitchFromNadirDeg));
}

export function getAngleFromNadirLabelValue(pitchFromNadirDeg: number): number {
  return Math.round(clampDegrees(pitchFromNadirDeg));
}

export function getCameraElevationBadge(cameraElevationDeg: number): CameraElevationBadge {
  const angle = clampDegrees(cameraElevationDeg);

  if (angle >= 80) {
    return {
      label: 'overhead',
      color: '#38bdf8',
      mutedColor: '#bae6fd',
      textClass: 'text-sky-400',
    };
  }

  if (angle >= 60) {
    return {
      label: 'steep',
      color: '#eab308',
      mutedColor: '#fde047',
      textClass: 'text-amber-400',
    };
  }

  if (angle >= 25) {
    return {
      label: 'oblique',
      color: '#22c55e',
      mutedColor: '#86efac',
      textClass: 'text-[#138f45]',
    };
  }

  if (angle >= 5) {
    return {
      label: 'low',
      color: '#eab308',
      mutedColor: '#fde047',
      textClass: 'text-amber-400',
    };
  }

  return {
    label: 'ground',
    color: '#ef4444',
    mutedColor: '#fca5a5',
    textClass: 'text-red-400',
  };
}

export function describeCameraAngleForPrompt(pitchFromNadirDeg: number): string {
  const angleFromNadir = getAngleFromNadirLabelValue(pitchFromNadirDeg);
  const elevation = pitchFromNadirToCameraElevation(pitchFromNadirDeg);
  const suffix = `~${elevation}deg camera elevation above ground; ~${angleFromNadir}deg from nadir`;

  if (elevation >= 80) return `near top-down / nadir (${suffix})`;
  if (elevation >= 60) return `steep aerial (${suffix})`;
  if (elevation >= 25) return `oblique aerial (${suffix})`;
  if (elevation >= 5) return `low-angle oblique (${suffix})`;
  return `ground-level / horizon (${suffix})`;
}
