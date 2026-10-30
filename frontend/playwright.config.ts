import { defineConfig, devices } from '@playwright/test';

/** Offline auth/project UI checks; actual Google 3D needs a separate keyed trial. */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 1,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  timeout: 30_000,
  use: {
    baseURL: 'http://127.0.0.1:5173',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    // Tests mock backend APIs and exercise the provider-free map fallback.
    // Explicit test mode keeps real developer/provider credentials out of CI;
    // normal dev/build/preview continue to use their existing startup guards.
    command: 'npm run dev -- --mode test --host 127.0.0.1 --port 5173',
    env: { VITE_GOOGLE_MAPS_API_KEY: '', VITE_MAPBOX_TOKEN: '' },
    url: 'http://127.0.0.1:5173',
    timeout: 180_000,
    reuseExistingServer: !process.env.CI,
  },
});
