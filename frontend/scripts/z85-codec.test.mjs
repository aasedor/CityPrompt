import assert from 'node:assert/strict';
import { test } from 'node:test';
import { encodeZ85, decodeZ85 } from './z85-codec.mjs';

test('Z85 v1 matches the RFC32 independent network-byte-order vector', () => {
  const bytes = Uint8Array.of(0x86,0x4f,0xd2,0x6f,0xb5,0x59,0xf7,0x5b);
  assert.equal(encodeZ85(bytes), 'HelloWorld');
  assert.deepEqual(decodeZ85('HelloWorld'), bytes);
});

for (const [label, encoded, length] of [
  ['incomplete group','HelloWorl',8], ['unknown character','Hell~',4],
  ['non ASCII','Hellé',4], ['overflowing word','#####',4],
  ['negative length','00000',-1], ['oversized length','00000',5],
  ['too much padding','00000',0], ['fractional length','00000',3.5],
]) test(`Z85 rejects ${label}`, () => assert.throws(()=>decodeZ85(encoded,length),/Invalid Z85/));

test('Z85 framing refuses partial source words and nonzero application padding', () => {
  assert.throws(()=>encodeZ85(Uint8Array.of(1,2,3)),/four/);
  assert.throws(()=>decodeZ85(encodeZ85(Uint8Array.of(1,2,3,4)),3),/Invalid Z85/);
  assert.deepEqual(decodeZ85(encodeZ85(Uint8Array.of(1,2,3,0)),3),Uint8Array.of(1,2,3));
});

test('Z85 application padding preserves exact non ASCII JSON bytes before parsing', () => {
  const original = new TextEncoder().encode('{"offset":-0,"label":"é — 測試 🏙"}');
  const padded = new Uint8Array(Math.ceil(original.length / 4) * 4);
  padded.set(original);
  assert.deepEqual(decodeZ85(encodeZ85(padded),original.length),original);
});
