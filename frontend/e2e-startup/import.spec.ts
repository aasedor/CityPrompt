import { test, expect } from '@playwright/test';

test('opens Import GLB on the first click while the real globe is preparing', async ({ page }) => {
  const diagnostics = { pageErrors: [] as string[], consoleErrors: [] as string[], requests: [] as string[] };
  const safe = (value: string) => value.replace(/([?&](?:key|token|access_token|file_ticket)=)[^&\s)]+/gi, '$1[redacted]');
  const requestPath = (value: string) => { const url = new URL(value); return url.origin + url.pathname; };
  page.on('pageerror', error => {
    if (diagnostics.pageErrors.length < 30) diagnostics.pageErrors.push(safe(error.stack ?? error.message));
  });
  page.on('console', message => {
    if (message.type() === 'error' && diagnostics.consoleErrors.length < 30) diagnostics.consoleErrors.push(safe(message.text()));
  });
  page.on('requestfailed', request => {
    if (diagnostics.requests.length < 30) diagnostics.requests.push(`${requestPath(request.url())}: ${request.failure()?.errorText}`);
  });
  page.on('response', response => {
    if (response.status() >= 400 && diagnostics.requests.length < 30) diagnostics.requests.push(`${requestPath(response.url())}: HTTP ${response.status()}`);
  });
  let finishTerrain!: () => void;
  const terrain = new Promise<void>(resolve => { finishTerrain = resolve; });
  await page.addInitScript(() => localStorage.setItem('access_token', 'startup-test-token'));
  // Exercise the real loading cover and browser hit testing with local requests only.
  await page.route('**/*', route => new URL(route.request().url()).origin === 'http://127.0.0.1:5186'
    ? route.continue() : route.abort());
  await page.route('**/api/v1/**', async route => {
    const path = new URL(route.request().url()).pathname;
    let body: unknown = [];
    if (path.endsWith('/auth/me')) body = { id: 'student', email: 'student@example.com', role: 'user', is_active: true, render_credits: 0 };
    else if (path === '/api/v1/render/image-models') body = {
      default_model: 'gpt-image-2', credit_balance: 0, credit_exempt: false,
      models: [{ id: 'gpt-image-2', available: false }],
    };
    else if (path === '/api/v1/projects/startup-project') body = {
      id: 'startup-project', name: 'Startup exercise', status: 'draft', buildings: [], documents: [], construction_phases: [],
      location: { latitude: 51.05, longitude: -114.08, address: 'Calgary' },
    };
    else if (path === '/api/v1/site-zones/projects/startup-project/zones') body = [{
      id: '11111111-1111-4111-8111-111111111111', project_id: 'startup-project', name: 'Site', zone_type: 'site_boundary',
      coordinates: [[-114.0801, 51.05], [-114.0799, 51.05], [-114.0799, 51.0502], [-114.0801, 51.0502]],
      area_sqm: 300, properties: {},
    }];
    else if (path.includes('/site-assessments/')) body = null;
    else if (path.includes('/elevation')) {
      await terrain;
      body = path.endsWith('/batch')
        ? { elevations: (route.request().postDataJSON()?.points ?? []).map(() => 1000) }
        : { elevation: 1000, ellipsoidal_height: 975, resolution: 1000 };
    } else if (path.endsWith('/details')) body = { version: 1, revision: 0, can_edit: true, benches: [], trees: [], props: [], surfaces: [] };
    else if (path.includes('/reference-layers/')) body = { layers: [], can_edit: true };
    else if (path.includes('/video/')) body = { attempts: [] };
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
  });

  try {
    await page.goto('/projects/startup-project');
    await expect(page.getByText('Checking terrain height', { exact: true })).toBeVisible({ timeout: 20_000 });
    const button = page.getByRole('button', { name: 'Import GLB', exact: true });
    await expect(button).toBeEnabled();
    expect(await button.evaluate(element => {
      const rect = element.getBoundingClientRect();
      return element.contains(document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2));
    })).toBe(true);
    await button.click({ timeout: 5000 });
    const dialog = page.getByRole('dialog', { name: 'Import your building', exact: true });
    await expect(dialog.getByLabel('GLB building file')).toBeVisible();
    await dialog.getByLabel('GLB building file').setInputFiles({ name: 'test.glb', mimeType: 'model/gltf-binary', buffer: Buffer.from('glTF') });
    await expect(dialog.getByText('test.glb', { exact: true })).toBeVisible();
    await expect(page.getByText('Preparing project view...', { exact: true })).toBeVisible();
    await expect(page.getByText('Checking terrain height', { exact: true })).toBeVisible();
    finishTerrain();
    await expect(page.getByText('Checking terrain height', { exact: true })).toBeHidden();
    await expect(dialog.getByText('test.glb', { exact: true })).toBeVisible();
    await expect(dialog.getByRole('button', { name: 'Upload', exact: true })).toBeEnabled();
  } catch (error) {
    const body = await page.locator('body').innerText({ timeout: 1000 }).catch(() => '[body unavailable]');
    const evidence = { ...diagnostics, url: requestPath(page.url()), body: safe(body.slice(0, 12000)) };
    console.error('Startup failure diagnostics:', JSON.stringify(evidence));
    await test.info().attach('startup-diagnostics', { body: Buffer.from(JSON.stringify(evidence, null, 2)), contentType: 'application/json' }).catch(() => {});
    await page.screenshot({ timeout: 2000 }).then(body => test.info().attach('startup-screen', { body, contentType: 'image/png' })).catch(() => {});
    throw error;
  } finally {
    finishTerrain();
  }
});
