import type { Object3D, Vector3 } from 'three';

export const PEOPLE_CAPTURE_KEY = 'cityPromptPeopleCapture';
export interface PeopleCaptureActor { pose(seconds: number): void; restore(): void; focus?: () => Vector3 }

/** A capture owns only temporary motion, never the saved detail placement. */
export function beginPeopleCapture(scene: Object3D, enabled: boolean) {
  const liveActors = () => {
    const actors = new Map<string, PeopleCaptureActor>();
    if (enabled) scene.traverseVisible(object => {
      const actor = object.userData[PEOPLE_CAPTURE_KEY] as PeopleCaptureActor | undefined;
      if (!actor) return;
      const id = String(object.userData.projectDetailId ?? object.uuid);
      if (actors.has(id)) throw new Error('A duplicate person identity prevents a reliable video capture.');
      actors.set(id, actor);
    });
    return actors;
  };
  const originalActors = liveActors();
  const ids = [...originalActors.keys()];
  const current = () => {
    const actors = liveActors();
    if (actors.size !== ids.length || ids.some(id => !actors.has(id))) {
      throw new Error('The placed people changed during capture. Prepare the route again.');
    }
    return actors;
  };
  let restored = false;
  return {
    count: ids.length,
    pose(seconds: number) {
      if (!Number.isFinite(seconds) || seconds < 0) throw new Error('People capture time must be finite and nonnegative.');
      if (!restored) current().forEach(actor => actor.pose(seconds));
    },
    focus() { return current().get(ids[0])?.focus?.() ?? null; },
    restore() {
      if (restored) return;
      restored = true;
      // Restore all actors even if a layer was removed during cancellation.
      let failure: unknown;
      const all = new Set(originalActors.values());
      // Cleanup must still run when duplicate/changed IDs caused the failure.
      if (enabled) scene.traverseVisible(object => {
        const actor = object.userData[PEOPLE_CAPTURE_KEY] as PeopleCaptureActor | undefined;
        if (actor) all.add(actor);
      });
      for (const actor of all) { try { actor.restore(); } catch (error) { failure ??= error; } }
      if (failure) throw failure;
    },
  };
}

/** React may replace a terrain-grounded rig during the awaited frame. Re-resolve
 * its absolute pose and tracking target immediately before the encoded draw. */
export async function renderPeopleCaptureFrame(
  capture: Pick<ReturnType<typeof beginPeopleCapture>, 'pose'>,
  seconds: number,
  applyCamera: () => void,
  settle: () => Promise<void>,
  render: () => void,
) {
  capture.pose(seconds); applyCamera();
  await settle();
  capture.pose(seconds); applyCamera(); render();
}
