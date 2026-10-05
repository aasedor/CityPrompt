import { afterEach, beforeEach, vi } from 'vitest';
const fixtures = import.meta.glob('./data/*UrbanForm.json', { eager:true, import:'default' });

/** Serve the actual reviewed JSON in tests, through the same fetch boundary. */
export function installPolicyMapFetch() {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async (url: URL) => {
      const name = url.pathname.split('/').pop()!;
      if (!/^(riley|chinook|east-calgary|heritage|north-hill|south-shaganappi|westbrook|west-elbow)UrbanForm\.json$/.test(name)) {
        throw new Error(`Unexpected test request: ${name}`);
      }
      return new Response(JSON.stringify(fixtures[`./data/${name}`]), { status: 200 });
    }));
  });
  afterEach(() => vi.unstubAllGlobals());
}
