import { describe, expect, it, vi } from 'vitest';
import { runImageModelBatch } from './runImageModelBatch';

describe('bounded image comparison', () => {
  it('finishes and saves Flare before starting Sunburst', async () => {
    const events: string[] = [];
    await runImageModelBatch('compare-flare-sunburst', async (model) => {
      events.push(`render ${model}`);
      return model;
    }, async (result) => { events.push(`save ${result}`); });
    expect(events).toEqual([
      'render gpt-image-2.5-flare', 'save gpt-image-2.5-flare',
      'render gpt-image-2.5-sunburst', 'save gpt-image-2.5-sunburst',
    ]);
  });

  it('preserves the first result if the second fails and never retries', async () => {
    const render = vi.fn().mockResolvedValueOnce('first image').mockRejectedValueOnce(new Error('provider unavailable'));
    const save = vi.fn();
    await expect(runImageModelBatch('compare-flare-sunburst', render, save)).rejects.toThrow('provider unavailable');
    expect(save).toHaveBeenCalledExactlyOnceWith('first image', 0);
    expect(render).toHaveBeenCalledTimes(2);
  });

  it('stops before further spending if the first result cannot be saved', async () => {
    const render = vi.fn().mockResolvedValue('first image');
    await expect(runImageModelBatch('compare-flare-sunburst', render, async () => { throw new Error('save failed'); })).rejects.toThrow('save failed');
    expect(render).toHaveBeenCalledTimes(1);
  });

  it('still permits one explicitly chosen engine', async () => {
    const render = vi.fn().mockResolvedValue('legacy');
    await runImageModelBatch('gpt-image-2', render, vi.fn());
    expect(render).toHaveBeenCalledExactlyOnceWith('gpt-image-2');
  });
});
