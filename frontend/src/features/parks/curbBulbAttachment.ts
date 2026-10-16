import polygonClipping from 'polygon-clipping';
import evidence from './curbBulbContracts.json';

export type CurbPoint = readonly [number, number, number];
export type PlanPoint = [number, number];
export interface CurbBulbPose { x: number; y: number; angle: number; roadHeight: number }
export interface SidewalkAttachmentHost {
  id: string;
  /** Existing curb top, in a common metre ENU frame. Not a model bounding box. */
  curb: readonly CurbPoint[];
  /** Ramp/access-route footprints in that same frame. */
  protectedAreas: readonly (readonly PlanPoint[])[];
}
export type CurbAttachmentResult =
  | { ok: true; hostId: string; removedRange: [number, number]; remainingCurbs: CurbPoint[][] }
  | { ok: false; reason: 'host' | 'asset' | 'seam' | 'height' | 'access'; message: string };

const MM = .001;
const contracts = evidence.contracts as Record<string, {
  attachment: number[][]; polygon: number[][]; parameters: { height: number };
}>;

/** Source native XY equals local East/North after the app's Y-up GLB conversion. */
export function transformCurbPoints(points: readonly (readonly number[])[], pose: CurbBulbPose): PlanPoint[] {
  const angle = pose.angle * Math.PI / 180, c = Math.cos(angle), s = Math.sin(angle);
  return points.map(p => [pose.x + c * p[0] - s * p[1], pose.y + s * p[0] + c * p[1]]);
}

function lengths(points: readonly (readonly number[])[]) {
  const offsets = [0];
  for (let i = 1; i < points.length; i++)
    offsets.push(offsets[i - 1] + Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]));
  return offsets;
}

function project(p: readonly number[], path: readonly (readonly number[])[], offsets: number[]) {
  let best = { distance: Infinity, along: 0 };
  for (let i = 1; i < path.length; i++) {
    const a = path[i - 1], b = path[i], dx = b[0] - a[0], dy = b[1] - a[1];
    const square = dx * dx + dy * dy;
    if (square <= 1e-16) continue;
    const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / square));
    const distance = Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
    if (distance < best.distance) best = { distance, along: offsets[i - 1] + t * Math.sqrt(square) };
  }
  return best;
}

function at(path: readonly CurbPoint[], offsets: number[], along: number): CurbPoint {
  for (let i = 1; i < path.length; i++) {
    if (along > offsets[i] + 1e-9) continue;
    const length = offsets[i] - offsets[i - 1];
    const t = length ? Math.max(0, Math.min(1, (along - offsets[i - 1]) / length)) : 0;
    return path[i - 1].map((v, axis) => v + t * (path[i][axis] - v)) as unknown as CurbPoint;
  }
  return [...path[path.length - 1]];
}

function slice(path: readonly CurbPoint[], offsets: number[], start: number, end: number): CurbPoint[] {
  return [at(path, offsets, start), ...path.filter((_, i) => offsets[i] > start + 1e-8 && offsets[i] < end - 1e-8), at(path, offsets, end)];
}

/** Compare every vertex in both directions and require ordered traversal.
 * A chord with the same endpoints, a different radius, or a loop cannot stand in
 * for the complete source seam. Called on edits only, never in the frame loop.
 */
function follows(a: readonly (readonly number[])[], b: readonly (readonly number[])[]) {
  const offsets = lengths(b);
  let previous = -Infinity;
  for (const point of a) {
    const p = project(point, b, offsets);
    if (p.distance > MM || p.along < previous - MM) return false;
    previous = p.along;
  }
  return true;
}

/** Pure validation/cut instruction. Source model and host data are never mutated.
 * The caller must provide a real sidewalk host and apply the returned curb cut;
 * this function does not infer one from terrain, aerial imagery or a bounding box.
 */
export function checkCurbBulbAttachment(id: string, pose: CurbBulbPose, host: SidewalkAttachmentHost | null): CurbAttachmentResult {
  const fail = (reason: Extract<CurbAttachmentResult, { ok: false }>['reason'], message: string): CurbAttachmentResult => ({ ok: false, reason, message });
  const contract = Object.prototype.hasOwnProperty.call(contracts, id) ? contracts[id] : undefined;
  if (!contract) return fail('asset', 'Choose an audited curb-bulb variant.');
  if (!host?.id || host.curb.length < 2 || host.curb.some(p => p.length !== 3 || !p.every(Number.isFinite))
    || !Object.values(pose).every(Number.isFinite)) return fail('host', 'Choose a compatible authored sidewalk edge.');
  const offsets = lengths(host.curb), total = offsets[offsets.length - 1];
  if (offsets.some((v, i) => i > 0 && v - offsets[i - 1] < 1e-8)) return fail('host', 'The sidewalk edge contains an invalid segment.');
  let seam = transformCurbPoints(contract.attachment, pose);
  const first = project(seam[0], host.curb, offsets), last = project(seam[seam.length - 1], host.curb, offsets);
  const start = Math.min(first.along, last.along), end = Math.max(first.along, last.along);
  if (first.distance > MM || last.distance > MM || end - start < MM) return fail('seam', 'The complete attachment edge must match the existing sidewalk.');
  if (first.along > last.along) seam = [...seam].reverse();
  const matched = slice(host.curb, offsets, start, end);
  if (!follows(seam, matched) || !follows(matched, seam)) return fail('seam', 'This corner radius or attachment curve does not match the chosen bulb.');
  if (matched.some(p => Math.abs(p[2] - pose.roadHeight - contract.parameters.height) > MM))
    return fail('height', 'Use a level sidewalk 150 mm above the same road datum.');
  const polygon = transformCurbPoints(contract.polygon, pose);
  for (const area of host.protectedAreas) {
    if (area.length < 3 || area.some(p => p.length !== 2 || !p.every(Number.isFinite)))
      return fail('access', 'Access-route geometry must be verified before attachment.');
    if (polygonClipping.intersection([polygon], [[...area]]).length)
      return fail('access', 'This bulb conflicts with a ramp or protected access route.');
  }
  const remainingCurbs: CurbPoint[][] = [];
  if (start > MM) remainingCurbs.push(slice(host.curb, offsets, 0, start));
  if (total - end > MM) remainingCurbs.push(slice(host.curb, offsets, end, total));
  return { ok: true, hostId: host.id, removedRange: [start, end], remainingCurbs };
}
