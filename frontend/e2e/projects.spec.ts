import type { Page } from '@playwright/test';
import { test, expect } from './fixtures/test';

/**
 * Helper: mock the auth endpoints and set a fake token in localStorage
 * so the ProtectedRoute allows access without a real backend.
 */
async function authenticateUser(page: Page) {
  // Seed localStorage with a fake token before navigating so the auth
  // store treats the user as authenticated.
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'fake-access-token');
    localStorage.setItem('refresh_token', 'fake-refresh-token');
  });

  // Mock the /me endpoint that App.tsx calls on mount when a token exists
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

const MOCK_PROJECTS = [
  {
    id: 'proj-1',
    name: 'Riverside Development',
    description: 'Phase 1 of the riverside residential complex.',
    status: 'draft',
    location: null,
    buildings: [],
    documents: [],
    created_at: '2025-06-01T10:00:00Z',
    updated_at: '2025-06-15T14:30:00Z',
  },
  {
    id: 'proj-2',
    name: 'Downtown Tower',
    description: 'Commercial high-rise project.',
    status: 'ready',
    location: { latitude: 40.7128, longitude: -74.006, address: '123 Main St, New York' },
    buildings: [],
    documents: [],
    created_at: '2025-05-20T08:00:00Z',
    updated_at: '2025-06-10T11:00:00Z',
  },
];

test.describe('Project management', () => {
  test('shows project list page with existing projects', async ({ page }) => {
    await authenticateUser(page);

    await page.route('**/api/v1/projects/**', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(MOCK_PROJECTS),
        });
      }
    });

    await page.goto('/projects');

    // Page heading
    await expect(page.getByRole('heading', { name: 'Projects' })).toBeVisible();

    // Both projects should be listed
    await expect(page.getByText('Riverside Development')).toBeVisible();
    await expect(page.getByText('Downtown Tower')).toBeVisible();

    // The "New Project" button should be visible
    await expect(page.getByRole('button', { name: /New Project/i })).toBeVisible();
  });

  test('create a new project via the form', async ({ page }) => {
    await authenticateUser(page);

    // Initial list is empty
    await page.route('**/api/v1/projects/**', async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes('/projects/proj-new')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      }
    });

    // Mock the create endpoint
    await page.route('**/api/v1/projects/', async (route) => {
      if (route.request().method() === 'POST') {
        const body = route.request().postDataJSON();
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'proj-new',
            name: body.name,
            description: body.description || null,
            status: 'draft',
            location: null,
            buildings: [],
            documents: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }),
        });
      }
    });

    // Mock the project detail page the app navigates to after creation
    await page.route('**/api/v1/projects/proj-new', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'proj-new',
          name: 'My New Project',
          description: 'A brand new project',
          status: 'draft',
          location: null,
          buildings: [],
          documents: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }),
      });
    });

    // Mock activity endpoint
    await page.route('**/api/v1/activity/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/projects');

    // When there are no projects, a "Create Project" button appears in the empty state
    await page.getByRole('button', { name: /Create Project|New Project/i }).first().click();

    // Fill the create form
    await page.getByPlaceholder(/Riverside Development/i).fill('My New Project');
    await page.getByPlaceholder(/Brief description/i).fill('A brand new project');

    // Submit
    await page.getByRole('button', { name: 'Create Project' }).click();

    // After creation, the app navigates to the project detail page
    await expect(page).toHaveURL(/\/projects\/proj-new/);
    await expect(page.getByText('My New Project')).toBeVisible();
  });

  test('navigate to the integrated project workspace', async ({ page }) => {
    await authenticateUser(page);

    await page.route('**/api/v1/projects/**', async (route) => {
      const url = route.request().url();
      if (route.request().method() === 'GET' && url.includes('/projects/proj-1')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ...MOCK_PROJECTS[0],
            buildings: [
              {
                id: 'bldg-1',
                name: 'Tower A',
                height_meters: 45,
                floor_count: 12,
                roof_type: 'flat',
                model_url: null,
                specifications: {},
              },
            ],
          }),
        });
      } else if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(MOCK_PROJECTS),
        });
      }
    });

    await page.route('**/api/v1/activity/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/projects/proj-1');

    await expect(page).toHaveURL(/\/projects\/proj-1$/);
    await expect(page.getByText('Riverside Development', { exact: true })).toBeVisible();
    await expect(page.getByText('Master Plan', { exact: true }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: 'Generate to 3D' })).toBeVisible();
  });

  test('shows integrated 3D generation controls in the project workspace', async ({ page }) => {
    await authenticateUser(page);

    await page.route('**/api/v1/projects/proj-1', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_PROJECTS[0]),
      });
    });

    await page.route('**/api/v1/activity/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.route('**/api/v1/annotations/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/projects/proj-1');

    await expect(page).toHaveURL(/\/projects\/proj-1$/);
    const generate3D = page.getByRole('button', { name: 'Generate to 3D' });
    await expect(generate3D).toBeVisible();
    await expect(generate3D).toBeDisabled();
  });
});
