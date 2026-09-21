import type { Object3D } from 'three';

export function assertStreetGroundReady(scene: Object3D | null): void {
  const status = streetGroundCaptureStatus(scene);
  if (status !== 'ready') throw new Error(status === 'sampling'
    ? 'The road connection is still aligning with the ground. Keep the site in view and try again once it finishes.'
    : 'The road connection could not be measured completely. Check its position on clear ground, then reload to retry. Your design is saved.');
}

export function streetGroundCaptureStatus(scene: Object3D | null): 'ready' | 'sampling' | 'unavailable' {
  let status: 'ready' | 'sampling' | 'unavailable' = 'ready';
  scene?.traverse(object => {
    const value = object.userData.streetGroundStatus;
    if (value === 'unavailable') status = 'unavailable';
    else if (value === 'sampling' && status !== 'unavailable') status = 'sampling';
  });
  return status;
}
