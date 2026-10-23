import assert from 'node:assert/strict';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

for (const [mode, dev, containsTrial] of [
  ['production', false, false],
  ['test', true, false],
  ['development', true, true],
]) {
  test(`local Claude data is ${containsTrial ? 'retained' : 'absent'} in ${mode} bundles`, async () => {
    const result = await build({
      stdin: {
        contents: "export { LOCAL_CLAUDE_ASSETS, LOCAL_CLAUDE_SAVED_ASSETS } from '../src/features/pickPlace/claudeAssetLocalTrial';",
        resolveDir: fileURLToPath(new URL('.', import.meta.url)),
      },
      alias: { '@': fileURLToPath(new URL('../src', import.meta.url)) },
      bundle: true,
      write: false,
      format: 'esm',
      minify: true,
      define: { 'import.meta.env.DEV': String(dev), 'import.meta.env.MODE': JSON.stringify(mode) },
    });
    assert.equal(result.outputFiles[0].text.includes('claude_trial_cmu_dock_warehouse'), containsTrial);
  });
}

test('production public-realm renderer excludes local Claude fixture data', async () => {
  const result = await build({
    stdin: {
      contents: "export { publicRealmTrialAsset } from '../src/components/viewer/globe/publicRealmTrial';",
      resolveDir: fileURLToPath(new URL('.', import.meta.url)),
    },
    alias: { '@': fileURLToPath(new URL('../src', import.meta.url)) },
    bundle: true,
    write: false,
    format: 'esm',
    minify: true,
    define: { 'import.meta.env.DEV': 'false', 'import.meta.env.MODE': '"production"' },
  });
  assert.equal(result.outputFiles[0].text.includes('claude_trial_cmu_dock_warehouse'), false);
});
