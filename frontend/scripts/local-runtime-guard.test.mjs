import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { applyLocalRuntimeProfile, verifyLocalRuntime, localRuntimeGuard } from './local-runtime-guard.mjs';

test('missing Maps configuration blocks startup without invoking the catalogue or printing credentials', async () => {
  let calls = 0;
  await assert.rejects(verifyLocalRuntime({ VITE_GOOGLE_MAPS_API_KEY: '  ', OTHER_SECRET: 'secret' }, async () => calls++), /VITE_GOOGLE_MAPS_API_KEY is missing/);
  assert.equal(calls, 0);
});

test('valid key configuration still fails on missing catalogue assets', async () => {
  await assert.rejects(verifyLocalRuntime({ VITE_GOOGLE_MAPS_API_KEY: 'test-key' }, async () => { throw new Error('Missing park preview'); }), /Missing park preview/);
  let calls = 0;
  await verifyLocalRuntime({ VITE_GOOGLE_MAPS_API_KEY: 'test-key' }, async () => calls++);
  assert.equal(calls, 1);
});

test('worktree runtime profile applies together and preserves explicit overrides', t => {
  const root = mkdtempSync(join(tmpdir(), 'cityprompt-runtime-'));
  t.after(() => {
    assert.equal(dirname(resolve(root)), resolve(tmpdir()));
    assert.ok(basename(root).startsWith('cityprompt-runtime-'));
    rmSync(root, { recursive: true, force: true });
  });
  mkdirSync(join(root, 'artifacts'));
  const profile = { schema: 'cityprompt.local-runtime@1', envDir: root, cataloguePacket: root, apiProxyTarget: 'http://127.0.0.1:8011', port: 5181 };
  writeFileSync(join(root, 'artifacts/local-runtime.json'), JSON.stringify(profile));
  const env = { VITE_ENV_DIR: 'explicit-test-environment' };
  assert.equal(applyLocalRuntimeProfile(root, env).port, 5181);
  assert.equal(env.VITE_ENV_DIR, 'explicit-test-environment');
  assert.equal(env.CITYPROMPT_CATALOGUE_PACKET, root);
  assert.equal(env.API_PROXY_TARGET, profile.apiProxyTarget);
});

test('module-only catalogue audits skip the server guard to avoid recursion', async () => {
  await localRuntimeGuard().configureServer({ config: { server: { middlewareMode: true }, env: {} } });
  await assert.rejects(localRuntimeGuard().configureServer({ config: { server: {}, env: {} } }), /VITE_GOOGLE_MAPS_API_KEY is missing/);
});
