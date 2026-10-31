import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer, build } from 'vite';

const FRONTEND = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PUBLIC_VALUES = {
  VITE_API_URL: 'https://api.synthetic.example',
  VITE_GOOGLE_MAPS_API_KEY: 'synthetic-public-maps',
  VITE_MAPBOX_TOKEN: 'synthetic-public-mapbox',
  VITE_SENTRY_DSN: 'https://public@synthetic.example/1',
  VITE_KTX2_TRANSCODER_PATH: '/synthetic-basis/',
  VITE_CLAUDE_FIVE_TRIAL: 'true',
  VITE_CONTEXT_PILOT: 'true',
  VITE_ENABLE_CLASSIC_POLYGON_RENDER: 'true',
  VITE_ENABLE_LEGACY_SITE_BOUNDARY_TOOLS: 'true',
  VITE_ENABLE_RENDER_PANEL_COMMUNITY_3D_TOOLS: 'true',
  VITE_PARK_KIT_ASSETS_READY: 'true',
};
const PRIVATE_VALUES = {
  VITE_FAL_KEY: 'SYNTHETIC_FAL_CANARY',
  VITE_PRIVATE_PROVIDER_KEY: 'SYNTHETIC_PRIVATE_PROVIDER_CANARY',
  VITE_API_URL_PRIVATE_KEY: 'SYNTHETIC_PREFIX_MATCH_CANARY',
  VITE_ENV_DIR: 'SYNTHETIC_CONFIGURATION_PATH_CANARY',
};

function fixture(t, source) {
  const root = fs.mkdtempSync(join(tmpdir(), 'cityprompt-public-env-'));
  t.after(() => {
    assert.equal(dirname(resolve(root)), resolve(tmpdir()));
    assert.ok(basename(root).startsWith('cityprompt-public-env-'));
    fs.rmSync(root, { recursive: true, force: true });
  });
  // Protect the desktop dotenv boundary even while testing the existing config.
  const read = fs.readFileSync;
  t.mock.method(fs, 'readFileSync', function (path, ...args) {
    const filename = typeof path === 'string' ? resolve(path) : path instanceof URL ? fileURLToPath(path) : '';
    if (filename && basename(filename).startsWith('.env') && dirname(filename) !== root) {
      throw new Error('Synthetic test refuses non-fixture dotenv reads');
    }
    return read.call(this, path, ...args);
  });
  const before = { ...process.env };
  t.after(() => {
    for (const name of Object.keys(process.env)) if (!(name in before)) delete process.env[name];
    Object.assign(process.env, before);
  });
  for (const name of Object.keys(process.env)) if (name.startsWith('VITE_')) delete process.env[name];
  process.env.VITE_ENV_DIR = root;
  process.env.NODE_ENV = 'development';
  const values = { ...PUBLIC_VALUES, ...PRIVATE_VALUES };
  delete values.VITE_ENV_DIR;
  if (source === 'dotenv') {
    fs.writeFileSync(join(root, '.env'), Object.entries(values).map(([key, value]) => `${key}=${value}`).join('\n'));
  } else {
    Object.assign(process.env, values);
  }
  fs.writeFileSync(join(root, 'entry.js'), 'export const environment = import.meta.env;\nexport const maps = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;');
  return root;
}

for (const source of ['process', 'dotenv']) {
  test(`dev modules expose only approved public settings from ${source}`, async t => {
    const root = fixture(t, source);
    const server = await createServer({
      configFile: join(FRONTEND, 'vite.config.ts'), root, mode: 'test',
      cacheDir: join(root, 'cache'), publicDir: false,
      server: { middlewareMode: true, watch: null, hmr: false },
      optimizeDeps: { noDiscovery: true },
      plugins: [{
        name: 'synthetic-environment-fixture', enforce: 'post',
        config(config) { config.optimizeDeps.include = []; },
      }],
    });
    t.after(() => server.close());
    const transformed = await server.transformRequest('/entry.js');
    for (const value of Object.values(PRIVATE_VALUES)) assert.ok(!transformed.code.includes(value));
    assert.ok(!transformed.code.includes(root), 'Configuration directory must not become browser environment');
    const client = await import(`data:text/javascript;base64,${Buffer.from(transformed.code).toString('base64')}`);
    assert.deepEqual(Object.fromEntries(Object.keys(PUBLIC_VALUES).map(key => [key, client.environment[key]])), PUBLIC_VALUES);
    assert.equal(client.maps, PUBLIC_VALUES.VITE_GOOGLE_MAPS_API_KEY);
    assert.equal(client.environment.MODE, 'test');
    assert.equal(client.environment.DEV, true);
    assert.equal(client.environment.PROD, false);
    assert.equal(client.environment.BASE_URL, '/');
    for (const key of Object.keys(PRIVATE_VALUES)) assert.equal(client.environment[key], undefined);
  });
}

test('production environment objects retain public settings without private canaries', async t => {
  const root = fixture(t, 'dotenv');
  process.env.NODE_ENV = 'production';
  const result = await build({
    configFile: join(FRONTEND, 'vite.config.ts'), root, mode: 'test',
    cacheDir: join(root, 'cache'), publicDir: false,
    build: { write: false, minify: false, lib: { entry: join(root, 'entry.js'), formats: ['es'] } },
  });
  const chunk = (Array.isArray(result) ? result : [result]).flatMap(item => item.output).find(item => item.type === 'chunk');
  for (const value of Object.values(PRIVATE_VALUES)) assert.ok(!chunk.code.includes(value));
  assert.ok(!chunk.code.includes(root));
  const client = await import(`data:text/javascript;base64,${Buffer.from(chunk.code).toString('base64')}`);
  assert.deepEqual(Object.fromEntries(Object.keys(PUBLIC_VALUES).map(key => [key, client.environment[key]])), PUBLIC_VALUES);
  assert.equal(client.environment.PROD, true);
});

test('public environment fixture covers every named application consumer', () => {
  const found = new Set();
  for (const path of fs.readdirSync(join(FRONTEND, 'src'), { recursive: true })) {
    if (!/\.(?:ts|tsx|js|mjs)$/.test(path)) continue;
    const source = fs.readFileSync(join(FRONTEND, 'src', path), 'utf8');
    for (const match of source.matchAll(/import\.meta\.env\.(VITE_[A-Z0-9_]+)/g)) found.add(match[1]);
  }
  assert.deepEqual([...found].sort(), Object.keys(PUBLIC_VALUES).sort());
});
