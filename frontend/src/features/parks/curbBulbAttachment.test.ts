import { describe, expect, it } from 'vitest';
import evidence from './curbBulbContracts.json';
import { checkCurbBulbAttachment, transformCurbPoints, type SidewalkAttachmentHost } from './curbBulbAttachment';

const ids = Object.keys(evidence.contracts) as (keyof typeof evidence.contracts)[];
const pose = { x: 17, y: -23, angle: 37, roadHeight: 1040 };
function hostFor(id: typeof ids[number], reverse = false): SidewalkAttachmentHost {
  const curve = transformCurbPoints(evidence.contracts[id].attachment, pose);
  const points = curve.map(p => [p[0], p[1], pose.roadHeight + .15] as const);
  return { id: 'sidewalk-1', curb: reverse ? points.reverse() : points, protectedAreas: [] };
}

describe('source-bound curb-bulb attachment', () => {
  it.each(ids)('%s matches its whole authored seam at a rigid rotated pose', id => {
    const original = hostFor(id);
    const before = JSON.stringify(original);
    const match = checkCurbBulbAttachment(id, pose, original);
    expect(match.ok).toBe(true);
    if (match.ok) expect(match.remainingCurbs).toEqual([]);
    expect(JSON.stringify(original)).toBe(before);
    expect(checkCurbBulbAttachment(id, pose, hostFor(id, true)).ok).toBe(true);
  });

  it('cuts only the matched part of a longer curb and retains both adjacent sections', () => {
    const p = { x: 0, y: 0, angle: 0, roadHeight: 0 };
    const result = checkCurbBulbAttachment('curb_bulb_midblock_small_r1', p,
      { id: 'long', curb: [[-10, 0, .15], [10, 0, .15]], protectedAreas: [] });
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.remainingCurbs).toEqual([
      [[-10, 0, .15], [-3, 0, .15]], [[3, 0, .15], [10, 0, .15]],
    ]);
  });

  it('rejects a straight chord with the correct corner endpoints', () => {
    const host = hostFor('curb_bulb_single_left_small_r1');
    host.curb = [host.curb[0], host.curb[host.curb.length - 1]];
    expect(checkCurbBulbAttachment('curb_bulb_single_left_small_r1', pose, host)).toMatchObject({ ok: false, reason: 'seam' });
  });

  it('rejects a changed interior curve even when both endpoints still match', () => {
    const host = hostFor('curb_bulb_dual_corner_medium_r1');
    host.curb = host.curb.map((p, i) => i === 30 ? [p[0] + .2, p[1], p[2]] : p);
    expect(checkCurbBulbAttachment('curb_bulb_dual_corner_medium_r1', pose, host).ok).toBe(false);
  });

  it('rejects both the old 145 mm deck and a sloping seam', () => {
    const id = 'curb_bulb_midblock_small_r1';
    const host = hostFor(id);
    host.curb = host.curb.map(p => [p[0], p[1], pose.roadHeight + .145]);
    expect(checkCurbBulbAttachment(id, pose, host)).toMatchObject({ ok: false, reason: 'height' });
    host.curb = hostFor(id).curb.map((p, i) => [p[0], p[1], p[2] + i * .02]);
    expect(checkCurbBulbAttachment(id, pose, host)).toMatchObject({ ok: false, reason: 'height' });
  });

  it('rejects an access route inside the footprint and one crossing its edge', () => {
    const id = 'curb_bulb_midblock_small_r1';
    const host = hostFor(id);
    for (const area of [
      [[-.2, -.8], [.2, -.8], [.2, -.4], [-.2, -.4]],
      [[-10, -.8], [10, -.8], [10, -.7], [-10, -.7]],
    ]) {
      host.protectedAreas = [transformCurbPoints(area, pose)];
      expect(checkCurbBulbAttachment(id, pose, host)).toMatchObject({ ok: false, reason: 'access' });
    }
  });

  it('rejects missing, malformed and unknown hosts/assets without throwing', () => {
    expect(checkCurbBulbAttachment(ids[0], pose, null)).toMatchObject({ ok: false, reason: 'host' });
    expect(checkCurbBulbAttachment('unknown', pose, hostFor(ids[0])).ok).toBe(false);
    expect(checkCurbBulbAttachment(ids[0], { ...pose, angle: NaN }, hostFor(ids[0])).ok).toBe(false);
    expect(checkCurbBulbAttachment(ids[0], pose, { id: 'bad', curb: [[0, 0, NaN]], protectedAreas: [] }).ok).toBe(false);
  });
});
