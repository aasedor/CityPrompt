import { afterEach, expect, it, vi } from 'vitest';
import { createDirect3DCaptureQAPreview, type Direct3DCaptureBundle } from './direct3dCapture';

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

it('decodes captured PNG data locally when the hosted CSP blocks data fetches', async () => {
  const fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
  vi.stubGlobal('fetch', fetch);
  const close = vi.fn();
  const decode = vi.fn().mockResolvedValue({ width: 2048, height: 1024, close });
  vi.stubGlobal('createImageBitmap', decode);
  const drawImage = vi.fn();
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ drawImage } as never);
  vi.spyOn(HTMLCanvasElement.prototype, 'toDataURL').mockReturnValue('data:image/png;base64,cHJldmlldw==');
  const source = 'data:image/png;base64,iVBORw0KGgo=';
  const capture = {
    beautyImageBase64: source, proposalMaskBase64: source,
    classIdImageBase64: source, instanceIdImageBase64: source,
    width: 2048, height: 1024, maskCoverage: 0.02, classCoverage: { landscape: 0.02 },
  } as Direct3DCaptureBundle;

  const preview = await createDirect3DCaptureQAPreview(capture);
  expect(fetch).not.toHaveBeenCalled();
  expect(decode).toHaveBeenCalledTimes(4);
  expect(decode.mock.calls[0][0]).toBeInstanceOf(Blob);
  expect(decode.mock.calls[0][0]).toMatchObject({ size: 8, type: 'image/png' });
  expect(drawImage).toHaveBeenCalledWith(expect.anything(), 0, 0, 320, 160);
  expect(close).toHaveBeenCalledTimes(4);
  expect(preview).toMatchObject({ width: 2048, height: 1024, maskCoverage: 0.02 });
  expect(Object.values(preview.thumbnails)).toHaveLength(4);
});
