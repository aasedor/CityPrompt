import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e-startup',
  workers: 1,
  retries: 0,
  timeout: 30_000,
  use: { baseURL: 'http://127.0.0.1:5186', ...devices['Desktop Chrome'] },
  webServer: {
    command: 'npm run dev -- --mode test --host 127.0.0.1 --port 5186',
    env: { VITE_GOOGLE_MAPS_API_KEY: 'startup-regression-key', VITE_MAPBOX_TOKEN: '' },
    url: 'http://127.0.0.1:5186',
    timeout: 180_000,
  },
});
