import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';

const script = fileURLToPath(new URL('./check-landing-media.mjs', import.meta.url));
const names = ['kensington-aerial.png', 'kensington-context.png', 'tree-lined-street.png', 'tree-lined-street.mp4'];
const png = Buffer.from('89504e470d0a1a0a0000000d494844520000000100000001', 'hex');
const mp4 = Buffer.from('000000186674797069736f6d0000020069736f6d69736f32', 'hex');

function fixture(run) {
  const directory = mkdtempSync(join(tmpdir(), 'cityprompt-landing-media-'));
  try {
    for (const name of names) writeFileSync(join(directory, name), name.endsWith('.png') ? png : mp4);
    run(directory);
  } finally { rmSync(directory, { recursive: true, force: true }); }
}

function check(directory) {
  return spawnSync(process.execPath, [script, directory], { encoding: 'utf8' });
}

test('prebuild accepts hydrated PNG and MP4 landing media', () => fixture(directory => {
  const result = check(directory);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /4 hydrated/);
}));

test('accepts the existing context capture JPEG bytes under its tracked PNG filename', () => fixture(directory => {
  writeFileSync(join(directory, 'kensington-context.png'), Buffer.from('ffd8ffe000104a46494600010100000100010000ffd9', 'hex'));
  const result = check(directory);
  assert.equal(result.status, 0, result.stderr);
}));

test('prebuild rejects each landing LFS pointer with an actionable filename', () => {
  for (const name of names) fixture(directory => {
    writeFileSync(join(directory, name), 'version https://git-lfs.github.com/spec/v1\noid sha256:' + 'a'.repeat(64) + '\nsize 1000\n');
    const result = check(directory);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Unhydrated Git LFS pointer/);
    assert.ok(result.stderr.includes(name));
  });
});

test('prebuild rejects corrupt media and missing required media', () => {
  for (const name of names) fixture(directory => {
    writeFileSync(join(directory, name), 'invalid media');
    const corrupt = check(directory);
    assert.notEqual(corrupt.status, 0);
    assert.match(corrupt.stderr, /Invalid landing media/);
    assert.ok(corrupt.stderr.includes(name));
    rmSync(join(directory, name));
    const missing = check(directory);
    assert.notEqual(missing.status, 0);
    assert.ok(missing.stderr.includes(name));
  });
});
