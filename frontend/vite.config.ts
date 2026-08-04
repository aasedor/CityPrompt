/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'path';

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

function resolveEnvDir(): string {
  if (process.env.VITE_ENV_DIR) return path.resolve(process.env.VITE_ENV_DIR);

  const projectRoot = path.resolve(__dirname, '..');
  if (fs.existsSync(path.join(projectRoot, '.env'))) return projectRoot;

  const sharedGitDir = gitCommonDir(projectRoot);
  if (sharedGitDir && fs.existsSync(path.join(sharedGitDir, '.env'))) {
    return sharedGitDir;
  }

  return __dirname;
}

export default defineConfig({
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
