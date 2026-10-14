import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

test('the actual flexible-park audit includes every shared equipment model and its exact lock', () => {
  const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
  const temporary = mkdtempSync(join(tmpdir(), 'cityprompt-equipment-audit-'));
  const env = { ...process.env };
  delete env.CITYPROMPT_CATALOGUE_PACKET;
  try {
    const reportPath = join(temporary, 'report.json');
    execFileSync(process.execPath, [join(frontend, 'scripts/check-catalogue-delivery.mjs'),
      '--metadata-only', '--report=' + reportPath], { cwd: frontend, env, timeout: 60000 });
    const report = JSON.parse(readFileSync(reportPath, 'utf8'));
    assert.deepEqual(report.failures, []);
    const manifest = JSON.parse(readFileSync(join(frontend,
      'public/park-kits/shared-park-equipment-v1/kit_manifest.json'), 'utf8'));
    const parks = report.choices.filter(row => row.representation === 'procedural_park_kit');
    assert.ok(parks.length > 0, 'test must exercise actual flexible park choices');
    assert.equal(manifest.assets.length, 5);
    for (const park of parks) for (const asset of manifest.assets) {
      const check = park.checks.find(row => row.url === '/park-kits/shared-park-equipment-v1/' + asset.file);
      assert.ok(check, park.id + ' omitted runtime equipment ' + asset.id);
      assert.equal(check.kind, 'glb');
      assert.match(check.sha256, /^[a-f0-9]{64}$/);
      assert.equal(check.sha256, asset.sha256);
    }
  } finally { rmSync(temporary, { recursive: true, force: true }); }
});


test('production audit explicitly includes reviewed five with exact paths and completed publication gates', () => {
  const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
  const temporary = mkdtempSync(join(tmpdir(), 'cityprompt-trial-audit-'));
  const env = { ...process.env, NODE_ENV:'production', VITE_CLAUDE_FIVE_TRIAL:'true', VITE_ENV_DIR:temporary };
  delete env.CITYPROMPT_CATALOGUE_PACKET;
  try {
    const reportPath=join(temporary,'report.json');
    execFileSync(process.execPath,[join(frontend,'scripts/check-catalogue-delivery.mjs'),'--metadata-only','--report='+reportPath],{cwd:frontend,env,timeout:60000});
    const report=JSON.parse(readFileSync(reportPath,'utf8'));
    const trials=JSON.parse(readFileSync(join(frontend,'../seed/claude-five-trial/library.json'),'utf8')).entries;
    assert.deepEqual(report.failures,[]);
    for(const entry of trials) {
      const choice=report.choices.find(row=>row.variantId===entry.variant_id);
      assert.ok(choice,entry.candidate+' missing from explicit release');
      assert.equal(choice.local_trial_only,false);
      assert.ok(!report.publication_blockers.some(row=>row.id===choice.id));
      const model=choice.checks.find(row=>row.kind==='glb');
      assert.equal(model.sourcePath,'seed/model-library/objects/claude-five/models/'+entry.candidate+'.glb');
      assert.equal(model.sha256,entry.model.sha256);
    }
  } finally { rmSync(temporary,{recursive:true,force:true}); }
});
