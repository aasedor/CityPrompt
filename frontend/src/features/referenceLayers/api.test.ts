import { describe, expect, it, vi } from 'vitest';
import { api } from '@/services/api';
import { referenceLayersApi } from './api';

// Match the shared client's default JSON header so Axios's real request
// transformation catches uploads accidentally serialized as JSON.
vi.mock('@/services/api', async () => {
  const axios = (await import('axios')).default;
  return { api: axios.create({ headers: { 'Content-Type': 'application/json' } }) };
});
describe('Reference upload transport', () => {
  it('keeps the actual file and metadata as multipart data after Axios transforms the request', async () => {
    let sent: unknown;
    api.defaults.adapter = async (config) => {
      sent = config.data;
      return { data: { id: 'layer' }, status: 201, statusText: 'Created', headers: {}, config };
    };
    const file = new File(['{"type":"Point","coordinates":[0,0]}'], 'context.geojson', { type: 'application/geo+json' });
    await referenceLayersApi.import('project', file, { name: 'Context', kind: 'reference' });
    expect(sent).toBeInstanceOf(FormData);
    expect((sent as FormData).get('file')).toBe(file);
    expect((sent as FormData).get('name')).toBe('Context');
    expect((sent as FormData).get('kind')).toBe('reference');
  });
});
