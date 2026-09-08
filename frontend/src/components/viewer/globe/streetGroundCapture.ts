import type { Object3D } from 'three';

export function streetGroundCaptureStatus(scene: Object3D | null): 'ready' | 'sampling' | 'unavailable' {
  let status: 'ready' | 'sampling' | 'unavailable' = 'ready';
  scene?.traverse(object => {
    const value = object.userData.streetGroundStatus;
    if (value === 'unavailable') status = 'unavailable';
    else if (value === 'sampling' && status !== 'unavailable') status = 'sampling';
  });
  return status;
}
