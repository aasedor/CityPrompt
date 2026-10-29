// @ts-expect-error -- Vitest provides Node; production tsconfig is browser-only.
import { readFileSync, existsSync } from 'node:fs';
// @ts-expect-error -- Vitest provides Node; production tsconfig is browser-only.
import path from 'node:path';
// @ts-expect-error -- Vitest provides Node; production tsconfig is browser-only.
import process from 'node:process';
import { describe, expect, it } from 'vitest';
import { Texture, Vector3 } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import catalogue from './peopleCatalogue.json';
import { createPeopleActor } from './peopleAnimation';
import { createPeopleActionPose } from './peoplePose';

// Local visual assets may be external to an isolated source checkout. CI with
// hydrated public assets runs the same real rig tests; pointers are not models.
const publicRoot = process.env.CITYPROMPT_PUBLIC_DIR ?? path.resolve('public');
const hydrated = catalogue.every(row => {
  const file = path.join(publicRoot, row.url);
  return existsSync(file) && readFileSync(file).readUInt32LE(0) === 0x46546c67;
});
describe.skipIf(!hydrated)('actual catalogue arm rigs (requires hydrated CITYPROMPT_PUBLIC_DIR)', () => {
  it.each(catalogue)('$id keeps action elbows on their anatomical side and preserves arm lengths', async row => {
    const bytes = readFileSync(path.join(publicRoot, row.url));
    const loader = new GLTFLoader();
    // Texture decoding is unrelated to the exact geometry, bones and clips.
    loader.register(() => ({ name: 'offline-textures', loadTexture: async () => new Texture() }));
    const buffer = new ArrayBuffer(bytes.byteLength); new Uint8Array(buffer).set(bytes);
    const gltf = await loader.parseAsync(buffer, '');
    const actor = createPeopleActor(gltf.scene, gltf.animations, row.people);
    const point = (name: string) => actor.root.worldToLocal(actor.root.getObjectByName(name)!.getWorldPosition(new Vector3()));
    actor.pose(0, 'idle');
    let pelvis = actor.root.getObjectByName('pelvis')!;
    while ((pelvis.parent as { isBone?: boolean })?.isBone) pelvis = pelvis.parent!;
    const rigPoint = (name: string) => pelvis.parent!.worldToLocal(actor.root.getObjectByName(name)!.getWorldPosition(new Vector3()));
    const signs = { l: Math.sign(point('upperarm_l').x), r: Math.sign(point('upperarm_r').x) };
    const lengths = Object.fromEntries(['l', 'r'].map(side => [side, [
      rigPoint(`upperarm_${side}`).distanceTo(rigPoint(`lowerarm_${side}`)),
      rigPoint(`lowerarm_${side}`).distanceTo(rigPoint(`hand_${side}`)),
    ]]));
    const pose = createPeopleActionPose(actor);
    for (const action of ['sitting', 'waving', 'pointing', 'reading', 'using_phone', 'talking', 'stretching', 'cheering', 'dancing', 'waiting'] as const) {
      for (const seconds of [0, .5, 1]) {
        pose.sample(action, seconds, true);
        for (const side of ['l', 'r'] as const) {
          const elbow = point(`lowerarm_${side}`), hand = point(`hand_${side}`);
          expect(elbow.x * signs[side], `${row.id}/${action}/${side} elbow crosses chest`).toBeGreaterThan(.12);
          expect(rigPoint(`upperarm_${side}`).distanceTo(rigPoint(`lowerarm_${side}`))).toBeCloseTo(lengths[side][0], 5);
          expect(rigPoint(`lowerarm_${side}`).distanceTo(rigPoint(`hand_${side}`))).toBeCloseTo(lengths[side][1], 5);
          if (['waving', 'pointing', 'talking', 'using_phone'].includes(action) && side === 'r') {
            expect(hand.x * signs[side], `${action} hand crosses midline`).toBeGreaterThan(.03);
          }
        }
      }
    }
    actor.dispose();
  }, 30000);
});
