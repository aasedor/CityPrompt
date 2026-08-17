import { test, expect } from './fixtures/test';


const LIVE_STACK = process.env.CITYPROMPT_LIVE_E2E === '1';


test.describe('Live Japanese Machiya delivery', () => {
  test.skip(!LIVE_STACK, 'set CITYPROMPT_LIVE_E2E=1 after starting and seeding the local stack');

  test('persists a retail polygon and places the grounded restored family', async ({ page, request }) => {
    test.setTimeout(120_000);
    const nonce = `${Date.now()}-${process.pid}`;
    const email = `codex-live-machiya-${nonce}@example.com`;
    const password = 'CityPrompt-Live-QA-2026!';

    const register = await request.post('/api/v1/auth/register', {
      data: { email, password, full_name: 'Codex Live Machiya QA' },
    });
    expect(register.status()).toBe(201);

    const login = await request.post('/api/v1/auth/login', {
      data: { email, password },
    });
    expect(login.ok()).toBe(true);
    const { access_token: accessToken } = await login.json() as { access_token: string };
    const headers = { Authorization: `Bearer ${accessToken}` };

    const createProject = await request.post('/api/v1/projects/', {
      headers,
      data: {
        name: `Live Machiya QA ${nonce}`,
        description: 'Disposable full-stack grounding acceptance test.',
      },
    });
    expect(createProject.status()).toBe(201);
    const project = await createProject.json() as { id: string };
    await expect.poll(
      async () => (await request.get(`/api/v1/projects/${project.id}`, { headers })).status(),
      { timeout: 15_000 },
    ).toBe(200);

    const createZone = await request.post(`/api/v1/site-zones/projects/${project.id}/zones`, {
      headers,
      data: {
        name: 'Retail - Japanese Machiya Traditional Restored',
        zone_type: 'building',
        coordinates: [
          [-114.071000, 51.044000],
          [-114.070720, 51.044000],
          [-114.070720, 51.044126],
          [-114.071000, 51.044126],
          [-114.071000, 51.044000],
        ],
        color: '#cf4017',
        sort_order: 1,
        properties: {
          development_type: 'commercial_retail',
          development_aesthetic: 'japanese_contemporary',
          development_subcategory: 'japanese_machiya_mixed_use',
          development_archetype_id: 'machiya_traditional_restored',
          development_archetype_label: 'Japanese Machiya - Traditional Restored',
          development_selected_variant_id: 'machiya_traditional_restored',
          floors: 2,
          height: 11.57,
          floor_height: 3.35,
        },
      },
    });
    expect(createZone.status()).toBe(201);
    const zone = await createZone.json() as { id: string };

    const modulesResponse = await request.get('/api/v1/lego-assembly/modules', { headers });
    expect(modulesResponse.ok()).toBe(true);
    const moduleInventory = await modulesResponse.json() as {
      modules: Array<{ family: string; role: string }>;
    };
    expect(moduleInventory.modules.some((module) => (
      module.family === 'restored-kyoto-machiya' && module.role === 'assembled'
    ))).toBe(true);

    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await expect(page).toHaveURL(/\/projects$/);

    await page.goto(`/projects/${project.id}`);
    const generate = page.getByRole('button', { name: 'Generate to 3D', exact: true });
    await expect(generate).toBeEnabled();
    await generate.click();

    const builder = page.getByRole('complementary');
    await expect(builder.getByText('restored-kyoto-machiya', { exact: false })).toBeVisible({ timeout: 45_000 });
    await expect(builder.getByText('form preserved', { exact: true })).toBeVisible({ timeout: 45_000 });
    await expect(builder.getByText('placed', { exact: true })).toBeVisible({ timeout: 90_000 });
    await expect(builder.getByText(/Built 1 detailed building, 0 correct-size massing fallbacks/)).toBeVisible();

    const persistedProjectResponse = await request.get(`/api/v1/projects/${project.id}`, { headers });
    expect(persistedProjectResponse.ok()).toBe(true);
    const persistedProject = await persistedProjectResponse.json() as {
      buildings: Array<{ id: string }>;
    };
    expect(persistedProject.buildings).toHaveLength(1);

    const recipeResponse = await request.get(
      `/api/v1/lego-assembly/recipes/${persistedProject.buildings[0].id}`,
      { headers },
    );
    expect(recipeResponse.ok()).toBe(true);
    const { legoAssembly } = await recipeResponse.json() as {
      legoAssembly: {
        module_family: string;
        archetype_id: string;
        assembled_height_m: number;
        instances: Array<{
          role: string;
          position: [number, number, number];
          native_dimensions_m: [number, number, number];
          model_url: string;
        }>;
      };
    };
    expect(legoAssembly.module_family).toBe('restored-kyoto-machiya');
    expect(legoAssembly.archetype_id).toBe('machiya_traditional_restored');
    expect(legoAssembly.assembled_height_m).toBeCloseTo(11.57, 2);
    expect(legoAssembly.instances).toHaveLength(1);
    expect(legoAssembly.instances[0].role).toBe('assembled');
    expect(legoAssembly.instances[0].position[1]).toBe(0);
    expect(legoAssembly.instances[0].native_dimensions_m).toEqual([19.77, 16.77, 11.57]);

    const persistedZoneResponse = await request.get(
      `/api/v1/site-zones/projects/${project.id}/zones`,
      { headers },
    );
    expect(persistedZoneResponse.ok()).toBe(true);
    const persistedZones = await persistedZoneResponse.json() as Array<{
      id: string;
      properties?: { community_3d?: { generator?: string } };
    }>;
    expect(persistedZones.find((item) => item.id === zone.id)?.properties?.community_3d?.generator)
      .toBe('lego_assembly');

    const modelResponse = await request.get(legoAssembly.instances[0].model_url);
    expect(modelResponse.ok()).toBe(true);
    const model = await modelResponse.body();
    expect(model.byteLength).toBe(43_953_548);
    expect(model.subarray(0, 4).toString('ascii')).toBe('glTF');
  });
});
