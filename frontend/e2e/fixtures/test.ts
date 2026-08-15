import { test as base, expect } from '@playwright/test';

export const test = base.extend<{ browserErrors: string[] }>({
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
