/// <reference types="vitest" />
import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'path';
import { selectViteEnvDir } from './src/config/viteEnvDir';
import { MODEL_BENCHMARK_ASSETS } from './src/features/dev/modelBenchmarkAssets';

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

function modelBenchmarkAssetsPlugin(): Plugin {
  return {
    name: 'cityprompt-model-benchmark-assets',
    apply: 'serve',
    configureServer(server) {
      const projectRoot = path.resolve(__dirname, '..');
      const commonGitDir = gitCommonDir(projectRoot);

      server.middlewares.use((request, response, next) => {
        const requestPath = request.url
          ? new URL(request.url, 'http://localhost').pathname
          : '';
        const match = requestPath.match(
          /^\/__model-benchmark\/(original|optimized)\/([a-z0-9-]+)\.glb$/,
        );
        if (!match) {
          next();
          return;
        }

        const [, variant, assetId] = match;
        const asset = MODEL_BENCHMARK_ASSETS.find((candidate) => candidate.id === assetId);
        if (!asset || (request.method !== 'GET' && request.method !== 'HEAD')) {
          response.statusCode = asset ? 405 : 404;
          response.end(asset ? 'Method not allowed' : 'Unknown benchmark asset');
          return;
        }

        const sourcePath = variant === 'optimized'
          ? path.join(projectRoot, asset.relativePath)
          : commonGitDir
            ? path.join(
                commonGitDir,
                'lfs',
                'objects',
                asset.original.sha256.slice(0, 2),
                asset.original.sha256.slice(2, 4),
                asset.original.sha256,
              )
            : '';
        if (!sourcePath || !fs.existsSync(sourcePath)) {
          response.statusCode = 404;
          response.setHeader('Content-Type', 'text/plain; charset=utf-8');
          response.end(
            variant === 'original'
              ? 'Original Git LFS object is unavailable. Run: git lfs fetch origin main'
              : 'Optimized seed GLB is unavailable in this worktree.',
          );
          return;
        }

        const stat = fs.statSync(sourcePath);
        response.statusCode = 200;
        response.setHeader('Content-Type', 'model/gltf-binary');
        response.setHeader('Content-Length', stat.size);
        response.setHeader('Cache-Control', 'no-store');
        response.setHeader('X-CityPrompt-Benchmark-Variant', variant);
        if (request.method === 'HEAD') {
          response.end();
          return;
        }
        const stream = fs.createReadStream(sourcePath);
        stream.on('error', (error) => {
          server.config.logger.error(`Benchmark asset read failed: ${error.message}`);
          if (!response.headersSent) response.statusCode = 500;
          response.end();
        });
        stream.pipe(response);
      });
    },
  };
}

export default defineConfig({
  // Worktrees share browser API keys through the repository's ignored Git
  // common directory. VITE_ENV_DIR and a worktree-root .env remain explicit
  // overrides for unusual local or CI setups.
  envDir: resolveEnvDir(),
  plugins: [react(), modelBenchmarkAssetsPlugin()],
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
