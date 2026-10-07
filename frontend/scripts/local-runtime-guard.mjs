import { existsSync, readFileSync } from 'node:fs';
import { isAbsolute, join } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const run = promisify(execFile);

/** A worktree's ignored runtime profile keeps its environment and assets together. */
export function applyLocalRuntimeProfile(repositoryRoot, env = process.env) {
  const file = join(repositoryRoot, 'artifacts', 'local-runtime.json');
  if (!existsSync(file)) return null;
  const profile = JSON.parse(readFileSync(file, 'utf8'));
  if (profile.schema !== 'cityprompt.local-runtime@1') throw new Error('Invalid local runtime profile: ' + file);
  for (const [field, variable] of Object.entries({
    envDir: 'VITE_ENV_DIR', cataloguePacket: 'CITYPROMPT_CATALOGUE_PACKET', publicDir: 'CITYPROMPT_PUBLIC_DIR',
  })) {
    if (profile[field] === undefined) continue;
    if (typeof profile[field] !== 'string' || !isAbsolute(profile[field]) || !existsSync(profile[field])) {
      throw new Error('Local runtime profile needs an existing absolute ' + field + ' path.');
    }
    env[variable] ||= profile[field];
  }
  if (profile.apiProxyTarget) {
    const url = new URL(profile.apiProxyTarget);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) throw new Error('Invalid local API proxy URL.');
    env.API_PROXY_TARGET ||= profile.apiProxyTarget;
  }
  if (profile.port !== undefined && (!Number.isInteger(profile.port) || profile.port < 1 || profile.port > 65535)) {
    throw new Error('Invalid local frontend port.');
  }
  return profile;
}

export async function verifyLocalRuntime(env, audit) {
  if (!env.VITE_GOOGLE_MAPS_API_KEY?.trim()) {
    throw new Error('City Prompt cannot start: VITE_GOOGLE_MAPS_API_KEY is missing. Restore the browser-key environment in artifacts/local-runtime.json (envDir) or VITE_ENV_DIR. Key values are never printed.');
  }
  await audit();
}

/** Runs for direct Vite launches too; npm lifecycle hooks can be bypassed. */
export function localRuntimeGuard() {
  return {
    name: 'cityprompt-local-runtime-guard',
    apply: 'serve',
    async configureServer(server) {
      // The catalogue audit loads modules through Vite without serving an app.
      if (server.config.server.middlewareMode || server.config.mode === 'test') return;
      await verifyLocalRuntime(server.config.env, async () => {
        try {
          const { stdout } = await run(process.execPath, [join(server.config.root, 'scripts/check-catalogue-delivery.mjs')], {
            cwd: server.config.root, env: process.env, timeout: 120000, maxBuffer: 1024 * 1024,
          });
          server.config.logger.info(stdout.trim());
        } catch (error) {
          throw new Error('City Prompt catalogue startup check failed. Restore the matching catalogue packet before serving the app.\n' + (error.stderr || error.stdout || error.message));
        }
      });
    },
  };
}
