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
      // Do NOT watch the generated archetype/entourage image dirs. The polling
      // watcher repeatedly accesses these 1000+ binaries every second, which on
      // Windows collides with `git stash` / branch-switch file deletions and
      // causes "failed to remove" lock failures (see CLAUDE.md). These are static
      // generated assets that don't need HMR, so ignoring them is free.
      ignored: [
        '**/public/archetypes/**',
        '**/public/entourage/**',
      ],
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
    // Performance budget: warn if any chunk exceeds 500KB
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
          'react-three': ['@react-three/fiber', '@react-three/drei'],
          mapbox: ['mapbox-gl'],
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
