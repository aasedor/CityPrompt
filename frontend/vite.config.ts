/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
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
        target: process.env.API_PROXY_TARGET || 'http://localhost:8000',
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
