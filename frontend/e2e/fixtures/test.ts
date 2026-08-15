import { test as base, expect } from '@playwright/test';

type CityPromptFixtures = {
  browserErrors: string[];
  deterministicApiMocks: void;
};

export const test = base.extend<CityPromptFixtures>({
  deterministicApiMocks: [async ({ page }, use) => {
    // Workspace tests intentionally run without the backend. Keep terrain
    // startup deterministic instead of allowing Vite's proxy to return 500.
    await page.route('**/api/v1/elevation?*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          elevation: 0,
          ellipsoidal_height: -25,
          resolution: 1000,
        }),
      });
    });
    await page.route('**/api/v1/elevation/batch', async (route) => {
      const body = route.request().postDataJSON() as { points?: unknown[] } | null;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ elevations: body?.points?.map(() => -25) ?? [] }),
      });
    });
    await page.route('**/api/v1/projects/?*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: '[]',
      });
    });

    await use();
  }, { auto: true }],
  browserErrors: [async ({ page }, use) => {
    const browserErrors: string[] = [];
    page.on('console', (message) => {
      if (message.type() !== 'error') return;
      if (message.text().startsWith('Failed to load resource: the server responded with a status of')) return;
      browserErrors.push(`console: ${message.text()}`);
    });
    page.on('pageerror', (error) => browserErrors.push(`page: ${error.message}`));
    page.on('response', (response) => {
      if (response.status() < 400) return;
      const expectedInvalidLogin = response.status() === 401
        && response.url().endsWith('/api/v1/auth/login');
      if (!expectedInvalidLogin) {
        browserErrors.push(`http ${response.status()}: ${response.url()}`);
      }
    });

    await use(browserErrors);

    expect(browserErrors, 'unexpected browser errors').toEqual([]);
  }, { auto: true }],
});

export { expect };
