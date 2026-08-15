export const PROJECT_FRAME_RETRY_OFFSETS_MS = [0, 120, 450, 1_200, 2_600, 4_500] as const;

export interface ProjectFrameZone {
  coordinates?: [number, number][];
}

interface PassiveGlobeHeightCorrectionOptions {
  hasProjectFrameTargets: boolean;
  hasPreferredCameraPose: boolean;
}

/**
 * GlobeControls' passive height correction raycasts every newly streamed
 * scene mesh. That is useful while exploring an empty city, but it must not
 * move a close project frame or an exact handed-off camera when higher-detail
 * Google tiles arrive after the pose was applied.
 */
export function shouldUsePassiveGlobeHeightCorrection({
  hasProjectFrameTargets,
  hasPreferredCameraPose,
}: PassiveGlobeHeightCorrectionOptions): boolean {
  return !hasProjectFrameTargets && !hasPreferredCameraPose;
}

interface RunProjectFrameRetryOptions {
  isReady: () => boolean;
  isCancelled: () => boolean;
  frame: () => Promise<boolean>;
  onFrameApplied?: () => void;
  offsetsMs?: readonly number[];
  wait?: (delayMs: number) => Promise<void>;
}

const waitForDelay = (delayMs: number) => new Promise<void>((resolve) => {
  globalThis.setTimeout(resolve, Math.max(0, delayMs));
});

/**
 * Return only finite longitude/latitude pairs from zones that can form a
 * polygon. Projects load their zones after the globe mounts, so callers can
 * safely re-evaluate this list when that delayed data arrives.
 */
export function getFrameableProjectCoordinates(
  zones: readonly ProjectFrameZone[],
): [number, number][] {
  return zones.flatMap((zone) => {
    const coordinates = (zone.coordinates ?? []).filter(([lng, lat]) => (
      Number.isFinite(lng)
      && Number.isFinite(lat)
      && Math.abs(lng) <= 180
      && Math.abs(lat) <= 90
    ));
    return coordinates.length >= 3 ? coordinates : [];
  });
}

/**
 * Apply a project-frame request immediately when possible, then repeat it on
 * a short bounded schedule. GlobeControls and terrain setup can perform one
 * final internal camera update after their refs become available; the later
 * applications ensure that update cannot undo a user's single Focus Plan
 * click. Requests remain cancellable so genuine orbit/zoom gestures always
 * take ownership of the camera.
 */
export async function runProjectFrameRetry({
  isReady,
  isCancelled,
  frame,
  onFrameApplied,
  offsetsMs = PROJECT_FRAME_RETRY_OFFSETS_MS,
  wait = waitForDelay,
}: RunProjectFrameRetryOptions): Promise<boolean> {
  let previousOffsetMs = 0;
  let applied = false;

  for (const rawOffsetMs of offsetsMs) {
    const offsetMs = Math.max(previousOffsetMs, rawOffsetMs);
    const delayMs = offsetMs - previousOffsetMs;
    previousOffsetMs = offsetMs;

    if (delayMs > 0) await wait(delayMs);
    if (isCancelled()) return applied;
    if (!isReady()) continue;

    const framed = await frame();
    if (isCancelled()) return applied;
    if (!framed) continue;

    applied = true;
    onFrameApplied?.();
  }

  return applied;
}
