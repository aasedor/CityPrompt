import { afterEach, beforeEach, vi } from 'vitest';
const fixtures = import.meta.glob(['./data/*UrbanForm.json','./data/*LandUseConcept.json'], { eager:true, import:'default' });

/** Serve the actual reviewed JSON in tests, through the same fetch boundary. */
export function installPolicyMapFetch() {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async (url: URL) => {
      const name = url.pathname.split('/').pop()!;
      if (!fixtures[`./data/${name}`]) {
        throw new Error(`Unexpected test request: ${name}`);
      }
      return new Response(JSON.stringify(fixtures[`./data/${name}`]), { status: 200 });
    }));
  });
  afterEach(() => vi.unstubAllGlobals());
}
