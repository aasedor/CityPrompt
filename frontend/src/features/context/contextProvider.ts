/** Visual context never owns proposal coordinates, heights or the camera. */
export interface ContextProviderDefinition {
  id: string;
  kind: '3d-tiles';
  projectId: string;
  tilesetPath: '/context-pilot/tileset.json';
  attribution: string;
  licenseUrl: string;
  /** This bounded pilot has an explicit artificial ENU placement, not a survey. */
  registration: 'local-engineering-test';
  groundAuthority: 'saved-project';
}

export type ContextView = 'google' | 'capture' | 'terrain';

/** Only the fixed, locally curated development fixture can enter this pilot.
 * There is no arbitrary URL, upload or production dataset importer here. */
export function readContextPilot(value: unknown, projectId: string): ContextProviderDefinition | null {
  if (!value || typeof value !== 'object') return null;
  const v = value as Record<string, unknown>;
  if (v.id !== 'drone-building-scans-flat-roof' || v.kind !== '3d-tiles' || v.projectId !== projectId
    || v.tilesetPath !== '/context-pilot/tileset.json' || v.registration !== 'local-engineering-test'
    || v.groundAuthority !== 'saved-project' || v.licenseUrl !== 'https://creativecommons.org/licenses/by/4.0/'
    || typeof v.attribution !== 'string' || !v.attribution.trim() || v.attribution.length > 500) return null;
  return { id: v.id, kind: '3d-tiles', projectId, tilesetPath: v.tilesetPath,
    registration: v.registration, groundAuthority: v.groundAuthority, attribution: v.attribution, licenseUrl: v.licenseUrl };
}

export function visibleContext(requested: ContextView, captureReady: boolean, captureFailed: boolean): ContextView {
  return requested === 'capture' && (!captureReady || captureFailed) ? 'google' : requested;
}

export function contextPilotCaptureProblem(provider: ContextProviderDefinition | null, requested: ContextView): string | null {
  return provider && requested !== 'google'
    ? 'Sample context is for interactive testing. Switch to Google 3D before rendering.' : null;
}
