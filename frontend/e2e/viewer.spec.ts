import type { Page } from '@playwright/test';
import { test, expect, revealPlanningTools } from './fixtures/test';

/**
 * Helper: mock auth endpoints and seed localStorage with a fake token
 * so the ProtectedRoute grants access to the viewer.
 */
async function authenticateUser(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'fake-access-token');
    localStorage.setItem('refresh_token', 'fake-refresh-token');
  });

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'user-1',
        email: 'testuser@example.com',
        full_name: 'Test User',
        role: 'user',
        is_active: true,
        render_credits: 500,
        created_at: new Date().toISOString(),
      }),
    });
  });

  await page.route('**/api/v1/render/projects/**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
  });
  await page.route('**/api/v1/video/projects/**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '{"attempts":[]}' });
  });
  await page.route('**/api/v1/site-zones/projects/**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
  });
}

/**
 * Helper: mock all API endpoints the ViewerPage queries on load.
 */
async function mockViewerAPIs(page: Page) {
  await page.route('**/api/v1/projects/proj-1', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'proj-1',
        name: 'Riverside Development',
        description: 'Phase 1 of the riverside residential complex.',
        status: 'draft',
        location: null,
        buildings: [
          {
            id: 'bldg-1',
            name: 'Tower A',
            height_meters: 45,
            floor_count: 12,
            floor_height_meters: 3.5,
            roof_type: 'flat',
            model_url: null,
            construction_phase: 1,
            specifications: {},
          },
        ],
        documents: [],
        construction_phases: [],
        created_at: '2025-06-01T10:00:00Z',
        updated_at: '2025-06-15T14:30:00Z',
      }),
    });
  });

  await page.route('**/api/v1/annotations/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });

  // The collaboration websocket will fail silently in tests — that is fine.
}

test.describe('Integrated project workspace', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateUser(page);
    await mockViewerAPIs(page);
  });

  test('loads the project in the integrated workspace', async ({ page }) => {
    await page.goto('/projects/proj-1');
    await revealPlanningTools(page);

    await expect(page).toHaveURL(/\/projects\/proj-1$/);
    await expect(page.getByText('Riverside Development', { exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: '2 Design', exact: true })).toHaveAttribute('aria-current', 'step');
    for (const name of ['Buildings', 'Parks', 'Streets', 'Import GLB']) {
      await expect(page.getByRole('button', { name, exact: true })).toBeVisible();
    }
  });

  test('shows the current plan, 3D, image, and video workflow controls', async ({ page }) => {
    await page.goto('/projects/proj-1');
    await revealPlanningTools(page);

    await expect(page.getByText('3D appears automatically', { exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Render this view', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Image', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Video preview · free', exact: true })).toBeVisible();
    // An empty design must explain what is missing before offering capture.
    await expect(page.getByRole('button', { name: 'Image', exact: true })).toBeDisabled();
    await expect(page.getByText('Add a building, park, street, or detail first. A site boundary is optional.')).toBeVisible();
  });

  test('opens the simple GLB uploader and closes it without a file', async ({ page }) => {
    await page.goto('/projects/proj-1');
    await revealPlanningTools(page);

    await page.getByRole('button', { name: 'Import GLB', exact: true }).click();
    const dialog = page.getByRole('dialog', { name: 'Import your building', exact: true });
    await expect(dialog.getByLabel('GLB building file')).toBeVisible();
    await expect(dialog.getByRole('button', { name: 'Upload', exact: true })).toBeDisabled();
    await expect(dialog.getByLabel('Building name (optional)', { exact: true })).toBeHidden();
    await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
    await expect(dialog).toBeHidden();
    await expect(page.getByRole('button', { name: 'Import GLB', exact: true })).toBeVisible();
  });

  test('provides a route back to the project list', async ({ page }) => {
    await page.goto('/projects/proj-1');
    await revealPlanningTools(page);

    const projectsLink = page.locator('a[href="/projects"]').first();
    await expect(projectsLink).toBeVisible();
    await projectsLink.click();
    await expect(page).toHaveURL(/\/projects$/);
  });
});
