/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'path';
import { selectViteEnvDir } from './src/config/viteEnvDir';

function gitCommonDir(projectRoot: string): string | null {
  const dotGit = path.join(projectRoot, '.git');
  try {
    if (fs.statSync(dotGit).isDirectory()) return dotGit;
  } catch {
    // A linked worktree has a .git pointer file rather than a directory.
  }

  try {
    const pointer = fs.readFileSync(dotGit, 'utf8').trim();
    if (!pointer.toLowerCase().startsWith('gitdir:')) return null;
    // Slice once so a Windows drive colon inside the absolute gitdir path is
    // preserved (String.split(':', 2) would truncate it to just "C").
    const rawAdminDir = pointer.slice(pointer.indexOf(':') + 1).trim();
    const adminDir = path.resolve(projectRoot, rawAdminDir);
    const commonFile = path.join(adminDir, 'commondir');
    if (!fs.existsSync(commonFile)) return adminDir;
    return path.resolve(adminDir, fs.readFileSync(commonFile, 'utf8').trim());
  } catch {
    return null;
  }
}

function hasEnvAssignments(filePath: string): boolean {
  try {
    return fs.readFileSync(filePath, 'utf8')
      .split(/\r?\n/)
      .some((line) => /^\s*[A-Za-z_][A-Za-z0-9_]*\s*=/.test(line));
  } catch {
    return false;
  }
}

function resolveEnvDir(): string {
  const explicitEnvDir = process.env.VITE_ENV_DIR
    ? path.resolve(process.env.VITE_ENV_DIR)
    : undefined;
  const projectRoot = path.resolve(__dirname, '..');
  const projectEnv = path.join(projectRoot, '.env');
  // An interrupted recovery can leave an empty placeholder .env at the
  // worktree root. Existence alone must not shadow the repository's shared,
  // ignored key store and boot Vite without Maps/API credentials.
  const sharedGitDir = gitCommonDir(projectRoot);
  return selectViteEnvDir({
    explicitEnvDir,
    projectRoot,
    projectEnvExists: fs.existsSync(projectEnv),
    projectEnvHasAssignments: hasEnvAssignments(projectEnv),
    sharedGitDir,
    sharedEnvExists: Boolean(
      sharedGitDir && fs.existsSync(path.join(sharedGitDir, '.env')),
    ),
    fallbackEnvDir: __dirname,
  });
}

export default defineConfig({
  // Isolated source worktrees can reuse the large, already hydrated asset
  // directory without duplicating it or changing production asset URLs.
  publicDir: process.env.CITYPROMPT_PUBLIC_DIR || 'public',
  // Worktrees share browser API keys through the repository's ignored Git
  // common directory. VITE_ENV_DIR and a worktree-root .env remain explicit
  // overrides for unusual local or CI setups.
  envDir: resolveEnvDir(),
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5174,
    watch: {
      usePolling: true,
      interval: 1000,
      // Public assets are served verbatim and never need HMR. Polling the
      // hydrated catalogue (more than 25,000 files locally) every second makes
      // Windows/OneDrive development needlessly expensive and can hold file
      // handles during branch switches.
      ignored: ['**/public/**'],
    },
    proxy: {
      '/api': {
        // Use the explicit IPv4 loopback in local development. On Windows with
        // Docker + WSL, `localhost` can resolve to an orphaned IPv6 wslrelay
        // listener and leave otherwise healthy API requests hanging.
        target: process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Keep the route graph available to the bundle budget check. Render does
    // not serve this file to application code, and the file is only a few KB.
    manifest: true,
    // Performance budget: warn if any chunk exceeds 500KB
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        onlyExplicitManualChunks: true,
        // Assign packages by their own module id. Rollup's object form also
        // absorbs dependencies of each entry, which pulled React into the
        // react-three chunk and made every page download the 3D runtime.
        manualChunks(id) {
          const normalizedId = id.replace(/\\/g, '/');
          if (normalizedId.includes('/node_modules/@react-three/')) return 'react-three';
          if (
            normalizedId.includes('/node_modules/three/')
            || normalizedId.includes('/node_modules/three-stdlib/')
          ) return 'three';
          if (normalizedId.includes('/node_modules/mapbox-gl/')) return 'mapbox';
          return undefined;
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    css: false,
  },
});
