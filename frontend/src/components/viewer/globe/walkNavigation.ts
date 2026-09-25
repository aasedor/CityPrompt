export interface WalkPose {
  lng: number;
  lat: number;
  groundHeight: number;
  heading: number;
}

const METERS_PER_DEG_LAT = 111_320;
const WALK_SPEED_METERS_PER_SECOND = 2.2;
const TURN_DEGREES_PER_SECOND = 100;

/** Keep the walk camera at pedestrian speed and on a level ground plane. */
export function advanceWalkPose(pose: WalkPose, keys: ReadonlySet<string>, elapsedSeconds: number): WalkPose {
  const dt = Math.min(Math.max(elapsedSeconds, 0), 0.05);
  const turn = Number(keys.has('arrowright')) - Number(keys.has('arrowleft'));
  const heading = (pose.heading + turn * TURN_DEGREES_PER_SECOND * dt + 360) % 360;
  const forward = Number(keys.has('w') || keys.has('arrowup')) - Number(keys.has('s') || keys.has('arrowdown'));
  const strafe = Number(keys.has('d')) - Number(keys.has('a'));
  if (!forward && !strafe && !turn) return pose;
  const direction = heading * Math.PI / 180;
  const length = Math.max(1, Math.hypot(forward, strafe));
  const distance = WALK_SPEED_METERS_PER_SECOND * (keys.has('shift') ? 1.7 : 1) * dt / length;
  const north = (Math.cos(direction) * forward - Math.sin(direction) * strafe) * distance;
  const east = (Math.sin(direction) * forward + Math.cos(direction) * strafe) * distance;
  return { ...pose, heading, lat: pose.lat + north / METERS_PER_DEG_LAT,
    lng: pose.lng + east / Math.max(1, METERS_PER_DEG_LAT * Math.cos(pose.lat * Math.PI / 180)) };
}

export function lookWalkPose(pose: WalkPose, deltaX: number): WalkPose {
  return { ...pose, heading: (pose.heading + deltaX * 0.18 + 360) % 360 };
}
