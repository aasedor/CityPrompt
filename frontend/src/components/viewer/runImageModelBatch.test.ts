import { describe, expect, it, vi } from 'vitest';
import { runImageModelBatch } from './runImageModelBatch';

describe('bounded image comparison', () => {
  it('renders and saves all three models in order', async () => {
    const events: string[] = [];
    await runImageModelBatch('compare-all-three', async (model) => {
      events.push(`render ${model}`);
      return model;
    }, async (result) => { events.push(`save ${result}`); });
    expect(events).toEqual([
      'render gpt-image-2', 'save gpt-image-2',
      'render gpt-image-2.5-flare', 'save gpt-image-2.5-flare',
      'render gpt-image-2.5-sunburst', 'save gpt-image-2.5-sunburst',
    ]);
  });

  it('preserves the first result if the second fails and never retries', async () => {
    const render = vi.fn().mockResolvedValueOnce('first image').mockRejectedValueOnce(new Error('provider unavailable'));
    const save = vi.fn();
    await expect(runImageModelBatch('compare-all-three', render, save)).rejects.toThrow('provider unavailable');
    expect(save).toHaveBeenCalledExactlyOnceWith('first image', 0);
    expect(render).toHaveBeenCalledTimes(2);
  });

  it('stops before further spending if the first result cannot be saved', async () => {
    const render = vi.fn().mockResolvedValue('first image');
    await expect(runImageModelBatch('compare-all-three', render, async () => { throw new Error('save failed'); })).rejects.toThrow('save failed');
    expect(render).toHaveBeenCalledTimes(1);
  });

  it('keeps two saved images when Sunburst fails without retrying any model', async () => {
    const render = vi.fn().mockResolvedValueOnce('image 2').mockResolvedValueOnce('flare')
      .mockRejectedValueOnce(new Error('Sunburst unavailable'));
    const save = vi.fn();
    await expect(runImageModelBatch('compare-all-three', render, save)).rejects.toThrow('Sunburst unavailable');
    expect(render.mock.calls.map(([model]) => model)).toEqual([
      'gpt-image-2', 'gpt-image-2.5-flare', 'gpt-image-2.5-sunburst',
    ]);
    expect(save.mock.calls).toEqual([['image 2', 0], ['flare', 1]]);
  });

  it('still permits one explicitly chosen engine', async () => {
    const render = vi.fn().mockResolvedValue('legacy');
    await runImageModelBatch('gpt-image-2', render, vi.fn());
    expect(render).toHaveBeenCalledExactlyOnceWith('gpt-image-2');
  });
});
