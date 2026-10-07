import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { test } from 'node:test';

const directory = new URL('../public/render-style-examples/', import.meta.url);
const manifest = JSON.parse(readFileSync(new URL('manifest.json', directory), 'utf8'));

test('saved render examples retain the recorded PNGs and their original 3D sources', () => {
  assert.equal(manifest.schema, 'cityprompt.render-style-examples@1');
  assert.deepEqual(manifest.examples.map(example => example.style_id), ['photomontage', 'watercolour', 'charcoal']);
  for (const example of manifest.examples) {
    assert.deepEqual(example.files.map(file => file.role), ['output', 'source']);
    for (const file of example.files) {
      assert.equal(file.file, `${example.style_id}-${file.role}.png`);
      const bytes = readFileSync(fileURLToPath(new URL(file.file, directory)));
      assert.equal(bytes.length, file.bytes);
      assert.equal(createHash('sha256').update(bytes).digest('hex'), file.sha256);
      assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
      assert.ok(bytes.readUInt32BE(16) > 0 && bytes.readUInt32BE(20) > 0);
    }
  }
});
