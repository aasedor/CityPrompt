const registryPath = 'src/data/publicRealmRelease20261023.json';
const sha = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const fail = detail => { throw new Error(`Invalid production fixed public-realm registry: ${detail}`); };

// Keep the URL scanner aligned with this release's production and saved-scene
// gates. Disabled rows remain in source as immutable provenance, not dependencies.
function approvedIdentity(row) {
  const { asset, fixture, visual_review: visual, runtime_review: runtime } = row;
  const prefix = `/${row.category === 'park' ? 'park' : 'street'}-kits/claude-20261023/`;
  const properties = asset?.properties;
  const variant = row.category === 'park' ? properties?.green_space_selected_variant_id : properties?.road_selected_variant_id;
  return [row.source_sha256, row.review_sha256, row.runtime_sha256, row.thumbnail_sha256].every(sha)
    && ['park', 'street'].includes(row.category)
    && typeof asset?.id === 'string' && asset.id.startsWith('claude_public_realm:')
    && asset.id.endsWith(`:${row.runtime_sha256.slice(0, 12)}`)
    && asset.kind === 'object' && asset.reshapeMode === 'fixed_native'
    && asset.zoneType === (row.category === 'park' ? 'green_space' : 'road')
    && asset.model?.method === 'fixed_public_realm_v1' && asset.model.revision === row.runtime_sha256
    && typeof asset.model.variantId === 'string' && variant === asset.model.variantId
    && properties?.public_realm_release_asset === asset.id && properties.native_public_realm_url === fixture?.url
    && properties.validation_fixed_fixture == null && properties.validation_native_url == null && properties.public_realm_trial_asset == null
    && fixture?.id === asset.id && fixture.sha256 === row.runtime_sha256 && fixture.kind === row.category
    && fixture.url === `${prefix}${row.runtime_sha256}.glb`
    && [`${prefix}${row.thumbnail_sha256}.jpg`, `${prefix}${row.thumbnail_sha256}.png`].includes(asset.thumbnail)
    && Array.isArray(fixture.dimensions) && fixture.dimensions.length === 2
    && fixture.dimensions[0] === asset.width && fixture.dimensions[1] === asset.depth
    && asset.minWidth === asset.width && asset.minDepth === asset.depth && asset.maxWidth === asset.width && asset.maxDepth === asset.depth
    && Array.isArray(asset.nativeDimensions) && asset.nativeDimensions.length === 3
    && [asset.width, asset.depth, ...asset.nativeDimensions].every(value => Number.isFinite(value) && value > 0)
    && asset.nativeDimensions[0] <= asset.width && asset.nativeDimensions[1] <= asset.depth
    && fixture.preserveNativeGround === true && fixture.centerNativeClay === true
    && visual?.status === 'passed' && visual.scope === 'complete_runtime_derivative'
    && visual.runtime_sha256 === row.runtime_sha256 && sha(visual.evidence_sha256)
    && visual.unresolved_p0 === 0 && visual.unresolved_p1 === 0
    && runtime?.status === 'passed' && runtime.runtime_sha256 === row.runtime_sha256 && sha(runtime.evidence_sha256);
}

export function productionRuntimeSourceText(path, text) {
  if (path.replaceAll('\\', '/') !== registryPath) return text;
  const manifest = JSON.parse(text);
  if (manifest?.schema !== 'cityprompt.fixed-public-realm-release@1' || manifest.release_id !== 'claude-20261023'
    || !Array.isArray(manifest.models)) fail('unsupported schema or model list');
  const selected = [];
  const ids = new Set();
  for (const row of manifest.models) {
    if (!row || !['ready', 'retired', 'prepared', 'runtime_trial'].includes(row.status)) fail('unsupported model status');
    if (row.status !== 'ready' && row.status !== 'retired') continue;
    if (!approvedIdentity(row) || ids.has(row.asset.id)) fail(`approval or identity mismatch for ${row.candidate ?? 'unknown candidate'}`);
    ids.add(row.asset.id);
    selected.push(row);
  }
  return JSON.stringify({ ...manifest, models: selected });
}
