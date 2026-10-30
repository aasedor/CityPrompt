import { loadEnv } from 'vite';

// Only browser-consumed configuration belongs here. Provider credentials and
// filesystem configuration remain server-side even when a legacy dotenv uses VITE_.
const PUBLIC_ENV_NAMES = [
  'VITE_API_URL',
  'VITE_GOOGLE_MAPS_API_KEY',
  'VITE_MAPBOX_TOKEN',
  'VITE_SENTRY_DSN',
  'VITE_KTX2_TRANSCODER_PATH',
  'VITE_CLAUDE_FIVE_TRIAL',
  'VITE_CONTEXT_PILOT',
  'VITE_ENABLE_CLASSIC_POLYGON_RENDER',
  'VITE_ENABLE_LEGACY_SITE_BOUNDARY_TOOLS',
  'VITE_ENABLE_RENDER_PANEL_COMMUNITY_3D_TOOLS',
  'VITE_PARK_KIT_ASSETS_READY',
];

export function publicEnvironment(mode, envDir) {
  const loaded = loadEnv(mode, envDir, PUBLIC_ENV_NAMES);
  // Vite's prefix filter alone also accepts NAME_PRIVATE_SUFFIX. Select exact
  // names before constructing definitions, including the complete env object.
  const values = Object.fromEntries(PUBLIC_ENV_NAMES.filter(name => Object.hasOwn(loaded, name))
    .map(name => [name, loaded[name]]));
  return {
    values,
    envPrefix: [],
    define: Object.fromEntries(Object.entries(values).map(([name, value]) => [
      `import.meta.env.${name}`, JSON.stringify(value),
    ])),
  };
}
